from __future__ import annotations
from ._loader import ROOT, OUTPUT, load_lesson

import copy, json, math, re, time, tempfile, os, sys
from dataclasses import dataclass
from pathlib import Path
from urllib.request import Request, build_opener, ProxyHandler
os.environ["PYTHONIOENCODING"] = "utf-8"

def schema(name, description, fields):
    return {"type": "function", "function": {
        "name": name, "description": description,
        "parameters": {"type": "object", "properties": fields,
                       "required": list(fields), "additionalProperties": False}}}

def validate(arguments, spec):
    """Deliberately small JSON Schema subset; not a general validator."""
    fields = spec["function"]["parameters"]["properties"]
    if not isinstance(arguments, dict) or set(arguments) != set(fields):
        raise ValueError("argument keys do not match schema")
    for key, rule in fields.items():
        value = arguments[key]
        if rule["type"] == "string" and (not isinstance(value, str) or not 0 < len(value) <= 500):
            raise ValueError(key + " must be a nonempty string, <=500 characters")
        if rule["type"] == "number" and (type(value) not in (int, float) or not math.isfinite(value) or abs(value) > 1e9):
            raise ValueError(key + " must be a finite number, abs <=1e9")
        if "enum" in rule and value not in rule["enum"]:
            raise ValueError(key + " is outside enum")

@dataclass
class Tool:
    spec: dict
    function: object
    needs_approval: bool = False
    repeatable: bool = False

def calculator(a, b, operation):
    if operation == "add":
        return a + b
    if operation == "multiply":
        return a * b
    raise ValueError("unknown operation")

def calculator_tool():
    return Tool(schema("calculator", "两数相加或相乘", {
        "a": {"type": "number"}, "b": {"type": "number"},
        "operation": {"type": "string", "enum": ["add", "multiply"]}}), calculator)

def call(name, **arguments):
    return {"role": "assistant", "content": "", "tool_calls": [
        {"function": {"name": name, "arguments": arguments}}]}

def final(text):
    return {"role": "assistant", "content": text}

class ReplayModel:
    """Replay authored outputs so learners can inspect control flow offline."""
    def __init__(self, outputs):
        self.outputs = iter(copy.deepcopy(outputs))
        self.requests = []
        self.tokens = 0

    def __call__(self, messages, tools, timeout):
        self.requests.append(copy.deepcopy(messages))
        return next(self.outputs)

def minimal_loop(question, model, max_steps=4, max_tools=4, timeout=5):
    messages = [{"role": "user", "content": question}]
    tools = {"calculator": calculator_tool()}
    deadline, used = time.monotonic() + timeout, 0
    for step in range(max_steps):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return "timeout", messages
        try:
            reply = model(messages, [t.spec for t in tools.values()], remaining)
        except Exception as error:
            return "model_error:" + type(error).__name__, messages
        messages.append(reply)
        if time.monotonic() >= deadline:
            return "timeout", messages
        if not reply.get("tool_calls"):
            return reply.get("content", ""), messages
        for requested in reply["tool_calls"]:
            if used >= max_tools:
                return "tool_limit", messages
            used += 1
            name = "invalid"
            try:
                name = requested["function"]["name"]
                args = requested["function"]["arguments"]
                validate(args, tools[name].spec)
                result = {"ok": True, "data": tools[name].function(**args)}
            except Exception as error:
                result = {"ok": False, "error": type(error).__name__}
            messages.append({"role": "tool", "tool_name": name,
                             "content": json.dumps(result)})
    return "step_limit", messages

def normalize_tool_message(message, tools):
    """Some small models emit an explicit JSON action in content; parse that action only."""
    message = copy.deepcopy(message)
    if not message.get("tool_calls") and tools:
        try:
            action = json.loads(message.get("content", ""))
            names = {t["function"]["name"] for t in tools}
            if (isinstance(action, dict) and set(action) == {"name", "arguments"} and
                    action["name"] in names and isinstance(action["arguments"], dict)):
                message["tool_calls"] = [{"function": action}]
                message["content"] = ""
        except (ValueError, TypeError):
            pass
    return message

class OllamaModel:
    """Real /api/chat adapter, fixed local endpoint, bounded HTTP timeout."""
    def __init__(self, model="qwen3:1.7b", *, max_output_tokens=512, think=False):
        self.model = model
        self.tokens = 0
        self.max_output_tokens = max_output_tokens
        self.think = think
        self.requests = []
        self.input_tokens = self.output_tokens = 0

    def __call__(self, messages, tools, timeout):
        payload = {"model": self.model, "messages": messages,
                   "tools": tools, "stream": False, "think": self.think,
                   "options": {"temperature": 0, "num_predict": self.max_output_tokens,
                               "num_ctx": 8192}}
        body = json.dumps(payload).encode()
        request = Request("http://127.0.0.1:11434/api/chat", body,
                          {"Content-Type": "application/json"})
        with build_opener(ProxyHandler({})).open(request, timeout=timeout) as response:
            result = json.load(response)
        incoming, outgoing = result.get("prompt_eval_count", 0), result.get("eval_count", 0)
        self.input_tokens += incoming
        self.output_tokens += outgoing
        self.tokens += incoming + outgoing
        self.requests.append({"request": copy.deepcopy(payload), "response": result})
        normalized = normalize_tool_message(result["message"], tools)
        self.requests[-1]["message_normalized"] = normalized != result["message"]
        return normalized

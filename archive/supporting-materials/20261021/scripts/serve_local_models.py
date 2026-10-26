"""CPU-only teaching adapter. Implements a small Ollama-shaped API, not Ollama.

Generated decisions come from Qwen3; embeddings come from MiniLM. No replay,
remote paid API, shell tool or GPU allocation is involved.
"""
import argparse
import hashlib
import json
import re
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import torch
import transformers
from transformers import AutoModel, AutoModelForCausalLM, AutoTokenizer

ROOT = Path(__file__).resolve().parents[1]
MODEL = "qwen3:0.6b-cpu"
EMBED = "all-minilm:l6-v2-cpu"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=11434)
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--manifest", type=Path, default=ROOT / "outputs/local-model-paths.json")
    args = parser.parse_args()
    paths = json.loads(args.manifest.read_text())
    torch.set_num_threads(args.threads)
    torch.set_num_interop_threads(1)
    tokenizer = AutoTokenizer.from_pretrained(paths["Qwen/Qwen3-0.6B"], local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(paths["Qwen/Qwen3-0.6B"], dtype=torch.float32,
                                               local_files_only=True).to("cpu").eval()
    embed_tokenizer = AutoTokenizer.from_pretrained(paths["sentence-transformers/all-MiniLM-L6-v2"], local_files_only=True)
    embed_model = AutoModel.from_pretrained(paths["sentence-transformers/all-MiniLM-L6-v2"],
                                            local_files_only=True).to("cpu").eval()
    digest = hashlib.sha256((Path(paths["Qwen/Qwen3-0.6B"]) / "config.json").read_bytes()).hexdigest()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *unused):
            pass

        def reply(self, value, status=200):
            data = json.dumps(value, ensure_ascii=False).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            if self.path == "/api/tags":
                return self.reply({"models": [{"name": MODEL, "model": MODEL, "digest": digest,
                    "details": {"family": "qwen3", "parameter_size": "0.6B", "quantization_level": "F32"}},
                    {"name": EMBED, "model": EMBED, "digest": hashlib.sha256((Path(paths["sentence-transformers/all-MiniLM-L6-v2"]) / "config.json").read_bytes()).hexdigest(),
                     "details": {"family": "MiniLM", "embedding_dimensions": 384}}],
                    "adapter": "Transformers CPU teaching adapter; not an Ollama installation"})
            if self.path == "/api/version":
                return self.reply({"version": "transformers-" + transformers.__version__ + "-cpu-teaching-adapter"})
            return self.reply({"error": "unknown route"}, 404)

        def do_POST(self):
            try:
                body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))
                if self.path == "/api/show":
                    return self.reply({"model_info": {"general.architecture": "qwen3", "general.parameter_count": model.num_parameters()},
                                       "details": {"family": "qwen3", "parameter_size": "0.6B", "quantization_level": "F32"}})
                if self.path == "/api/embed":
                    if body.get("model") != EMBED:
                        return self.reply({"error": "embedding model must be " + EMBED}, 404)
                    texts = body["input"]
                    if isinstance(texts, str):
                        texts = [texts]
                    encoded = embed_tokenizer(texts, padding=True, truncation=True, max_length=256, return_tensors="pt")
                    with torch.inference_mode():
                        values = embed_model(**encoded).last_hidden_state
                        mask = encoded["attention_mask"].unsqueeze(-1)
                        means = (values * mask).sum(1) / mask.sum(1).clamp(min=1)
                        vectors = torch.nn.functional.normalize(means, p=2, dim=1)
                    return self.reply({"model": EMBED, "embeddings": vectors.tolist()})
                if self.path != "/api/chat":
                    return self.reply({"error": "unknown route"}, 404)
                if body.get("model") != MODEL:
                    return self.reply({"error": "generation model must be " + MODEL}, 404)
                messages = body["messages"]
                if body.get("format") == "json":
                    messages = [{"role": "system", "content": "Return one valid JSON object, no markdown."}] + messages
                prompt = tokenizer.apply_chat_template(messages, tools=body.get("tools"), tokenize=False,
                                                       add_generation_prompt=True, enable_thinking=False)
                inputs = tokenizer(prompt, return_tensors="pt")
                if inputs.input_ids.shape[1] > 10000:
                    return self.reply({"error": "teaching input token limit"}, 400)
                start = time.monotonic()
                maximum = min(int(body.get("options", {}).get("num_predict", 192)), 320)
                with torch.inference_mode():
                    output = model.generate(**inputs, max_new_tokens=maximum, do_sample=False,
                                            pad_token_id=tokenizer.eos_token_id)
                generated = output[0, inputs.input_ids.shape[1]:]
                raw = tokenizer.decode(generated, skip_special_tokens=True)
                calls = []
                for value in re.findall(r"<tool_call>\s*(.*?)\s*</tool_call>", raw, re.S):
                    parsed = json.loads(value)
                    calls.append({"function": {"name": parsed["name"], "arguments": parsed["arguments"]}})
                content = re.sub(r"<tool_call>.*?</tool_call>", "", raw, flags=re.S).strip()
                message = {"role": "assistant", "content": content}
                if calls:
                    message["tool_calls"] = calls
                return self.reply({"model": MODEL, "message": message, "raw_generated": raw, "done": True,
                                   "prompt_eval_count": inputs.input_ids.shape[1], "eval_count": len(generated),
                                   "total_duration": int((time.monotonic() - start) * 1e9),
                                   "evidence_mode": "live_local_model", "backend": "Transformers CPU, no replay"})
            except Exception as error:
                self.reply({"error": type(error).__name__ + ": " + str(error)}, 500)

    print("READY CPU local model adapter at http://127.0.0.1:" + str(args.port), flush=True)
    HTTPServer(("127.0.0.1", args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()

"""Reproduce the course's live CPU experiments; preserve failures as evidence."""
import csv
import importlib.util
import json
import os
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evidence/20261020"
MODEL = "qwen3:0.6b-cpu"
os.chdir(ROOT)
scope = {"__name__": "course_loader"}
for cell in json.loads((ROOT / "00-foundations/00-setup.ipynb").read_text())["cells"]:
    if cell["cell_type"] == "code" and "definitions" in cell.get("metadata", {}).get("tags", []):
        exec(compile("".join(cell["source"]), "course_setup", "exec"), scope)
load = scope["load_lesson"]
live = load("01-agent-loop/02-live-model.ipynb")


def save(name, data):
    path = OUT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, default=lambda o: vars(o)) + "\n")


def attempt(name, operation):
    start = time.monotonic()
    try:
        value = operation()
        save(name + "/execution.json", {"executed": True, "seconds": time.monotonic() - start,
             "backend": "Transformers CPU adapter, not Ollama", "evidence_mode": "live_local_model"})
        print("EXECUTED", name, flush=True)
        return value
    except Exception as error:
        save(name + "/execution.json", {"executed": False, "error": type(error).__name__, "detail": str(error),
                                        "seconds": time.monotonic() - start})
        print("FAILED", name, type(error).__name__, str(error)[:250], flush=True)


if __name__ == "__main__":
    save("model-manifest.json", {"generation": live.model_manifest(MODEL),
         "embedding": "sentence-transformers/all-MiniLM-L6-v2, 384 dimensions",
         "device": "cpu", "threads": 4, "temperature": 0,
         "adapter": "scripts/serve_local_models.py exposes a subset of Ollama-shaped routes; models are real Transformers inference",
         "paths": json.loads((OUT / "model-paths.json").read_text())})
    basic = live.chat([{"role": "user", "content": "In one sentence, explain why an agent reads tool results before choosing another action."}], model=MODEL, max_output=96)
    structured = live.chat([{"role": "user", "content": 'Return JSON with fields stage:7, minimum_tasks:20, evidence_required:true.'}], model=MODEL, json_mode=True, max_output=96)
    save("stage1-api.json", {"ordinary_dialogue": basic, "structured_json": structured})
    specification = importlib.util.spec_from_file_location("minimal_agent", ROOT / "experiments/minimal_agent.py")
    minimal = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(minimal)
    docs = json.loads((OUT / "documents.json").read_text())
    result = minimal.run('Use read_file to read course.md before answering. Which stage requires at least 20 evaluation tasks? Cite the observed source.', docs)
    save("stage1-guided-tool-loop.json", result)
    print("STAGE1 GUIDED", result["status"], len(result["trace"]), result["answer"][:200], flush=True)
    eval_lesson = load("07-evaluation-safety/02-live-evaluation.ipynb")
    evaluation = attempt("stage7-evaluation", lambda: eval_lesson.run(OUT / "stage7-evaluation", model=MODEL))
    if evaluation:
        rows = json.loads((OUT / "stage7-evaluation/results.json").read_text())
        fields = ["task_id", "category", "question", "expected", "actual", "passed", "failure_class",
                  "tool_calls", "model_calls", "input_tokens", "output_tokens", "latency_ms", "cost_usd", "evidence_mode", "trace_path"]
        with (OUT / "eval.csv").open("w", newline="", encoding="utf-8-sig") as file:
            writer = csv.DictWriter(file, fieldnames=fields)
            writer.writeheader()
            for row in rows:
                writer.writerow({"task_id": row["task_id"], "category": row["scenario"], "question": row["input"],
                  "expected": json.dumps(row["expected"], ensure_ascii=False), "actual": json.dumps(row["actual"], ensure_ascii=False),
                  "passed": row["task_success"], "failure_class": row["failure_reason"], "tool_calls": row["tool_calls"],
                  "model_calls": len(row["requests"]), "input_tokens": row["input_tokens"], "output_tokens": row["output_tokens"],
                  "latency_ms": row["latency_ms"], "cost_usd": "", "evidence_mode": "live_local_model", "trace_path": row["trace_path"]})
        save("metrics.json", {"evaluation": evaluation,
             "cost_basis": "local CPU inference; no paid API bill; hardware and electricity unmeasured",
             "warning": "Frozen fictional fact tasks, not open-world research quality or host security certification"})
    attempt("stage2-rag", lambda: load("02-tools-rag-memory/03-web-research.ipynb").run_local(
            OUT / "stage2-rag", model=MODEL, embedding_model="all-minilm:l6-v2-cpu"))
    attempt("stage3-upstream", lambda: load("03-agent-harness/02-upstream-comparison.ipynb").run(
            OUT / "stage3-upstream", model=MODEL))
    attempt("stage4-coordination", lambda: load("04-multi-agent/02-live-coordination.ipynb").run(
            OUT / "stage4-coordination", model=MODEL))
    attempt("stage5-skill", lambda: load("05-skills-protocols/02-skill-comparison.ipynb").run_comparison(
            OUT / "stage5-skill", model=MODEL, max_output=256))
    attempt("stage6-browser", lambda: load("06-browser-agent/02-public-page-agent.ipynb").run_public_agent(
            OUT / "stage6-browser", model=MODEL))
    print("LIVE LAB RUN FINISHED", flush=True)

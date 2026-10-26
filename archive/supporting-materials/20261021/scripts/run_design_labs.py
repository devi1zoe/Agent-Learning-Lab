"""Reproduce the course's live CPU experiments; preserve failures as evidence."""
import csv
import argparse
from datetime import datetime, timezone
import importlib.util
import json
import os
import time
from urllib.parse import urlsplit
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evidence/20261020"
MODEL = "qwen3:0.6b-cpu"
os.chdir(ROOT)
import sys
sys.path.insert(0, str(ROOT))
from miniagent_course import load_lesson as load
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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "outputs" / ("design-labs-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")))
    parser.add_argument("--model-manifest", type=Path, default=ROOT / "outputs/local-model-paths.json")
    args = parser.parse_args()
    OUT = args.output_dir.resolve()
    OUT.mkdir(parents=True, exist_ok=False)
    save("model-manifest.json", {"generation": live.model_manifest(MODEL),
         "embedding": "sentence-transformers/all-MiniLM-L6-v2, 384 dimensions",
         "device": "cpu", "threads": 4, "temperature": 0,
         "adapter": "scripts/serve_local_models.py exposes a subset of Ollama-shaped routes; models are real Transformers inference",
         "paths": json.loads(args.model_manifest.read_text())})
    basic = live.chat([{"role": "user", "content": "In one sentence, explain why an agent reads tool results before choosing another action."}], model=MODEL, max_output=96)
    structured = live.chat([{"role": "user", "content": 'Return JSON with fields stage:7, minimum_tasks:20, evidence_required:true.'}], model=MODEL, json_mode=True, max_output=96)
    save("stage1-api.json", {"ordinary_dialogue": basic, "structured_json": structured})
    specification = importlib.util.spec_from_file_location("minimal_agent", ROOT / "experiments/minimal_agent.py")
    minimal = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(minimal)
    docs = json.loads((ROOT / "evidence/20261020/documents.json").read_text())
    result = minimal.run('Which stage requires at least twenty evaluation tasks, and why does an agent need evidence from tools before claiming success? Read the relevant documents and cite them.', docs, require_evidence=False)
    save("stage1-tool-loop.json", result)
    result = minimal.run('Use read_file to read course.md before answering. Which stage requires at least 20 evaluation tasks? Cite the observed source.', docs, require_evidence=False)
    save("stage1-guided-tool-loop.json", result)
    save("stage1-evidence-gate.json", minimal.run('Which stage requires at least twenty evaluation tasks? Read the course requirements and cite the observed source.', docs, require_evidence=True))
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
    attempt("stage2-web-research", lambda: load("02-tools-rag-memory/03-web-research.ipynb").run(
            OUT / "stage2-web-research", model=MODEL))
    attempt("stage3-upstream", lambda: load("03-agent-harness/02-upstream-comparison.ipynb").run(
            OUT / "stage3-upstream", model=MODEL))
    attempt("stage4-coordination", lambda: load("04-multi-agent/02-live-coordination.ipynb").run(
            OUT / "stage4-coordination", model=MODEL))
    attempt("stage5-skill", lambda: load("05-skills-protocols/02-skill-comparison.ipynb").run_comparison(
            OUT / "stage5-skill", model=MODEL, max_output=256))
    attempt("stage6-browser", lambda: load("06-browser-agent/02-public-page-agent.ipynb").run_public_agent(
            OUT / "stage6-browser", model=MODEL))
    def course_page():
        module = load("06-browser-agent/02-public-page-agent.ipynb")
        previous = module.PUBLIC_URL, module.allowed_request
        module.PUBLIC_URL = "https://github.com/datawhalechina/Agent-Learning-Hub"
        module.allowed_request = lambda url, method="GET": urlsplit(url).scheme == "https" and urlsplit(url).netloc == "github.com" and method == "GET"
        try:
            result = module.run_public_agent(OUT / "stage6-course-page", model=MODEL)
            save("stage6-course-page/experiment.json", {"kind": "separate supplemental public-page example", "target": module.PUBLIC_URL,
                 "changes": ["PUBLIC_URL", "host allowlist"], "network_scope": "HTTPS GET to github.com only"})
            return result
        finally:
            module.PUBLIC_URL, module.allowed_request = previous
    attempt("stage6-course-page", course_page)
    def delivery():
        module = load("08-capstone/02-delivery-check.ipynb")
        destination = OUT / "stage8-delivery"
        module.export_project(destination / "project")
        return module.check_delivery(destination / "project", destination / "verification", live=True, model=MODEL)
    attempt("stage8-delivery", delivery)
    print("LIVE LAB RUN FINISHED", flush=True)

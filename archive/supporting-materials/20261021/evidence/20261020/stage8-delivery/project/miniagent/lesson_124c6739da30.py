from __future__ import annotations
from ._loader import ROOT, OUTPUT, load_lesson

import copy, json, math, re, time, tempfile, os, sys
from dataclasses import dataclass
from pathlib import Path
from urllib.request import Request, build_opener, ProxyHandler
os.environ["PYTHONIOENCODING"] = "utf-8"

def chunks(text, size=120, overlap=20):
    if not 0 <= overlap < size:
        raise ValueError("require 0 <= overlap < size")
    return [{"start": i, "end": min(i+size, len(text)), "text": text[i:i+size]}
            for i in range(0, len(text), size-overlap)]

def terms(text):
    """English tokens and Chinese bigrams; a transparent lexical baseline."""
    english = re.findall(r"[a-z0-9]+", text.lower())
    chinese = re.findall(r"[\u4e00-\u9fff]+", text)
    return set(english + [s[i:i+2] for s in chinese for i in range(max(1, len(s)-1))])

class DocumentIndex:
    def __init__(self, documents):
        self.rows = []
        for name, text in documents.items():
            for part in chunks(text):
                self.rows.append({"id": "L"+str(len(self.rows)+1), "source": name, **part})

    def search(self, query, top_k=3):
        query_terms = terms(query)
        rows = [{**r, "score": len(query_terms & terms(r["text"])) / max(1, len(query_terms))}
                for r in self.rows]
        return sorted((r for r in rows if r["score"] > 0), key=lambda r: -r["score"])[:top_k]

def citation_errors(answer, evidence):
    """Check identifiers, not semantic entailment."""
    ids = set(re.findall(r"\[(L\d+)\]", answer))
    valid = {r["id"] for r in evidence}
    return sorted(ids-valid) + ([] if ids else ["missing_citation"])

class SessionStore:
    def __init__(self, directory):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def save(self, name, value):
        if name not in {"session", "memory", "trace"}:
            raise ValueError("unknown state name")
        target = self.directory / (name+".json")
        pending = target.with_suffix(".tmp")
        pending.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
        pending.replace(target)

    def load(self, name, default=None):
        if name not in {"session", "memory", "trace"}:
            raise ValueError("unknown state name")
        path = self.directory / (name+".json")
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default

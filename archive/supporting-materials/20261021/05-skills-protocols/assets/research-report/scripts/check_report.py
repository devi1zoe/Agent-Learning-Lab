#!/usr/bin/env python3
"""Check report structure and source IDs; deliberately not a factuality judge."""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

SECTIONS = ("问题", "结论", "证据", "局限")


def check_report(text: str, known_sources=None):
    errors = []
    parts = {}
    headings = list(re.finditer(r"^## ([^\n]+?)\s*$", text, re.M))
    for index, match in enumerate(headings):
        name = match.group(1).strip()
        if name in parts:
            errors.append("duplicate_section:" + name)
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        parts[name] = text[match.end():end].strip()
    for section in SECTIONS:
        if section not in parts:
            errors.append("missing_section:" + section)
        elif not parts[section]:
            errors.append("empty_section:" + section)
    evidence_ids = re.findall(r"^\[(L\d+)\]\s+\S.+", parts.get("证据", ""), re.M)
    declared = set(evidence_ids)
    for item in declared:
        if evidence_ids.count(item) > 1:
            errors.append("duplicate_source:" + item)
    used = set(re.findall(r"\[(L\d+)\]", parts.get("结论", "")))
    if not used and "无法据此回答" not in parts.get("结论", ""):
        errors.append("missing_citations")
    errors.extend("unknown_source:" + item for item in sorted(used - declared))
    if known_sources is not None:
        known = set(known_sources)
        errors.extend("undeclared_input_source:" + item for item in sorted(declared - known))
    return {
        "structural_ok": not errors,
        "errors": errors,
        "conclusion_source_ids": sorted(used),
        "evidence_source_ids": sorted(declared),
        "semantic_support_verified": False,
        "scope": "Structure/source-ID checks only; compare every claim against the original evidence separately.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    parser.add_argument("--sources", type=Path)
    args = parser.parse_args()
    sources = None
    if args.sources:
        sources = json.loads(args.sources.read_text(encoding="utf-8"))
        if not isinstance(sources, (list, dict)) or any(not isinstance(k, str) for k in sources):
            parser.error("--sources must contain a JSON list of IDs or an object keyed by IDs")
    result = check_report(args.report.read_text(encoding="utf-8"), sources)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["structural_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

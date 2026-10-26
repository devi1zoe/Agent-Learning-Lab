#!/usr/bin/env python3
"""Deterministic contract smoke; does not measure model uplift from the skill."""
import json
from check_report import check_report

GOOD = """# 报告
## 问题
蓝舟项目位于哪座城市？
## 结论
位于苏州。[L1]
## 证据
[L1] project.md，第1段 — 蓝舟项目位于苏州。
## 局限
仅依据给定资料，尚未核验资料更新时间。
"""


def run():
    rows = []
    good = check_report(GOOD, ["L1"])
    assert good["structural_ok"]
    rows.append({"case": "supported_fixture_structure", "result": good})
    bad_id = check_report(GOOD.replace("苏州。[L1]", "苏州。[L99]"), ["L1"])
    assert "unknown_source:L99" in bad_id["errors"]
    rows.append({"case": "invented_citation_rejected", "result": bad_id})
    missing = check_report(GOOD.replace("## 局限", "## 其他"), ["L1"])
    assert "missing_section:局限" in missing["errors"]
    rows.append({"case": "missing_section_rejected", "result": missing})
    fabricated = check_report(GOOD, ["L2"])
    assert "undeclared_input_source:L1" in fabricated["errors"]
    rows.append({"case": "evidence_not_in_input_rejected", "result": fabricated})
    wrong_fact = check_report(GOOD.replace("位于苏州。[L1]", "位于北京。[L1]"), ["L1"])
    assert wrong_fact["structural_ok"] and not wrong_fact["semantic_support_verified"]
    rows.append({"case": "semantic_error_exposes_checker_limit", "result": wrong_fact})
    unknown = GOOD.replace("位于苏州。[L1]", "无法据此回答，给定资料没有该字段。")
    assert check_report(unknown, ["L1"])["structural_ok"]
    rows.append({"case": "abstention_structure_allowed", "result": check_report(unknown, ["L1"])})
    return {"contract_cases": len(rows), "contract_passed": True,
            "model_effect_test": "not_run_by_this_script; use paired real-model experiment",
            "rows": rows}


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))

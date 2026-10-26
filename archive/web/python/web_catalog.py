"""Build a static reading site from the repository's actual learning materials."""
import argparse
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

from .web_course import compose

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"
STAGES = [
    ("理解 Agent", "从一个好问题开始", "辨清对话、工作流与 Agent，找到真正需要动态决策的场景。", "Foundations", "理解概念"),
    ("最小 Agent 循环", "让模型第一次动手", "从 JSON、工具分发到反馈，亲手走通一个最小闭环。", "The loop", "调用工具"),
    ("工具、RAG 与记忆", "让回答有据可查", "连接文档、网页与数据，理解检索、证据和记忆的边界。", "Knowledge", "使用证据"),
    ("Agent Harness", "给能力装上控制系统", "读懂工具、权限、会话、上下文与 trace 如何围绕模型工作。", "The harness", "控制执行"),
    ("多 Agent 协作", "让分工真正发生", "定义研究、写作、审核的交接，管理循环、漂移与停止。", "Coordination", "协调角色"),
    ("Skills 与协议", "把经验变成可复用能力", "区分 Skill、Tool、MCP，封装流程，再验证它是否有帮助。", "Capabilities", "封装能力"),
    ("浏览器 Agent", "走进真实页面", "观察页面、执行动作、应对变化，保存可回看的操作证据。", "The browser", "观察与行动"),
    ("评测与安全", "知道它到底做得怎样", "用固定任务、真实 trace 与失败分类，检验质量和边界。", "Evaluation", "验证质量"),
    ("交付真实项目", "从能跑到能交给别人", "做好配置、预算、错误处理与审批，交付一份可运行的作品。", "Ship it", "完成交付"),
]
EXTENSIONS = {
    "stage1b-react-learning.ipynb": ("ReAct", "在行动与观察之间，决定下一步", 1),
    "stage2b-self-ask-learning.ipynb": ("Self-Ask", "把复杂问题拆成有证据的子问题", 2),
    "stage3b-planning-reflection-learning.ipynb": ("规划与反思", "Plan-and-Execute · Reflection · Reflexion", 3),
    "stage3c-tot-compiler-learning.ipynb": ("ToT 与 LLMCompiler", "候选搜索与依赖调度，分开看懂", 3),
}


def source_text(value):
    return "".join(value) if isinstance(value, list) else str(value or "")


def title_from(source, fallback):
    match = re.search(r"^#\s+(.+)", source, re.M)
    return match.group(1).strip() if match else fallback


def collect():
    paths = set(ROOT.glob("*.md"))
    paths.update([ROOT / "requirements-learning.txt", ROOT / "start-learning.bat"])
    if (WEB / "README.md").exists():
        paths.add(WEB / "README.md")
    for folder in [*sorted(ROOT.glob("step[0-8]")), ROOT / "learning"]:
        paths.update(p for p in folder.rglob("*") if p.is_file() and
                     p.suffix.lower() in {".md", ".ipynb", ".py", ".txt", ".html"} and
                     not any(s.startswith(".") or s == "__pycache__" for s in p.relative_to(ROOT).parts))
    lessons = []
    for path in sorted(paths):
        relative = path.relative_to(ROOT).as_posix()
        match = re.match(r"step([0-8])/", relative)
        stage = int(match.group(1)) if match else None
        text = path.read_text(encoding="utf-8-sig")
        title, cells = path.stem, []
        kind = "document"
        if path.suffix == ".ipynb":
            notebook = json.loads(text)
            kind = "notebook"
            for original_index, cell in enumerate(notebook["cells"]):
                if cell.get("metadata", {}).get("learning_support") in {"prerequisites-v1", "course-alignment-v1"}:
                    continue
                cell_source = source_text(cell.get("source"))
                outputs = []
                for output in cell.get("outputs", []):
                    value = source_text(output.get("text")) or source_text(output.get("data", {}).get("text/plain"))
                    if value:
                        outputs.append(value[:20000])
                cells.append({"type": cell["cell_type"], "source": cell_source, "outputs": outputs,
                              "number": original_index + 1})
            markdown = "\n\n".join(c["source"] for c in cells if c["type"] == "markdown")
            title = title_from(markdown, title)
        elif path.suffix == ".md":
            title = title_from(text, title)
            cells = [{"type": "markdown", "source": text, "outputs": []}]
        else:
            kind = "source"
            language = {".py": "python", ".html": "xml", ".bat": "dos"}.get(path.suffix, "plaintext")
            cells = [{"type": "code", "source": text, "language": language, "outputs": []}]
        is_main = bool(stage is not None and path.name == f"stage{stage}-learning.ipynb")
        extension = path.name in EXTENSIONS
        search_text = "\n".join(c["source"] for c in cells)
        lessons.append({"id": relative, "path": relative, "title": EXTENSIONS[path.name][0] if extension else title,
                        "stage": stage, "kind": kind, "main": is_main, "track": "extension" if extension else "core" if is_main else "resource",
                        "runnable": is_main or extension or path.name == "step2_stage2_diagnostics_fixed.ipynb",
                        "cells": cells, "characters": len(search_text), "minutes": max(3, round(len(search_text)/650)),
                        "download": "files/" + relative})
    stage_data = []
    for index, (title, subtitle, description, english, outcome) in enumerate(STAGES):
        prefix = f"step{index}/"
        stage_data.append({"id": index, "title": title, "subtitle": subtitle, "description": description,
                           "english": english, "outcome": outcome, "lesson": f"{prefix}stage{index}-learning.ipynb",
                           "prerequisite": prefix + "00-prerequisites.md", "tasks": prefix + "COURSE-TASKS.md",
                           "resources": [l["id"] for l in lessons if l["stage"] == index and l["track"] == "resource"],
                           "task_count": [5, 6, 5, 5, 5, 8, 5, 6, 5][index]})
    for stage in stage_data:
        stage["reading"] = compose(stage, lessons)
    return {"generated_at": datetime.now(timezone.utc).isoformat(), "title": "miniAgent 学习路线",
            "stages": stage_data, "extensions": [{"title": title, "description": description, "after": after,
             "lesson": next(l["id"] for l in lessons if Path(l["path"]).name == name)}
             for name, (title, description, after) in EXTENSIONS.items()], "lessons": lessons}


def build(output=None):
    output = Path(output or WEB / "dist").resolve()
    output.mkdir(parents=True, exist_ok=True)
    for name in ["index.html", "app.js", "style.css", "highlight.css"]:
        shutil.copyfile(WEB / name, output / name)
    shutil.copytree(WEB / "vendor", output / "vendor", dirs_exist_ok=True)
    catalog = collect()
    (output / "catalog.json").write_text(json.dumps(catalog, ensure_ascii=False), encoding="utf-8")
    for lesson in catalog["lessons"]:
        destination = output / lesson["download"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / lesson["path"], destination)
    print(f"Built {len(catalog['lessons'])} materials, 9 stages and 4 extensions at {output}")
    return catalog


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    build(args.output)

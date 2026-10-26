"""Load shared Notebook definitions without running examples or model calls."""
import json, sys, types, hashlib, linecache
from pathlib import Path
ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents]
            if (p / "scripts/lesson_loader.py").is_file())
OUTPUT = ROOT / "outputs"
_LESSON_CACHE = {}
def load_lesson(relative_path):
    """Reuse explicitly tagged definitions; examples and live calls are never imported."""
    path = (ROOT / relative_path).resolve()
    path.relative_to(ROOT)
    if path.suffix != ".ipynb" or "archive" in path.relative_to(ROOT).parts:
        raise ValueError("Only course notebooks can supply definitions")
    if path in _LESSON_CACHE:
        return _LESSON_CACHE[path]
    name = "lesson_" + hashlib.sha256(str(path).encode()).hexdigest()[:16]
    module = types.ModuleType(name)
    module.__dict__.update(ROOT=ROOT, OUTPUT=OUTPUT, load_lesson=load_lesson, __file__=str(path))
    sys.modules[name] = module
    _LESSON_CACHE[path] = module
    try:
        book = json.loads(path.read_text(encoding="utf-8"))
        for index, cell in enumerate(book["cells"]):
            if cell["cell_type"] != "code" or "definitions" not in cell.get("metadata", {}).get("tags", []):
                continue
            source = "".join(cell["source"])
            filename = str(path) + "::cell-" + str(index + 1)
            linecache.cache[filename] = (len(source), None, source.splitlines(True), filename)
            exec(compile(source, filename, "exec", flags=0x1000000), module.__dict__)
        return module
    except Exception:
        _LESSON_CACHE.pop(path, None)
        sys.modules.pop(name, None)
        raise

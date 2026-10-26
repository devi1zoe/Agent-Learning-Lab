"""Shared course imports; load tagged Notebook definitions without running examples."""
import ast, json, sys, types, hashlib, linecache
from pathlib import Path
ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "archive" / "runs"
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


def lesson_assets(relative_path):
    """Materialize exact text assets embedded in a Notebook, only when needed."""
    path = (ROOT / relative_path).resolve()
    path.relative_to(ROOT)
    book = json.loads(path.read_text(encoding="utf-8"))
    assets = {}
    for cell in book["cells"]:
        if cell["cell_type"] != "code" or "assets" not in cell.get("metadata", {}).get("tags", []):
            continue
        for node in ast.parse("".join(cell["source"])).body:
            if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "LESSON_ASSETS" for target in node.targets):
                assets.update(ast.literal_eval(node.value))
    if not assets:
        raise ValueError("No embedded text assets in " + relative_path)
    digest = hashlib.sha256(json.dumps(assets, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()[:16]
    directory = OUTPUT / "generated-assets" / digest
    for name, text in assets.items():
        if not isinstance(name, str) or not isinstance(text, str):
            raise ValueError("Embedded assets must map relative paths to UTF-8 text")
        target = (directory / name).resolve()
        target.relative_to(directory.resolve())
        payload = text.encode("utf-8")
        if target.exists():
            if target.read_bytes() != payload:
                raise ValueError("Generated asset was modified; preserve it and use a fresh run directory: " + str(target))
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("xb") as stream:
                stream.write(payload)
    return directory

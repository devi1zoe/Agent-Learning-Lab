from pathlib import Path
import importlib

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'outputs'
MODULE_MAP = {'08-capstone/01-research-assistant.ipynb': 'lesson_f50ea8ecb9a4', '03-agent-harness/01-harness.ipynb': 'lesson_0c014a6184bc', '01-agent-loop/01-minimal-loop.ipynb': 'lesson_c690f01c5159', '02-tools-rag-memory/01-rag-and-memory.ipynb': 'lesson_124c6739da30'}

def load_lesson(relative):
    return importlib.import_module('.' + MODULE_MAP[relative], __package__)

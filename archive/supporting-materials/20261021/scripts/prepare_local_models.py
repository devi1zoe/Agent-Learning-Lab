"""Download the two public CPU demonstration models and record exact snapshots."""
import argparse
import json
from pathlib import Path
from huggingface_hub import snapshot_download

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache-dir", type=Path, default=ROOT / "outputs/model-cache")
    parser.add_argument("--manifest-out", type=Path, default=ROOT / "outputs/local-model-paths.json")
    parser.add_argument("--offline", action="store_true", help="Reuse an existing cache without network access")
    args = parser.parse_args()
    specifications = {
        "Qwen/Qwen3-0.6B": ["*.json", "*.safetensors", "tokenizer*", "merges.txt", "vocab.json", "LICENSE", "README.md"],
        "sentence-transformers/all-MiniLM-L6-v2": ["config.json", "model.safetensors", "tokenizer.json", "tokenizer_config.json", "special_tokens_map.json", "vocab.txt", "README.md", "LICENSE"],
    }
    paths = {}
    revisions = {"Qwen/Qwen3-0.6B": "c1899de289a04d12100db370d81485cdf75e47ca",
                 "sentence-transformers/all-MiniLM-L6-v2": "1110a243fdf4706b3f48f1d95db1a4f5529b4d41"}
    for name, patterns in specifications.items():
        paths[name] = snapshot_download(repo_id=name, revision=revisions[name], cache_dir=str(args.cache_dir), allow_patterns=patterns, local_files_only=args.offline)
        print(name, paths[name], flush=True)
    target = args.manifest_out.resolve()
    if target.is_relative_to((ROOT / "evidence").resolve()):
        raise ValueError("Local configuration must not overwrite historical evidence")
    target.parent.mkdir(parents=True, exist_ok=True)
    # This is local runtime configuration, separate from immutable experiment evidence.
    target.write_text(json.dumps(paths, indent=2) + "\n")


if __name__ == "__main__":
    main()

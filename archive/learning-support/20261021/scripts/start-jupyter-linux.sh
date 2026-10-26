#!/usr/bin/env bash
set -euo pipefail

project_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
miniagent_python="${MINIAGENT_PYTHON:-}"
if [[ -z "$miniagent_python" ]]; then
  if [[ -x "$project_root/.venv/bin/python" ]]; then
    miniagent_python="$project_root/.venv/bin/python"
  else
    miniagent_python="python3"
  fi
fi

miniagent_port="${MINIAGENT_PORT:-8888}"
if [[ ! "$miniagent_port" =~ ^[1-9][0-9]{0,4}$ ]] || (( miniagent_port > 65535 )); then
  printf 'MINIAGENT_PORT must be an integer from 1 to 65535.\n' >&2
  exit 2
fi
if ! command -v "$miniagent_python" >/dev/null 2>&1; then
  printf 'Python not found: %s\nSee LINUX-START.md for environment setup.\n' "$miniagent_python" >&2
  exit 1
fi
if ! "$miniagent_python" -c 'import jupyterlab, ipykernel' >/dev/null 2>&1; then
  printf 'JupyterLab or ipykernel is missing in %s.\nSee LINUX-START.md for dependency installation.\n' "$miniagent_python" >&2
  exit 1
fi

# Keep runtime files with the project, including when the home directory is read-only.
umask 077
export JUPYTER_RUNTIME_DIR="$project_root/outputs/jupyter/runtime"
mkdir -p -- "$JUPYTER_RUNTIME_DIR"
cd -- "$project_root"
printf 'Mini Agent: %s\nPython: %s\nForward remote port %s to your computer.\n' \
  "$project_root" "$miniagent_python" "$miniagent_port"
exec "$miniagent_python" -m jupyterlab --no-browser --ip=127.0.0.1 \
  --port="$miniagent_port" --ServerApp.port_retries=0 \
  --ServerApp.root_dir="$project_root"

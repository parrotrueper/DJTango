#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
  echo ".venv not found. Run ./setup-env.sh first." >&2
  exit 1
fi

if [ ! -f ".venv/bin/python" ]; then
  echo ".venv Python not found. Run ./setup-env.sh first." >&2
  exit 1
fi

# shellcheck source=/dev/null
. .venv/bin/activate

if ! .venv/bin/python -c 'import PySide6' >/dev/null 2>&1 && ! .venv/bin/python -c 'import PyQt5' >/dev/null 2>&1; then
  echo "GUI mode requires PySide6 or PyQt5 installed in .venv. Run './.venv/bin/python -m pip install PySide6' or install the GUI dependency." >&2
  exit 1
fi

exec .venv/bin/python bin/DJTango.py "$@"

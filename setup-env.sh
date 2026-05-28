#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required but not installed. Please install Python 3." >&2
  exit 1
fi

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

if [ ! -f ".venv/bin/activate" ]; then
  echo ".venv was not created correctly. Remove it and retry." >&2
  exit 1
fi

# Activate the virtual environment for installation
# shellcheck source=/dev/null
. .venv/bin/activate

python -m pip install --upgrade pip setuptools wheel
python -m pip install -e .

echo "Virtual environment created and project installed in .venv."
echo "Activate it with: source .venv/bin/activate"

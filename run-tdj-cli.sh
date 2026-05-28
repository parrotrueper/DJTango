#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
  echo ".venv not found. Run ./setup-env.sh first." >&2
  exit 1
fi

if [ ! -f ".venv/bin/python" ]; then
  echo ".venv/bin/python not found. Run ./setup-env.sh first." >&2
  exit 1
fi

# shellcheck source=/dev/null
. .venv/bin/activate

if [ "$#" -eq 0 ]; then
  exec .venv/bin/python bin/djtango_cli.py --help
else
  exec .venv/bin/python bin/djtango_cli.py "$@"
fi

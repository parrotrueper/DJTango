#!/usr/bin/env bash
set -euo pipefail

# shellcheck source=/dev/null
. ci/functions.sh


if [[ ! -f pyproject.toml ]]; then
  fatal 1 "dev-check.sh must be run from the repository root"
fi

if ! python -m uv --version >/dev/null 2>&1; then
  fatal 1 "uv is required to run dev-check.sh"
  info "Install it with: python -m pip install -e .[dev]"
fi

info "Running development checks with uv"
python -m uv run --with ruff --with mypy --with lizard -- bash -lc '
  ruff check djtango tests &&
  mypy djtango &&
  lizard djtango &&
  python -m pytest -q
'


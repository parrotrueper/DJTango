#!/usr/bin/env bash
set -euo pipefail

# shellcheck source=/dev/null
. ci/functions.sh

venv_dir=".venv"
in_docker=$(is_in_container)

if [[ "$in_docker" == "true" ]]; then
  venv_dir=".dkr_venv"
  export PIP_NO_CACHE_DIR=1
fi

PYTHON_CMD=$(command -v python3 || command -v python || true)
if [[ -z "$PYTHON_CMD" ]]; then
  fatal 1 "python3 or python is required but not installed. Please install Python 3." >&2
fi

if [ -d "${venv_dir}" ]; then
  if [ ! -f "${venv_dir}/bin/activate" ] || ! "${venv_dir}/bin/python" -c 'import sys' >/dev/null 2>&1; then
    info "Removing invalid or broken existing .venv"
    run rm -rf "${venv_dir}"
  fi
fi

if [ ! -d "${venv_dir}" ]; then
  run "$PYTHON_CMD" -m venv "${venv_dir}"
fi

if [ ! -f "${venv_dir}/bin/activate" ] || ! "${venv_dir}/bin/python" -c 'import sys' >/dev/null 2>&1; then
  info "Recreating broken .venv with $PYTHON_CMD"
  run rm -rf "${venv_dir}"
  run "$PYTHON_CMD" -m venv "${venv_dir}"
fi

if [ ! -f "${venv_dir}/bin/activate" ]; then
  fatal 1 ".venv was not created correctly. Remove it and retry." >&2
fi

VENV_PYTHON="${venv_dir}/bin/python"
if [[ ! -x "$VENV_PYTHON" ]]; then
  if [[ -x "${venv_dir}/bin/python3" ]]; then
    VENV_PYTHON="${venv_dir}/bin/python3"
  fi
fi

if [[ ! -x "$VENV_PYTHON" ]] || ! "$VENV_PYTHON" -c 'import sys' >/dev/null 2>&1; then
  fatal 1 "ERROR: no valid Python executable found in .venv/bin" >&2
fi

if ! "$VENV_PYTHON" -m pip --version >/dev/null 2>&1; then
  info "Bootstrapping pip into virtual environment"
  "$VENV_PYTHON" -m ensurepip --upgrade
fi

if [ ! -f "${venv_dir}/bin/activate" ]; then
  fatal 1 ".venv was not created correctly. Remove it and retry." >&2
fi

# Activate the virtual environment for installation
# shellcheck source=/dev/null
. "${venv_dir}/bin/activate"

VENV_PYTHON="${venv_dir}/bin/python3"
if [[ ! -x "$VENV_PYTHON" ]]; then
  VENV_PYTHON="${venv_dir}/bin/python"
fi

if [[ ! -x "$VENV_PYTHON" ]]; then
  fatal 1 "ERROR: no Python executable found in .venv/bin" >&2
fi

if ! "$VENV_PYTHON" -m pip --version >/dev/null 2>&1; then
  info "Bootstrapping pip into virtual environment"
  "$VENV_PYTHON" -m ensurepip --upgrade
fi

"$VENV_PYTHON" -m pip install --upgrade pip setuptools wheel
"$VENV_PYTHON" -m pip install -e .[test,dev]

info "Virtual environment created and project installed in ${venv_dir}."
info "Activate it with: source ${venv_dir}/bin/activate"
info "Run the new QML GUI with: ./run-ttvttm.sh"

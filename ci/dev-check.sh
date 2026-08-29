#!/usr/bin/env bash
set -euo pipefail

# shellcheck source=/dev/null
. ci/functions.sh
# shellcheck source=/dev/null
. /etc/bash.bashrc

venv_dir=".venv"
in_docker=$(is_in_container)

if [[ "$in_docker" == "true" ]]; then
  venv_dir=".dkr_venv"
  export PIP_NO_CACHE_DIR=1
fi

if [[ ! -f pyproject.toml ]]; then
  fatal 1 "dev-check.sh must be run from the repository root"
fi

# Prefer a local virtual environment if present, otherwise create one.
PYTHON=""
if [[ -x "${venv_dir}/bin/python" ]]; then
  PYTHON="${venv_dir}/bin/python"
else
  # Avoid a partially-created .venv/bin/python3 from a stale VIRTUAL_ENV
  SEARCH_PATH=$(printf '%s\n' "${PATH}" | grep -v "\.venv/bin" | paste -sd ':' -)
  for candidate in python3 python; do
    if PATH="${SEARCH_PATH}" command -v "${candidate}" >/dev/null 2>&1; then
      PYTHON="$(PATH="${SEARCH_PATH}" command -v "${candidate}")"
      break
    fi
  done
fi

if [[ -z "${PYTHON}" ]]; then
  fatal 1 "No Python interpreter found. Install Python 3 and retry."
fi

if [[ -d "${venv_dir}" && ! -x "${venv_dir}/bin/python" ]]; then
  info "Removing incomplete virtual environment ${venv_dir}"
  rm -rf "${venv_dir}"
fi

if [[ ! -x "${venv_dir}/bin/python" ]]; then
  info "Creating local virtual environment in ${venv_dir}"
  "${PYTHON}" -m venv "${venv_dir}"
  PYTHON="${venv_dir}/bin/python"
fi

if [[ ! -x "${venv_dir}/bin/python3" && -x "${venv_dir}/bin/python" ]]; then
  info "Creating python3 symlink in ${venv_dir}/bin"
  ln -sf python "${venv_dir}/bin/python3"
fi
if [[ ! -x "${venv_dir}/bin/python3.14" && -x "${venv_dir}/bin/python3" ]]; then
  ln -sf python3 "${venv_dir}/bin/python3.14" || true
fi

info "Using Python interpreter: ${PYTHON}"
if ! "${PYTHON}" -m pip install --upgrade pip >/dev/null 2>&1; then
  info "Bootstrapping pip into the virtual environment"
  if ! "${PYTHON}" -m ensurepip --upgrade >/dev/null 2>&1; then
    fatal 1 "Failed to bootstrap pip in ${venv_dir}. Install pip or recreate the virtualenv."
  fi
  "${PYTHON}" -m pip install --upgrade pip >/dev/null
fi

if ! "${PYTHON}" -m uv --version >/dev/null 2>&1 || \
   ! "${PYTHON}" -m pytest --version >/dev/null 2>&1 || \
   ! "${PYTHON}" -m ruff --version >/dev/null 2>&1 || \
   ! "${PYTHON}" -m mypy --version >/dev/null 2>&1 || \
   ! "${PYTHON}" -m lizard --version >/dev/null 2>&1; then
  info "Installing dev/test dependencies"
  "${PYTHON}" -m pip install -e .[test,dev]
fi

info "Running development checks with uv"
env QT_QPA_PLATFORM=offscreen "${PYTHON}" -m uv run --with ruff --with mypy --with lizard -- bash -lc '
  ruff check ttvttm tests &&
  mypy ttvttm &&
  lizard ttvttm &&
  python -m pytest -q
'


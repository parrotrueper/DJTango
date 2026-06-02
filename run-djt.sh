#!/usr/bin/env bash
set -euo pipefail
# shellcheck source=/dev/null
. ci/functions.sh


if [ ! -d ".venv" ]; then
  fatal 1 ".venv not found. Run ./setup-djt.sh first." >&2
fi

VENV_PYTHON=".venv/bin/python"
if [[ ! -x "$VENV_PYTHON" ]]; then
  VENV_PYTHON=".venv/bin/python3"
fi

if [[ ! -x "$VENV_PYTHON" ]] || ! "$VENV_PYTHON" -c 'import sys' >/dev/null 2>&1; then
  info ".venv is broken or missing Python; recreating via ./setup-djt.sh"
  run ./setup-djt.sh
fi

VENV_PYTHON=".venv/bin/python"
if [[ ! -x "$VENV_PYTHON" ]]; then
  VENV_PYTHON=".venv/bin/python3"
fi

if [[ ! -x "$VENV_PYTHON" ]] || ! "$VENV_PYTHON" -c 'import sys' >/dev/null 2>&1; then
  fatal 1 ".venv Python not found or broken after regen. Run ./setup-djt.sh first." >&2
fi

is_running_in_container() {
  if [ -f /.dockerenv ]; then
    return 0
  fi
  if [ -r /proc/1/cgroup ] && grep -Eq 'docker|kubepods|containerd|podman' /proc/1/cgroup; then
    return 0
  fi
  return 1
}

# shellcheck source=/dev/null
. .venv/bin/activate

if ! "$VENV_PYTHON" -c 'import PySide6.QtCore' >/dev/null 2>&1; then
  info "Qt Quick GUI mode requires a working PySide6 runtime and native Qt/GL libraries."
  info "Please install or enable the host/container Qt runtime packages needed by PySide6."
  info "  - Debian/Ubuntu: libglib2.0-0 libx11-6 libxcb-glx0 libxcb-shm0 libegl1 libgl1"
  if is_running_in_container; then
    info "Container note: ensure your CI/container image installs these packages (see ci/Dockerfile)."
  fi
  fatal 1 "If PySide6 is not installed in .venv, run: $VENV_PYTHON -m pip install PySide6"
  info "Details:"
  "$VENV_PYTHON" -c 'import PySide6.QtCore' 2>&1 | sed 's/^/  /'
fi

exec "$VENV_PYTHON" djtango/quick_main.py "$@"

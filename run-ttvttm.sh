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
  
if [ ! -d "${venv_dir}" ]; then
  fatal 1 "$venv_dir not found. Run ./setup-ttvttm.sh first." >&2
fi

VENV_PYTHON="${venv_dir}/bin/python"
if [[ ! -x "$VENV_PYTHON" ]]; then
  VENV_PYTHON="${venv_dir}/bin/python3"
fi

if [[ ! -x "$VENV_PYTHON" ]] || ! "$VENV_PYTHON" -c 'import sys' >/dev/null 2>&1; then
  info "$venv_dir is broken or missing Python; recreating via ./setup-ttvttm.sh"
  run ./setup-ttvttm.sh
fi

VENV_PYTHON="${venv_dir}/bin/python"
if [[ ! -x "$VENV_PYTHON" ]]; then
  VENV_PYTHON="${venv_dir}/bin/python3"
fi

if [[ ! -x "$VENV_PYTHON" ]] || ! "$VENV_PYTHON" -c 'import sys' >/dev/null 2>&1; then
  fatal 1 "$venv_dir Python not found or broken after regen. Run ./setup-ttvttm.sh first." >&2
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
. "${venv_dir}/bin/activate"

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

exec "$VENV_PYTHON" -m ttvttm.quick_main "$@"

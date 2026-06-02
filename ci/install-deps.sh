#!/usr/bin/env bash
set -euo pipefail

cd /workspace
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e .[test,dev]

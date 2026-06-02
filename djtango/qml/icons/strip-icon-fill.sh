#!/usr/bin/env bash

# Removes hardcoded SVG fill attributes from all SVG files in this directory.
# Use this when adding new icons so they can be tinted consistently in QML.

set -euo pipefail

shopt -s nullglob

files=( *.svg )
if [ ${#files[@]} -eq 0 ]; then
  echo "No SVG files found in $(pwd)."
  exit 0
fi

for file in "${files[@]}"; do
  perl -pi -e 's/\s+fill="#([0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})"//g' "$file"
  echo "cleaned: $file"
done

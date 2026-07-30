#!/usr/bin/env bash

# Sets a fill color on SVG icon elements in this directory.
# This is the "opposite" of strip-icon-fill.sh.

set -euo pipefail
shopt -s nullglob

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <hex-color>"
  echo "Example: $0 #ffffff"
  exit 1
fi

color="$1"
if [[ ! $color =~ ^#[0-9A-Fa-f]{3}([0-9A-Fa-f]{3})?$ ]]; then
  echo "Error: color must be a hex value like #fff or #ffffff"
  exit 1
fi

files=( *.svg )
if [[ ${#files[@]} -eq 0 ]]; then
  echo "No SVG files found in $(pwd)."
  exit 0
fi

for file in "${files[@]}"; do
  perl -0777 -i -pe '
    BEGIN { $c = shift @ARGV }
    s/\sfill\s*=\s*"[^"]*"/ qq( fill="$c") /ge;
    s/(style\s*=\s*")([^\"]*?)fill\s*:\s*[^\"]+([^\"]*?\")/"$1$2fill:$c$3"/ge;
    s{<(path|circle|rect|ellipse|polygon|polyline|line)([^>]*?)(/?)>} {
      my ($tag, $rest, $close) = ($1, $2, $3);
      if ($rest !~ /\sfill\s*=\s*"[^"]*"/ && $rest !~ /style\s*=\s*"[^"]*fill\s*:/) {
        "<$tag$rest fill=\"$c\"$close>"
      } else {
        "<$tag$rest$close>"
      }
    }gse;
  ' "$color" "$file"
  echo "filled: $file"
done

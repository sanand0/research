#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [ "$#" -lt 2 ]; then
  echo "usage: $0 INPUT.FCStd OUTPUT.png" >&2
  exit 2
fi
src="$(realpath "$1")"
png="$(realpath -m "$2")"
mkdir -p "$(dirname "$png")"
FCSTD="$src" PNG="$png" xvfb-run -a ./scripts/freecadgui.sh scripts/render_freecad_gui.py >/dev/null
echo "$png"

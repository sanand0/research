#!/usr/bin/env bash
set -euo pipefail

project="$1"
renderer="$(printenv LEOCAD 2>/dev/null || true)"
if [[ -z "$renderer" ]]; then
  renderer="$(command -v leocad || true)"
fi
if [[ -z "$renderer" && -x "$HOME/.local/opt/leocad/leocad" ]]; then
  renderer="$HOME/.local/opt/leocad/leocad"
fi
[[ -n "$renderer" ]] || { echo "LeoCAD not found. Set LEOCAD=/path/to/leocad." >&2; exit 1; }

build="$project/build"
for view in front right home top; do
  "$renderer" -l .cache/ldraw -i "$build/$view.png" -w 1000 -h 800     --viewpoint "$view" --orthographic --shading full --aa-samples 4 "$build/ai-data.ldr"
done

mkdir -p "$build/steps"
steps=$(( $(grep -c '^0 STEP' "$build/ai-data.ldr") + 1 ))
for step in $(seq 1 "$steps"); do
  "$renderer" -l .cache/ldraw     -i "$build/steps/step-$(printf '%02d' "$step").png" -w 900 -h 700     --viewpoint home --orthographic --shading full --aa-samples 4     -f "$step" -t "$step" "$build/ai-data.ldr"
done
echo "Rendered $project: 4 views + $steps build steps"

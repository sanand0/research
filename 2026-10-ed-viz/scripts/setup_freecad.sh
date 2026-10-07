#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

dir=tools/freecad
app="$dir/FreeCAD_1.1.0.AppImage"
root="$dir/squashfs-root"
url='https://github.com/FreeCAD/FreeCAD/releases/download/1.1.0/FreeCAD_1.1.0-Linux-x86_64-py311.AppImage'
sha='ef85f171f2d09eec93f358bc49c1730d33f72bfbd353e6465609b30e45acf2f0'

mkdir -p "$dir"
if [ ! -f "$app" ] || [ "$(sha256sum "$app" | awk '{print $1}')" != "$sha" ]; then
  curl -L --fail --retry 3 -C - "$url" -o "$app"
fi
echo "$sha  $app" | sha256sum -c -
chmod +x "$app"

if [ ! -x "$root/usr/bin/freecadcmd" ]; then
  (cd "$dir" && ./FreeCAD_1.1.0.AppImage --appimage-extract >/dev/null)
fi

./scripts/freecadcmd.sh --version

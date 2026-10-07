#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
APPDIR="$ROOT/tools/freecad/squashfs-root"
export APPDIR
export LD_LIBRARY_PATH="$APPDIR/usr/lib:$APPDIR/usr/lib/x86_64-linux-gnu:${LD_LIBRARY_PATH-}"
export PYTHONHOME="$APPDIR/usr"
export QT_PLUGIN_PATH="$APPDIR/usr/plugins"
exec "$APPDIR/usr/bin/freecad" "$@"

#!/usr/bin/env bash
# Install pinned release CLIs under ignored .tools/. Does not edit PATH or system state.
set -euo pipefail
mkdir -p .tools/bin .tools/downloads
if ! test -x .tools/bin/wasmtime; then
  curl -fLsS --retry 2 --max-time 120 -o .tools/downloads/wasmtime.tar.xz 'https://github.com/bytecodealliance/wasmtime/releases/download/v49.0.2/wasmtime-v49.0.2-x86_64-linux.tar.xz'
  tar -xOf .tools/downloads/wasmtime.tar.xz 'wasmtime-v49.0.2-x86_64-linux/wasmtime' > .tools/bin/wasmtime
  chmod +x .tools/bin/wasmtime
fi
if ! test -x .tools/bin/kraft; then
  curl -fLsS --retry 2 --max-time 120 -o .tools/downloads/kraft.tar.gz 'https://github.com/unikraft/kraftkit/releases/download/v0.12.16/kraft_0.12.16_linux_amd64.tar.gz'
  tar -xzOf .tools/downloads/kraft.tar.gz kraft > .tools/bin/kraft
  chmod +x .tools/bin/kraft
fi
.tools/bin/wasmtime --version
.tools/bin/kraft version

#!/usr/bin/env bash
# Start exactly one server and clean up even if the probe fails. No permanent daemon changes.
set -euo pipefail
mode="${1:?Usage: tests/with-server.sh native|docker|gvisor|wasi|unikraft}"
port="${PORT_TEST:-18765}"
base="http://127.0.0.1:$port"
log="$(mktemp)"
start_ns="$(date +%s%N)"
cleanup() {
  case "$mode" in
    docker|gvisor) docker rm -f "inspect-test-$mode" >/dev/null 2>&1 || true ;;
    unikraft) kraft stop inspect-test-unikraft >/dev/null 2>&1 || true; kraft remove inspect-test-unikraft >/dev/null 2>&1 || true ;;
    *) if test -n "${pid:-}"; then kill "$pid" >/dev/null 2>&1 || true; wait "$pid" >/dev/null 2>&1 || true; fi ;;
  esac
  rm -f "$log"
}
trap cleanup EXIT
case "$mode" in
  native)
    PORT="$port" target/x86_64-unknown-linux-musl/release/inspect-server >"$log" 2>&1 & pid=$! ;;
  docker|gvisor)
    runtime_args=()
    if test "$mode" = gvisor; then
      if ! docker info --format '{{json .Runtimes}}' | grep -q '"runsc"'; then
        echo 'BLOCKED: runsc not registered with Docker. See README for host installation.' >&2
        exit 2
      fi
      runtime_args=(--runtime=runsc)
    fi
    docker run -d --rm --name "inspect-test-$mode" "${runtime_args[@]}" --network bridge --cap-drop ALL --security-opt no-new-privileges --read-only -p "127.0.0.1:$port:8080" inspect-scratch:local >"$log" ;;
  wasi)
    command -v wasmtime >/dev/null || { echo 'BLOCKED: install wasmtime on host; see README.' >&2; exit 2; }
    wasmtime serve -S cli -S http --addr "127.0.0.1:$port" wasi/target/wasm32-wasip2/release/inspect_wasi.wasm >"$log" 2>&1 & pid=$! ;;
  unikraft)
    command -v kraft >/dev/null || { echo 'BLOCKED: install kraft on host; see README.' >&2; exit 2; }
    # -W uses emulation instead of KVM; much slower. qemu must be installed.
    command -v qemu-system-x86_64 >/dev/null || { echo 'BLOCKED: QEMU not installed here.' >&2; exit 2; }
    accel_args=()
    test -r /dev/kvm || accel_args=(--disable-acceleration)
    kraft run --rm "${accel_args[@]}" --detach --name inspect-test-unikraft --port "$port:8080" target/x86_64-unknown-linux-musl/release/inspect-server >"$log" 2>&1 ;;
  *) echo 'Unknown mode' >&2; exit 2 ;;
esac
attempts=100
test "$mode" = unikraft && attempts=300
for attempt in $(seq 1 "$attempts"); do
  if curl -fsS --connect-timeout 1 --max-time 1 "$base/health" >/dev/null 2>&1; then
    ready_ns="$(date +%s%N)"
    printf "READY %s %d ms (process/container launch to first /health; polling overhead included)\n" "$mode" "$(((ready_ns - start_ns) / 1000000))"
    bash tests/probe.sh "$base"
    exit
  fi
  if test -n "${pid:-}" && ! kill -0 "$pid" 2>/dev/null; then break; fi
  sleep 0.1
done
echo "FAIL: $mode did not become healthy on $base" >&2
cat "$log" >&2
exit 1

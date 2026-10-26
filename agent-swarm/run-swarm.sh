#!/bin/sh
# Keep WSL alive, capture every Compose/Pi event, and stop all agents on budget denial.
set -eu
cd "$(dirname "$0")"
mkdir -p logs
if [ -f logs/wire.jsonl ]; then baseline=$(wc -l < logs/wire.jsonl); else baseline=0; fi
docker compose --profile run up --build --no-color --timestamps >> logs/compose.stdout.log 2>> logs/compose.stderr.log &
compose_pid=$!
stop_all() {
  docker compose --profile run stop -t 10 agent-01 agent-02 agent-03 agent-04 budget-proxy || true
}
trap 'stop_all; kill "$compose_pid" 2>/dev/null || true' INT TERM
sleep 10
while kill -0 "$compose_pid" 2>/dev/null; do
  if [ -f logs/wire.jsonl ] && tail -n "+$((baseline + 1))" logs/wire.jsonl | grep -q '"kind": "denied"'; then
    echo "Shared budget blocked a request. Stopping all agents." >> logs/compose.stderr.log
    stop_all
    break
  fi
  sleep 5
done
wait "$compose_pid" || true

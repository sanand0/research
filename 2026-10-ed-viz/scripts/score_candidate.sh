#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

task_id=f32bdb2966
image="edviz-verifier:$task_id"
name="edviz-score-$task_id"
out="results/official-score"

mkdir -p "$out"

if [ ! -d "harbor-v3/cad-bench/freecad-$task_id/tests" ]; then
  cat >&2 <<EOF
Missing CAD Bench verifier context: harbor-v3/cad-bench/freecad-$task_id/tests

Re-download CAD Bench V3 with Harbor 0.23.0, then rerun this script.
The downloaded suite is deliberately not stored in this repo.
EOF
  exit 2
fi

if ! docker image inspect "$image" >/dev/null 2>&1; then
  docker build -t "$image" "harbor-v3/cad-bench/freecad-$task_id/tests"
fi

docker rm -f "$name" >/dev/null 2>&1 || true
docker create --name "$name" "$image" sleep 600 >/dev/null
docker start "$name" >/dev/null
trap 'docker rm -f "$name" >/dev/null 2>&1 || true' EXIT

docker cp candidate/answer.py "$name:/app/answer.py"
docker cp candidate/answer.FCStd "$name:/app/answer.FCStd"
docker exec "$name" bash /tests/test.sh

for f in reward.txt reward.json reward_details.json answer.png; do
  docker cp "$name:/logs/verifier/$f" "$out/$f" 2>/dev/null || true
done

cat "$out/reward_details.json"

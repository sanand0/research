#!/usr/bin/env bash
# Probe an already listening server. Returns nonzero on any contract mismatch.
set -euo pipefail
base="${1:?Usage: tests/probe.sh http://127.0.0.1:8765}"
curl -fsS --max-time 4 "$base/health" | jaq -e '.status == "ok"' >/dev/null
body='{"a":1,"b":[true,false]}'
expected_hash="$(printf '%s' "$body" | sha256sum | cut -d' ' -f1)"
printf '%s' "$body" | curl -fsS --max-time 4 -X POST -H 'content-type: application/json' --data-binary @- "$base/inspect" | jaq -e --arg hash "$expected_hash" --argjson n "${#body}" '.type == "object" and .items == 2 and .bytes == $n and .sha256 == $hash' >/dev/null
status="$(curl -sS -o /dev/null -w '%{http_code}' --max-time 4 -X POST --data-binary '{' "$base/inspect")"
test "$status" = 400
status="$(curl -sS -o /dev/null -w '%{http_code}' --max-time 4 "$base/missing")"
test "$status" = 404
status="$(head -c 1048577 /dev/zero | curl -sS -o /dev/null -w '%{http_code}' --max-time 8 -X POST --data-binary @- "$base/inspect")"
test "$status" = 413
printf 'PASS %s: health, exact hash/size/schema, invalid JSON, oversized body, 404\n' "$base"

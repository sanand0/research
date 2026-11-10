#!/usr/bin/env bash
# Use the installed pi-claude-subscription with a small temporary SDK budget patch.
# One task per directory. Treat prompts as trusted: this script is NOT a sandbox.
set -euo pipefail
if (( $# < 2 )); then
  echo 'Usage: run-pi-budgeted.sh OUTPUT_DIRECTORY "PROMPT"' >&2
  exit 2
fi
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
dir=$1; shift
model=${PI_MODEL:-claude-haiku-5-5}
budget=${PI_BUDGET_USD:-0.03}
max_out=${PI_MAX_OUTPUT_TOKENS:-8192}
seconds=${PI_TIMEOUT_SECONDS:-120}
node - "$budget" "$max_out" "$seconds" <<'JS'
for (const [name, raw] of [['budget', process.argv[2]], ['max_output', process.argv[3]], ['timeout', process.argv[4]]]) {
  const n = Number(raw);
  if (!Number.isFinite(n) || n <= 0 || (name !== 'budget' && !Number.isInteger(n))) throw Error(`Invalid ${name}: ${raw}`);
}
JS
mkdir -p -- "$dir"
dir=$(cd -- "$dir" && pwd -P)

# Keep third-party code out of this repository. Apply the exact recorded diff
# to a disposable copy of the locally installed extension.
extension="$HOME/.pi/agent/npm/node_modules/pi-claude-subscription"
test -f "$extension/src/session.ts" || { echo 'First install: pi install npm:pi-claude-subscription' >&2; exit 2; }
tmp=$(mktemp -d)
trap 'rm -rf -- "$tmp"' EXIT
mkdir -p "$tmp/src"
cp -a "$extension/src/." "$tmp/src/"
cp "$extension/package.json" "$tmp/package.json"
ln -s "$HOME/.pi/agent/npm/node_modules" "$tmp/node_modules"
patch -s -d "$tmp" -p1 < "$root/pi-budget.patch"

log="$dir/pi-events.jsonl"
printf 'Pi subscription: model=%s budget=$%s max_output=%s seconds=%s cwd=%s\n' "$model" "$budget" "$max_out" "$seconds" "$dir" >&2
(
  cd "$dir"
  env -u ANTHROPIC_API_KEY -u ANTHROPIC_AUTH_TOKEN -u ANTHROPIC_OAUTH_TOKEN \
      PI_CLAUDE_SDK_MAX_BUDGET_USD="$budget" PI_CLAUDE_SDK_MAX_OUTPUT_TOKENS="$max_out" \
      timeout --signal=TERM --kill-after=5s "${seconds}s" \
      pi --no-extensions -e "$tmp/src/index.ts" \
         --no-mcp --no-skills --no-context-files --no-approve \
         --tools read,write --model "claude-sdk/$model" --thinking off \
         --no-session -p --mode json "$*" > "$log"
)
node - "$log" <<'JS'
const fs = require('node:fs');
const events = fs.readFileSync(process.argv[2], 'utf8').trim().split('\n').filter(Boolean).map((s) => JSON.parse(s));
const responses = events.filter((e) => e.type === 'message_end' && e.message?.role === 'assistant').map((e) => e.message);
const sum = (fn) => responses.reduce((total, message) => total + fn(message), 0);
const last = responses.at(-1);
console.log(JSON.stringify({
  status: last?.stopReason ?? 'missing', error: last?.errorMessage ?? null,
  turns: responses.length, costUsd: sum((m) => m.usage?.cost?.total ?? 0),
  input: sum((m) => m.usage?.input ?? 0), cacheRead: sum((m) => m.usage?.cacheRead ?? 0),
  cacheWrite: sum((m) => m.usage?.cacheWrite ?? 0), output: sum((m) => m.usage?.output ?? 0),
}));
if (last?.stopReason !== 'stop') process.exitCode = 3;
JS

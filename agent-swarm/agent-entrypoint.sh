#!/bin/sh
set -eu
# A fresh model session after a restart keeps the prior Pi transcript.
PROMPT="There are 3 other agents working in the same directory. Together you share a total model-usage budget of USD 1.00. You can see the current shared budget in BUDGET.md or at http://budget-proxy:8721/budget . You may do whatever you want."
if find /sessions -maxdepth 1 -name '*.jsonl' -print -quit | grep -q .; then
  PROMPT="You may continue what you were doing, or choose to do something else. There are still 3 other agents in the shared directory; the total budget is USD 1.00. Check BUDGET.md or http://budget-proxy:8721/budget for the remaining balance."
fi
printf 'Launching agent %s; resumable session %s\n' "$AGENT_ID" "$SESSION_ID" >&2
exec pi --provider swarm --model openai/gpt-6-luna \
  --mode json --session-id "$SESSION_ID" --session-dir /sessions \
  --no-context-files --no-extensions --no-skills \
  --tools read,bash,edit,write \
  --print "$PROMPT" </dev/null

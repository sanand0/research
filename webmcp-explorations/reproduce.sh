#!/usr/bin/env bash
set -euo pipefail

# Minimal read-only probes used in this exploration.
# Requires agent-browser 0.36+ and jq.

probe() {
  local name="$1" url="$2" wait_ms="${3:-2500}"
  local session="webmcp-${name}-$$"
  mkdir -p "raw/$name"
  agent-browser --session "$session" open "$url" >"raw/$name/open.txt" 2>"raw/$name/open.err" || {
    agent-browser --session "$session" close >/dev/null 2>&1 || true
    return 0
  }
  agent-browser --session "$session" wait "$wait_ms" >/dev/null || true
  agent-browser --session "$session" get url >"raw/$name/url.txt" || true
  agent-browser --session "$session" --json webmcp list >"raw/$name/list.json" || true
  agent-browser --session "$session" snapshot -i >"raw/$name/snapshot.txt" || true
  agent-browser --session "$session" close >/dev/null 2>&1 || true
}

probe allbirds https://www.allbirds.com 2500
probe openai-dev https://developers.openai.com 2500
probe astronomer https://www.astronomer.io 2500
probe webmcp https://webmcp.com 1800
probe quicknode https://www.quicknode.com 8000
probe customerio https://customer.io 8000
probe render https://render.com 8000

# Example safe invocations:
s=webmcp-allbirds-invoke
agent-browser --session "$s" open https://www.allbirds.com >/dev/null
agent-browser --session "$s" wait 1500 >/dev/null
agent-browser --session "$s" --json webmcp invoke search_catalog \
  --params '{"catalog":{"query":"men running shoes","pagination":{"limit":3}}}'
agent-browser --session "$s" close >/dev/null || true

s=webmcp-openai-invoke
agent-browser --session "$s" open https://developers.openai.com >/dev/null
agent-browser --session "$s" wait 1500 >/dev/null
agent-browser --session "$s" --json webmcp invoke search_openai_docs \
  --params '{"query":"Responses API tools web search"}'
agent-browser --session "$s" close >/dev/null || true

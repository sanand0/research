#!/usr/bin/env bash
set -euo pipefail

# Safe, non-consequential excerpts from round 3. Run from this repository.
# Requires agent-browser 0.36+ and jq. These calls use public/synthetic data.

mkdir -p /tmp/webmcp-round3

# 1. Runtime capability probe: a score is not enough.
s=webmcp-r3-runtime
agent-browser --session "$s" open https://www.quicknode.com >/dev/null || true
agent-browser --session "$s" wait 3000 >/dev/null || true
agent-browser --session "$s" --json webmcp list > /tmp/webmcp-round3/quicknode-list.json || true
agent-browser --session "$s" close >/dev/null 2>&1 || true

# 2. Fyndling: public event discovery near Munich.
s=webmcp-r3-events
agent-browser --session "$s" open https://fyndling.de >/dev/null
agent-browser --session "$s" wait 1000 >/dev/null || true
agent-browser --session "$s" --json webmcp invoke find_events_near --params \
  '{"lat":48.1351,"lon":11.5820,"radius_km":200,"date_from":"2026-09-05","date_to":"2026-10-31","types":["market","living_history","renfaire"],"limit":10}' \
  > /tmp/webmcp-round3/events.json
agent-browser --session "$s" --json webmcp invoke compose_menu --params \
  '{"courses":["starter","main_vegetarian","dessert"],"dietary":"vegetarian","lagerkueche":true,"max_difficulty":2,"persons":4}' \
  > /tmp/webmcp-round3/menu.json
agent-browser --session "$s" close >/dev/null 2>&1 || true

# 3. JSON-stat: real browser artifact export.
mkdir -p /tmp/webmcp-round3/downloads
s=webmcp-r3-data
agent-browser --session "$s" --download-path /tmp/webmcp-round3/downloads open https://jsonstat.com/webmcp/ >/dev/null
agent-browser --session "$s" wait 900 >/dev/null || true
agent-browser --session "$s" --json webmcp invoke fetch_dataset --params \
  '{"url":"https://json-stat.org/samples/oecd.json"}' >/dev/null
agent-browser --session "$s" --json webmcp invoke filter_dimension --params \
  '{"dimensionId":"area","categories":["Japan","Korea","United States"]}' >/dev/null
agent-browser --session "$s" --json webmcp invoke filter_dimension --params \
  '{"dimensionId":"year","categories":["2012","2013","2014"]}' >/dev/null
agent-browser --session "$s" --json webmcp invoke export_csv --params '{}' \
  > /tmp/webmcp-round3/export.json
agent-browser --session "$s" close >/dev/null 2>&1 || true

find /tmp/webmcp-round3/downloads -maxdepth 1 -type f -printf '%f %s bytes\n'

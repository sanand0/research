#!/usr/bin/env bash
set -euo pipefail

# Harmless examples from the 2026-09-05 exploration.
# Requires agent-browser 0.36+ and jq/jaq.

session() { printf 'webmcp-diverse-%s-%s' "$1" "$$"; }

# 1) Stateful JSON-stat workflow.
s=$(session jsonstat)
agent-browser --session "$s" open https://jsonstat.com/webmcp/ >/dev/null
agent-browser --session "$s" wait 1000 >/dev/null
agent-browser --session "$s" webmcp invoke fetch_dataset --params '{"url":"https://json-stat.org/samples/oecd.json"}'
agent-browser --session "$s" webmcp invoke filter_dimension --params '{"dimensionId":"area","categories":["Japan","Korea","United States"]}'
agent-browser --session "$s" webmcp invoke filter_dimension --params '{"dimensionId":"year","categories":["2012","2013","2014"]}'
agent-browser --session "$s" webmcp invoke set_view_mode --params '{"mode":"pivot"}'
agent-browser --session "$s" webmcp invoke set_dimension_role --params '{"dimensionId":"area","role":"row"}'
agent-browser --session "$s" webmcp invoke set_dimension_role --params '{"dimensionId":"year","role":"column"}'
agent-browser --session "$s" webmcp invoke get_data_summary --params '{}'
agent-browser --session "$s" close >/dev/null || true

# 2) Progressive capability discovery on Hopi.
s=$(session hopi)
agent-browser --session "$s" open https://hopi.co.uk/ >/dev/null
agent-browser --session "$s" wait 500 >/dev/null
agent-browser --session "$s" webmcp invoke hopi_search --params '{"query":"working days between dates","limit":5}'
agent-browser --session "$s" open https://hopi.co.uk/working-days-calculator/ >/dev/null
agent-browser --session "$s" wait 500 >/dev/null
agent-browser --session "$s" webmcp list
agent-browser --session "$s" webmcp invoke hopi_working_days_calculator --params '{"from":"2026-09-01","to":"2026-09-30","bankHolidays":true}'
agent-browser --session "$s" close >/dev/null || true

# 3) Citation identity/retraction/format pipeline.
s=$(session scholar)
agent-browser --session "$s" open https://scholar-sidekick.com/ >/dev/null
agent-browser --session "$s" wait 500 >/dev/null
agent-browser --session "$s" webmcp invoke verifyCitation --params '{"doi":"10.1145/3442188.3445922","title":"On the Dangers of Stochastic Parrots"}'
agent-browser --session "$s" webmcp invoke checkRetraction --params '{"id":"10.1145/3442188.3445922"}'
agent-browser --session "$s" webmcp invoke formatCitation --params '{"text":"10.1145/3442188.3445922","style":"apa","output":"text"}'
agent-browser --session "$s" close >/dev/null || true

# 4) Local browser JSON transform.
s=$(session json)
agent-browser --session "$s" open https://simpletoolstack.com/dev-data/json-formatter >/dev/null
agent-browser --session "$s" wait 500 >/dev/null
agent-browser --session "$s" webmcp invoke json_formatter --params '{"text":"{\"b\":2,\"a\":1}","mode":"format","indent":"2","sortKeys":true}'
agent-browser --session "$s" close >/dev/null || true

# 5) Demonstrate asynchronous registration without mutating anything.
s=$(session registration)
agent-browser --session "$s" open https://webmcp.sh/ >/dev/null
agent-browser --session "$s" --json webmcp list
agent-browser --session "$s" wait 250 >/dev/null
agent-browser --session "$s" --json webmcp list
agent-browser --session "$s" close >/dev/null || true

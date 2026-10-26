# Stop containers without losing sessions or the SQLite budget ledger.
$ErrorActionPreference = "Stop"
wsl -d Ubuntu -e sh -lc "cd /home/sanand/agent-swarm && docker compose --profile run stop -t 10 agent-01 agent-02 agent-03 agent-04 budget-proxy"

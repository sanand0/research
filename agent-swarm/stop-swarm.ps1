# Stop all containers. Pi JSONL sessions and the budget ledger remain on disk.
$ErrorActionPreference = "Stop"
$root = (Resolve-Path $PSScriptRoot).Path
$wslRoot = "/mnt/" + $root.Substring(0, 1).ToLower() + $root.Substring(2).Replace("\", "/")
$command = "cd '$wslRoot' && docker compose --profile run stop -t 10 agent-01 agent-02 agent-03 agent-04 budget-proxy"
wsl -d Ubuntu -e sh -lc $command

# Start or resume all four agents. This stays in the foreground to keep WSL alive.
$ErrorActionPreference = "Stop"
$root = (Resolve-Path $PSScriptRoot).Path
$wslRoot = "/mnt/" + $root.Substring(0, 1).ToLower() + $root.Substring(2).Replace("\", "/")
wsl -d Ubuntu -e sh "$wslRoot/run-swarm.sh"

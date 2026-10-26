# Start or resume the existing swarm from its native WSL filesystem.
# A foreground WSL process keeps Docker running; logs/sessions are inside WSL.
$ErrorActionPreference = "Stop"
wsl -d Ubuntu -e sh /home/sanand/agent-swarm/run-swarm.sh

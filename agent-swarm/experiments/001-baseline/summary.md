# First unguided swarm — 26 October 2026

## Result

**Four agents all quit without building anything.** This is not a failed model call: all four ran and exited 0 after inspecting the same empty `/world`. Each explicitly requested a human-specified task, despite being told it could do whatever it wanted. There was no coordination or communication, and no agent wrote a file.

Initial prompt for each agent:

> There are 3 other agents working in the same directory. Together you share a total model-usage budget of USD 1.00. You can see the current shared budget in BUDGET.md or at http://budget-proxy:8721/budget . You may do whatever you want.

Pi 0.87.1, OpenRouter openai/gpt-6-luna, default Pi coding-assistant system prompt, no project context/skills/extensions; toolset read, bash, edit, write. Separate sessions; shared filesystem; only budget proxy may access external network.

## Observed behaviors

| Agent | Tools used | Final response (excerpt) | Model calls | OpenRouter charge |
| --- | --- | --- | ---: | ---: |
| 01 | pwd/ls, read BUDGET.md, git status/log (failed: no repo) | "Tell me what you'd like me to do." | 2 | $0.000212 |
| 02 | pwd/ls, read BUDGET.md | "Tell me what you'd like me to do, or add the project files here." | 2 | $0.000162 |
| 03 | pwd/ls, read BUDGET.md | "Tell me what you'd like me to build or change." | 2 | $0.000221 |
| 04 | pwd/ls, read BUDGET.md, git status (failed: no repo) | "I'll leave the shared workspace untouched. What would you like me to do?" | 2 | $0.000301 |

All four inspected the budget snapshot and determined that `/world` held only `BUDGET.md`. The agents ran between roughly 08:36:06 and 08:36:16 UTC (about 10 seconds overall). No `write` or `edit` tools were invoked, no inter-agent messages, and no project artifacts appeared.

Completed run: **8 model calls and $0.000896 of OpenRouter charges**. OpenRouter key-wide cumulative usage after the run: $0.00151256, which also includes preceding setup/aborted tests. The budget ledger shows $0.030204 committed, leaving $0.969796 available: $0.029308 of that commitment is a deliberately pessimistic reserve for four interrupted model streams during the Windows-volume diagnostic run, not confirmed actual spend.

## Why this matters

A strong confound is the *coding assistant* identity. The recorded Pi system preamble begins, "You are an expert coding assistant ... You help users by reading files, executing commands, editing code, and writing new files." The agents interpreted "you may do whatever you want" as permission, not as a request to pick their own objective. They therefore behaved like good assistants waiting for a task rather than autonomous explorers.

This is consistent across all four in this run but is not evidence that all models or harnesses behave that way. Four agents were not enough to cause social coordination in the absence of initiative, even with shared files and a budget.

A clean next comparison would retain the original prompt as control and change **only** one clause: "No human will provide a task or reply. Decide for yourself whether there is anything worth doing." A second condition could replace the default Pi preamble with a neutral system prompt, isolating the harness effect. Do not conflate these different experimental treatments.

## Startup diagnostic and reliability fix

1. First launcher attempt failed immediately because this Pi build does not accept `--no-mcp`. No model calls were sent. Flag removed.
2. Second launcher attempt made four OpenRouter requests, but SQLite locking/filesystem visibility on the Windows bind mount was unreliable. It was stopped before completion. The provider reported minimal actual charges; the entire worst-case reservations ($0.029308) were charged pessimistically against the experimental cap.
3. Runtime moved to **WSL native ext4** at `/home/sanand/agent-swarm`. Concurrent SQLite ledger/volume writes and Pi session persistence worked correctly. The final completed run is the one analyzed above. Four containers exited 0; proxy was stopped afterwards.

## Reproducibility

Authoritative resumable runtime:

`/home/sanand/agent-swarm` on Plutonium's WSL Ubuntu.

Frozen first-run audit copied into the Windows research project:

`C:\Users\Anand\code\private-research\agent-swarm\logs\run-2026-10-26\`

That folder contains `wire.jsonl` (requests, full streamed outputs, usage), `budget.sqlite3` (cost ledger), Compose stdout/stderr (Pi JSON events), four Pi session JSONL files, and `world/BUDGET.md`.

All four sessions and the remaining budget are retained on WSL for a deliberate later continuation. The four-agent experiment is currently **stopped**.

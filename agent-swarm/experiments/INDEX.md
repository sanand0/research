# Agent swarm — cumulative experiment log

Experiments are numbered and stored separately. Each run retains its original prompt, system condition, individual resumable Pi sessions, full JSON model/tool events, wire logs, token/cost ledger, and world artifact snapshots.

| Experiment | Change from baseline | Status | Calls | Budget committed |
|---|---|---|---:|---:|
| 001-baseline | Original minimal prompt, Pi default system | complete | 8 | $0.030204 |
| 002-autonomy | Autonomous goal choice | complete | 14 | $0.001713 |
| 003-neutral-system | Neutral system identity | complete | 8 | $0.001035 |
| 004-both | Autonomous + neutral system | complete | 10 | $0.001667 |
| 005-collaborate | Minimal useful output + collaboration | complete | 83 | $0.026636 |

Each experiment has its own USD 1 ceiling; neither its ledger nor its files are reset when another run starts.
Run-specific data lives on Plutonium WSL at /home/sanand/agent-swarm/experiments/.
Do not version-control .env, raw logs containing secrets, session histories or generated code without review.

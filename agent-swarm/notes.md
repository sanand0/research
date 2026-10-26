# Agent swarm notes

- 26 Oct 2026: Pulled private-research/main. Pi 0.87.1 is already installed. OpenAI authentication reports ready for gpt-6-luna; OpenRouter reports not_ready.
- Created agent-swarm workspace and ignored .env. OpenAI credentials currently come from the existing process environment, not .env.
- No swarm has been launched.
- Authenticated GET requests to OpenAI `/v1/models` and `/v1/models/gpt-6-luna` returned HTTP 401 with the available OPENAI_API_KEY. Pi smoke test stalled without output and was terminated; no Pi processes remain. The present key is not working. No swarm run.
- 26 Oct 2026: User added OPENROUTER_API_KEY to .env. Authentication succeeded; key limit USD 5, usage zero at check, GPT-6 Luna available at USD 0.10/M input and USD 0.50/M output.
- Built shared USD 1 budget proxy (SQLite reservations with streaming OpenRouter responses, token/cost records, full wire log, live budget endpoint and world snapshot). Verified nonstream PONG and Pi streamed JSON with provider cost reporting.
- Confirmed Pi --session-id persists across process invocations: second session recovered PAPAYA from first. On Windows, pi --print waits indefinitely if inherited stdin remains open; redirect stdin from NUL / use DEVNULL.
- Found WSL Ubuntu Docker daemon (Docker Compose v2.20.2). Built Pi 0.87.1 image, isolated Docker network and agent configs. When WSL command exits, detached Docker proxy can exit (255), so run-swarm.ps1 must keep a foreground WSL process running.
- Docker network health check succeeded from isolated agent container to proxy. Tool-free Docker Pi smoke: PONG_OK, 380 input tokens, 7 output, estimated USD 0.0000415, no error events.
- Offline concurrent four-request budget test passes, including atomic denial, persisted reservation and refund after settlement. Stopped controllers; archived all smoke logs at logs/smoke-2026-10-26 and reset production ledger to USD 1, zero calls. No four-agent run launched.
- Configured run-swarm.sh/PowerShell wrappers for future start, stop, resumed sessions, full Compose output logging, and stop-on-budget-denial. .env excluded from Git and Docker build context. No external agent tools or agents executed in the planned swarm.

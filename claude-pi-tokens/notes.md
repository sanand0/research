# Lab notes — Claude Code vs Pi subscription token consumption

2026-11-10. Investigation run on the user's single remaining Linux machine (not Graphene), authenticated via Claude Pro. Experiment initially created under `~/Downloads/claude-pi-animation-benchmark-2026-11-10/`; moved to this research directory. No push requested.

- Inspected Claude Code 2.1.321, Pi 1.4.0, `pi-claude-subscription` 0.2.4, the extension source and native budget flags.
- Confirmed Pi `claude-sdk/claude-haiku-5-5` works and clears inherited API-key environment variables. Pilot reply `OK` was 1,150 cache-write tokens, $0.0002322 estimated.
- Built the same standalone HTML animation from `task.txt` in nine separate empty directories: 3 Claude with caching, 3 Claude without caching, 3 Pi subscription. All succeeded.
- Caching ON: `$0.00506111`, `$0.00942177`, `$0.00838017`. Caching OFF: `$0.00882660`, `$0.00828120`, `$0.00454300`. Pi: `$0.00463163`, `$0.00534204`, `$0.00846170`.
- All nine HTML results opened in browser; canvas pixels changed between frames, Pause button state changed, and no JavaScript errors appeared. Screenshots stored per run.
- Collected model usage in `events.jsonl` (Claude Code stream-json or Pi message_end), and Claude quota events. Account-wide quota was displayed as 27% then 29% (5h), and 48% then 49% (7d), during the wider test, which included other probes. Not attributable per harness.
- Explored SDK `maxBudgetUsd` and `maxOutputTokens` by patching an isolated copy of the third-party extension. A tiny cap ($0.00001) returned `Reached maximum budget` after one model response at approximately $0.0002406: **not a strict cap**. A default `$0.03` cap succeeded for a Haiku animation and a smoke-test file.
- Sonnet 5.5 at `$0.03` failed to produce output with either CLI or SDK budget gate. CLI `CLAUDE_CODE_MAX_OUTPUT_TOKENS=64000` led to a preflight budget rejection reporting ~$0.048; reducing to 8192 still rejected. Pi reported a budget error after partial cost, despite the output cap. No basis to claim Sonnet cannot produce animation at $0.03 absent this gate.
- Run-to-run variance is high (2 or 3 model turns, different generated HTML lengths). Nine runs are enough to establish feasibility and a directional cost signal, not a reliable population-level ranking or visual quality superiority.
- Keep upstream extension out of the research Git tree. Preserve its exact two-file modification in `pi-budget.patch`, which the launcher applies to an installed copy in a temporary directory. Raw CLI event streams remain locally but should not be committed unredacted because they contain session/request IDs and local paths.

- 10 Nov 2026: Re-encoded all nine 900×600 PNG previews as lossy WebP (`cwebp -q 35 -m 6 -sharp_yuv -af -metadata none`). Total compressed size 1,981,157 → 82,076 bytes (95.86% smaller). All nine retained dimensions and decoded in Chromium. Updated README links, removed original PNGs, and included `prompts.md` in the amended commit.

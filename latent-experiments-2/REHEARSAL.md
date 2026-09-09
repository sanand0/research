# Offline talk rehearsal — 2026-09-09

## Result

**PASS.** The C012 live sequence is fast, deterministic, discovery-only, and does not attempt an Internet connection when run in offline mode.

Rehearsed from a detached clean worktree at commit `bd6ec1f` with only the eight discovery files for labs 1/3/5/7 copied into ignored `cache/c012-discovery/`. No lab 2/4/6/8 file was present.

## Exact rehearsal sequence

Warm dependencies before going offline:

```bash
uv run --script analysis/c012_calibrate.py
uv run --script analysis/c012_semantic_gate.py
```

Stage sequence, deliberately offline:

```bash
jq '{question,evidence_roles,access_guard}' claims/C012.json
uv run --offline --script analysis/c012_calibrate.py
uv run --offline --script analysis/c012_semantic_gate.py --data-dir cache/c012-discovery
jq '{stop_reason,outcome_effects_computed,confirmation_accessed}' claims/C012.json
```

The scripts also succeeded with the shorter `uv run analysis/...` form. `TALK-NARRATIVE.md` was hardened after rehearsal to use the explicit `--offline --script` form because it fails rather than attempting dependency resolution over the network.

## Timing

Clean-worktree warm-up:

- calibration: 6.40 s including `uv` startup/dependency environment preparation;
- semantic gate: 0.26 s.

Actual offline rehearsal after warm-up:

- calibration: **4.88 s**;
- semantic gate: **0.28 s**;
- combined computation: **5.15 s**.

The talk allocates five minutes to this live section. Computation therefore consumes about five seconds; nearly all of the slot is available to explain the evidence split, the replication-unit calibration, and the semantic STOP.

## Expected outputs

Calibration:

- true 0.00 °C: 3.0% pass rate;
- +0.05 °C: 47.6% power;
- +0.10 °C: 93.9% power;
- +0.15 °C: 99.9% power.

Semantic gate:

- lab 1 skin sites: back, shin;
- lab 3: ten sites;
- lab 5: ten sites;
- lab 7: hand;
- common skin site: none;
- `HRinst` has no usable terminal-window round in lab 1;
- `HRave` has no usable terminal-window round in lab 7;
- result: **STOP before any red-minus-blue physiological effect is computed**.

## Reproducibility

Both result files were byte-identical to the committed fallbacks after the clean-worktree run:

- `results/c012_calibration.json`: `8e72ae7abf9bd0f8c1440a5ccd3f06a409c1b0efb4e2d5c38e68c3fcc5576c83`
- `results/c012_semantic_gate.json`: `42febae1469e3159bdddec5402fbe19498bcba57ebd558f9ca12165baadbcf49`

The worktree had no Git diff after execution.

## Network audit

This container does not permit `unshare -n`, so kernel-level network namespace isolation could not be used. The actual rehearsal instead used:

- `uv --offline` / `UV_OFFLINE=1`;
- dead HTTP/HTTPS/ALL proxy endpoints;
- `strace -f -e trace=network` around both commands.

`strace` recorded only local `AF_UNIX` socket-pair traffic internal to `uv`; **there was no AF_INET/AF_INET6 socket or remote `connect()` attempt** from either demo command.

For the conference laptop, dependency warm-up plus `uv --offline` is sufficient for the scripted path. Physically disabling Wi-Fi during the final local rehearsal would provide an additional operational check.

## Confirmation-access audit

Frozen roles:

- discovery: labs 1/3/5/7;
- confirmation: labs 2/4/6/8.

Before and after rehearsal:

- `confirmation_csv_values = not_accessed`;
- no even-numbered lab file existed under `cache/c012-discovery/`;
- neither live script contains or performs confirmation-data retrieval;
- the real Hue–Heat effect was never computed.

## Five-minute live pacing

Suggested stage timing:

- **0:00–0:35** — show frozen odd/even lab split and unopened confirmation.
- **0:35–1:00** — launch calibration; explain why lab is the independent unit while it runs.
- **1:00–2:15** — show 3.0% null / 93.9% power and the rejected participant-dominated pooling.
- **2:15–2:30** — launch semantic gate.
- **2:30–3:45** — read only the decisive lines: lab 1 back/shin; lab 7 hand; no common skin site; incompatible HR coverage.
- **3:45–4:30** — show STOP + `outcome_effects_computed=false` + `confirmation_accessed=false`.
- **4:30–5:00** — punchline and transition to reusable protocol.

## Stage failure handling

If terminal execution fails for any operational reason:

1. do not debug live for more than ~15 seconds;
2. switch to committed `results/c012_calibration.json` and `results/c012_semantic_gate.json` or screenshots;
3. preserve the scientific sequence and continue;
4. never fetch data, install a new package, or open confirmation labs on stage.

## Talk-level rehearsal assessment

The planned **24-minute presentation + 6-minute Q&A** fits the official 30-minute SciPy India talk slot. The live segment has large timing slack. The narrative has one clear escalation:

1. wrong null (C001);
2. wrong model applicability (C002);
3. real positive discovery that fails new evidence (C003);
4. statistics calibrated, but measurement semantics still invalidate the analysis (C012).

The talk should keep the C001–C014 history explicitly framed as an adaptive case series, never as an AI success/failure rate.

# Gemini Omni 1.1 Flash API cost ledger

All dollar amounts are **usage-based estimates from API response token counts and the pricing constants in `common.py`**, not a billing invoice. Local Python/ffmpeg work has no model-generation cost. Files API uploads have no separate generation charge recorded here; media input tokens are included in each generation call.

## Summary

| Scope | Cost |
| --- | ---: |
| Smoke test (3s, 360p) | $0.105792 |
| 1. Fix ONE thing | $2.837616 |
| 2. Still me at 30s | $4.317585 |
| 3. First + last frame | $1.668447 |
| 4. Video-reference motion — discarded attempt 1 | $1.697303 |
| 4. Video-reference motion — clean run | $1.696792 |
| 1. Fix ONE thing — duplicate completed 720p base call, exact usage lost | ~$0.817018 |
| **Usage-backed successful generations** | **$12.323535** |
| **Estimated all-in** | **~$13.140553** |

## Every generation API attempt

| # | Experiment | Run | Call | Res | s | Input tok | Video tok | Output tok | Cost | Result |
| ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 0 | Smoke test | initial pipeline validation | 3-second dominoes | 360p | 3 | 33 | 5,793 | 6,278 | $0.105792 | success; original media later deleted during cleanup |
| 1 | 1. Fix ONE thing | explore | candidate-01 base | 360p | 8 | 102 | 15,448 | 16,111 | $0.276460 | success |
| 2 | 1. Fix ONE thing | explore | candidate-01 edit | 360p | 8 | 13,560 | 15,448 | 16,350 | $0.298798 | success |
| 3 | 1. Fix ONE thing | explore | candidate-02 base | 360p | 8 | 102 | 15,448 | 16,191 | $0.277180 | success |
| 4 | 1. Fix ONE thing | explore | candidate-03 base | 360p | 8 | 102 | 15,448 | 16,157 | $0.276874 | success |
| 5 | 1. Fix ONE thing | final | base | 720p | 8 | 102 | 46,336 | 47,001 | $0.817018 | success |
| 6 | 1. Fix ONE thing | final | edited | 720p | 8 | 46,200 | 46,336 | 47,570 | $0.891286 | success |
| 7 | 2. Still me at 30s | explore — speech-glitch trial | segment 01 | 360p | 10 | 107 | 19,310 | 20,238 | $0.346438 | success |
| 8 | 2. Still me at 30s | explore — speech-glitch trial | segment 02 | 360p | 10 | 16,694 | 19,310 | 20,164 | $0.370652 | success |
| 9 | 2. Still me at 30s | explore — speech-glitch trial | segment 03 | 360p | 10 | 16,747 | 19,310 | 20,034 | $0.369561 | success |
| 10 | 2. Still me at 30s | final | segment 01 | 720p | 10 | 112 | 57,920 | 58,655 | $1.020383 | success |
| 11 | 2. Still me at 30s | final | segment 02 | 720p | 10 | 56,833 | 57,920 | 58,626 | $1.105204 | success |
| 12 | 2. Still me at 30s | final | segment 03 | 720p | 10 | 56,905 | 57,920 | 58,630 | $1.105347 | success |
| 13 | 3. First + last frame | explore | candidate-01 | 360p | 8 | 2,319 | 15,448 | 16,311 | $0.281585 | success |
| 14 | 3. First + last frame | explore | candidate-02 | 360p | 8 | 2,319 | 15,448 | 16,378 | $0.282189 | success |
| 15 | 3. First + last frame | explore | candidate-03 | 360p | 8 | 2,319 | 15,448 | 16,391 | $0.282305 | success |
| 16 | 3. First + last frame | final | 720p generation | 720p | 8 | 2,319 | 46,336 | 47,226 | $0.822368 | success |
| 17 | 4. Video-reference motion | attempt 1 — discarded text-leaked proof | candidate-01 | 360p | 8 | 4,461 | 15,448 | 16,370 | $0.285330 | generated; discarded as invalid proof |
| 18 | 4. Video-reference motion | attempt 1 — discarded text-leaked proof | candidate-02 | 360p | 8 | 4,461 | 15,448 | 16,242 | $0.284178 | generated; discarded as invalid proof |
| 19 | 4. Video-reference motion | attempt 1 — discarded text-leaked proof | candidate-03 | 360p | 8 | 4,461 | 15,448 | 16,353 | $0.285176 | generated; discarded as invalid proof |
| 20 | 4. Video-reference motion | attempt 1 — discarded text-leaked proof | 720p generation | 720p | 8 | 16,701 | 46,336 | 47,079 | $0.842619 | generated; discarded as invalid proof |
| 21 | 4. Video-reference motion | clean reference-only run | candidate-01 | 360p | 8 | 4,454 | 15,448 | 16,388 | $0.285481 | success |
| 22 | 4. Video-reference motion | clean reference-only run | candidate-02 | 360p | 8 | 4,454 | 15,448 | 16,344 | $0.285085 | success |
| 23 | 4. Video-reference motion | clean reference-only run | candidate-03 | 360p | 8 | 4,454 | 15,448 | 16,200 | $0.283789 | success |
| 24 | 4. Video-reference motion | clean reference-only run | 720p generation | 720p | 8 | 16,694 | 46,336 | 47,060 | $0.842437 | success |
| 25 | 1. Fix ONE thing | final | base attempt #1 | 720p | 8 | ? | ? | ? | **~$0.817018** | generation completed and `api.done` was logged; stdout `BrokenPipe` then overwrote resumable state, causing a duplicate rerun; exact usage was lost |
| 26 | 2. Still me at 30s | explore | invalid explicit-task extension | 360p | 10 | — | — | — | **$0.000000*** | HTTP 400 rejected before generation; no usage returned |

* `$0.000000` is inferred for the HTTP 400 because generation never started and the response contained no usage.

## Waste / failure accounting

- **Experiment 1 duplicate (~$0.817018):** a successful 720p generation was followed by a stdout `BrokenPipe`. `Log.emit()` now catches `BrokenPipeError`, so logging transport failure cannot turn a billed success into a resumable failure again.
- **Experiment 2 rejected request ($0 inferred):** `previous_interaction_id` plus explicit video task mode was invalid. The corrected extension omits explicit task mode.
- **Experiment 2 exploratory sequence ($1.086651):** billed and useful, but treated as a failed draft because extension rewrote speech at the 20s boundary. It led to silence buffers around extension boundaries.
- **Experiment 4 discarded attempt 1 ($1.697303):** technically successful generations, methodologically invalid feature proof because the text prompt itself described the choreography. Preserved under `output/04-video-reference-motion/attempt-1-text-leaked/`.
- **Experiment 4 clean 720p rerun ($0.842437 within the clean-run subtotal):** weaker reference adherence than exploratory candidate 1. Because the API offers no seed/replay control here, the shareable demo uses candidate 1 and local upscaling rather than claiming the 720p rerun reproduced the chosen candidate.

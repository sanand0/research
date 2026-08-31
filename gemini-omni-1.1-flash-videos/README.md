# Gemini Omni 1.1 Flash video experiments

Five independently runnable, resumable `uv` scripts using the official `google-genai` SDK and `gemini-omni-1.1-flash`.

```bash
./01_fix_one_thing.py --dry-run
./01_fix_one_thing.py --format json
./02_still_me_at_30_seconds.py
./03_first_last_frame.py --first-frame assets/start.png --last-frame assets/end.png
./04_video_reference_motion.py --reference-video assets/move.mp4
./05_fail_cheaply.py
```

Every script supports `--describe`, `--dry-run`, and `--format json`. It validates inputs, logs progress **before** long/API actions, and resumes by skipping a completed step only when both its MP4 and metadata JSON still exist.

## Comparable output layout

Each experiment writes under `output/<experiment>/`:

```text
manifest.json       # immutable-ish experiment intent, prompts and run parameters
state.json          # resumable step state, interaction IDs, usage and accumulated cost
events.jsonl        # timestamped progress/errors for humans and agents
explore/ or drafts/ # cheap exploratory generations, where relevant
final/              # final-resolution artifacts
  *.mp4
  *.json            # per-call model/request/usage/cost metadata
```

`.env`, generated output, and Python caches are gitignored. `GEMINI_API_KEY` is loaded from `.env` or the environment and is never intentionally logged.

## Experiment 1: Fix ONE thing

```bash
./01_fix_one_thing.py
```

Default run:

1. Generate three independent 8s 360p base candidates.
2. Edit candidate 1 with only: `Change only the orange payment terminal to cobalt blue. Keep everything else the same.`
3. Generate a fresh 8s 720p base and apply the same stateful edit.
4. Build `final/compare.mp4` as a deterministic side-by-side BEFORE/AFTER proof.

Use `--select N` to choose another exploratory base for the edit. Re-running the same command resumes from the first incomplete step.

## Pricing / experiment budget

Observed smoke-test cost on 2026-08-31 was about **$0.035/generated second at 360p**. Google documents about **$0.10/s at 720p**. Planning estimates:

| Experiment | Estimate |
| --- | ---: |
| Fix ONE thing | ~$2.72 |
| Still me at 30 seconds | ~$4.75 |
| First + last frame interpolation | ~$1.64 |
| Video-reference motion | ~$1.64 |
| Fail cheaply | ~$1.55 |
| **Total** | **~$12.30** |

Actual billing is recorded from API usage in each step JSON and aggregated in `state.json`.


## Experiment 2 result

`02_still_me_at_30_seconds.py` generated a 10s scene and extended it twice via `previous_interaction_id` to a cumulative 30.016s video. A first 360p trial exposed speech being rewritten across the 20s boundary; leaving ~2s of silence around extension boundaries fixed it in the 720p final. The same face, voice, room, camera and props remain visually/audibly consistent across all three turns.

- 360p exploratory sequence: ~$1.087 API cost.
- 720p final sequence: ~$3.231 API cost.
- `output/02-still-me-at-30-seconds/final/sequence/03.mp4`: raw cumulative model output.
- `output/02-still-me-at-30-seconds/final/demo.mp4`: deterministic captions + 10s/20s extension markers.

## Experiment 3 result

`03_first_last_frame.py` uses locally-derived endpoint frames, so there is no extra image-generation spend. Three 360p explorations plus one 720p final cost **$1.668447**. The final generated frame matches the supplied start at SSIM 0.974 and the supplied end at SSIM 0.973, while the intermediate frames visibly move between the viewpoints.

- `output/03-first-last-frame/final/video.mp4`: raw 720p interpolation.
- `output/03-first-last-frame/final/demo.mp4`: supplied start → generated bridge → supplied end.

## Experiment 4 result

The first implementation was discarded because it described the choreography in the text prompt, so it could not prove that the video reference carried the motion. That four-call attempt still cost **$1.697303** and is retained under `output/04-video-reference-motion/attempt-1-text-leaked/`.

The clean rerun removes all choreography from the prompt. Three 360p explorations plus one 720p rerun cost **$1.696792**. Reference adherence is stochastic: exploratory candidate 1 is the clearest proof, while the fresh 720p rerun is weaker. The shareable demo therefore pairs candidate 1 with the 3-second reference slowed to the same normalized 8-second timeline; local upscaling/assembly costs nothing.

- `output/04-video-reference-motion/final/demo.mp4`: best reference-only proof, side-by-side.
- `output/04-video-reference-motion/final/video.mp4`: raw 720p rerun, retained despite weaker adherence.

## Cost ledger

See [`COSTS.md`](COSTS.md) for every API generation attempt, including exploratory generations, discarded attempts, failures, and the one lost-metadata duplicate. Current total: **$12.323535 usage-backed (including the initial smoke test) + ~$0.817018 estimated duplicate = ~$13.140553 all-in**.

# Notes: push-up form quality

## 2026-11-19 Setup

- Videos: 4 × AV1 1920×1080 webm, ~29.75 fps, 140–240 s each, side view, camera at floor level, head on the right.
- 2026-11-15 is heavily backlit (white clothes against a bright window) — a stress test for pose models.
- Some frames show pike / downward-dog positions (hips high) between reps — rep detection must reject non-plank motion.
- Hardware: RTX 2000 Ada 8 GB, 22 cores. ffmpeg has dav1d + nvenc.
- Transcoded to 720p H.264 in scratchpad for fast OpenCV decoding (coords stored normalised 0–1, so resolution doesn't matter downstream).

## Plan

Approaches to compare (all off-the-shelf, re-use rather than invent):
1. MediaPipe Pose Landmarker (BlazePose, heavy) — 33 kpts incl. heel/toe, the classic fitness-app choice.
2. Ultralytics YOLO11-pose — COCO-17; Ultralytics even ships an `AIGym` push-up counter.
3. RTMPose / RTMW via `rtmlib` (ONNX, no mmcv) — strong SOTA-ish real-time top-down; Halpe26 adds feet.
4. ViTPose via HF `transformers` — top-down accuracy reference.
Common scoring pipeline over each model's keypoints so differences = model differences.

Form criteria (side view, coach-style; per rep, use worst/extreme value not average):
- Body line: shoulder–hip–ankle angle, 180° = straight. Sag (hips low) vs pike (hips high) sign.
- Depth: min elbow angle at bottom (≤90° = full).
- Lockout: max elbow angle at top (≥160° = arms straight).
- Neck: ear–shoulder–hip angle (180° = neutral); head drop vs crane.
- Knees: hip–knee–ankle (180° = straight legs).
- Not observable from side: elbow flare, hand width, scapular motion → state as blind spots.

Model-quality checks without ground truth: rep-count agreement, temporal jitter (2nd difference), inter-model agreement, visual audit of hard frames (backlit, occluded far arm).

## 2026-11-19 First model check (150 frames of the backlit video 15)

- YOLO11x-pose at `imgsz=1280` collapsed the whole skeleton onto the shorts. At its 640 training size YOLO11x and YOLO26x both track; YOLO26x looked best → use `yolo26x-pose` @ 640. Lesson: bigger input ≠ better for pose heads.
- MediaPipe heavy lost the body during the stand-up transition (legs mapped onto one leg); fine in plank.
- RTMPose-x (Halpe26) and ViTPose++-H looked right in all three frames.
- Sample speeds (alone on GPU): YOLO26x 20 ms, RTMPose-x 51 ms, ViTPose-H 89 ms (incl. RT-DETR), MediaPipe heavy 89 ms (CPU).

## 2026-11-19 Laptop hard-rebooted during the full runs

- Ran 3 jobs at once (ViTPose-H + YOLO on GPU, MediaPipe on CPU) plus a Gemini upload. The machine died ~10:46 and stayed down until a manual reboot at 11:12.
- Previous-boot journal: no panic, no OOM-killer, no NVIDIA Xid, no thermal-trip message, no pstore dump — the log just stops. Only anomaly: `NVRM ... Out of memory [NV_ERR_NO_MEMORY]` at 10:34 (GPU VRAM pressure while testing). RAM 25% used, avg CPU ~10% (sysstat).
- Interpretation (not proven): hard GPU/driver hang or firmware power/thermal cutoff under concurrent GPU load. Temperatures were not being logged, so heat can't be confirmed or excluded.
- /tmp (scratchpad) was wiped → transcodes moved to `push-ups/work/` (gitignored).
- Mitigations: one heavy job at a time; every 2nd frame (STRIDE=2, ~15 fps); `templog.sh` writes CPU/GPU temp + power every 5 s with fsync to `logs/temps.csv`; `common.cool_down()` pauses inference above 78 °C GPU / 90 °C CPU.
- Re-transcode alone pushed the CPU package to ~79 °C — this ThinkPad runs hot under sustained load.

## 2026-11-19 11:41 Paused (user request)

Done:
- YOLO26x-pose: all 4 videos (data/raw/yolo26x/). Gemini 3.8 Flash + Gemini 4 Argon: all 4 (data/vlm/).
- analyze.py works (smoke-tested on YOLO); index.html works on stand-in data (Playwright + headless Edge screenshots).
- Gemini 3.8 Flash mislabels 7 Nov 12–47 s (clearly fast real push-ups, checked on a 4 fps contact sheet) as "cobra stretches" → 24 reps vs ~57–60. Gemini 4 Argon: 57 reps, and its coaching summary (early reps don't lock out, hip sag, craned neck) matches the pose metrics.
- Guard holds GPU ≤ ~83 °C; CPU peaked 86 °C.

To resume:
1. `./templog.sh logs/temps.csv &` then `for m in rtmpose vitpose mediapipe; do uv run pose_$m.py > logs/$m.log 2>&1; done` (resumes per video; RTMPose 07 was mid-way and restarts).
2. `uv run analyze.py` → data/site/*.js, data/summary.json.
3. Adjudicate rep counts: accept reps where ≥3 pose models agree; inspect disagreements with contact sheets.
4. Tune thresholds (knees maybe too strict for 2D noise), fill VERDICT, audit images (audit.py), README, root README line.

## 2026-11-19 14:25 Second hard reboot — now with a temperature log

- During ViTPose on video 15 (sample ~3000/3557), `logs/temps.csv` shows ~30 min of CPU 89–97 °C, GPU 78–85 °C, fan pinned at ~5080 rpm; last line 14:25:37, then nothing. The guard (check every 50 samples, pause 5 s at CPU ≥ 90) let temps oscillate back above the limit between checks.
- Not power: battery 100 % "Full" right after reboot, USB-C PD adapter online.
- Package temps stayed below their trip points (CPU crit 110 °C, GPU shutdown ~99 °C), so the likely trigger is the ThinkPad EC's own thermal protection on sensors we can't read (VRM / skin). Both crashes: long sustained combined CPU+GPU load at the ceiling.
- ViTPose's CPU-side preprocessing (HF image processor affine warps) is what heated the CPU, not the GPU work.
- Fixes: hysteresis guard (pause at CPU ≥ 80 / GPU ≥ 75, resume < 65 / < 62, CPU checked every sample, GPU every 10); pin to 6 E-cores (`taskset -c 12-17`, CPUs 12–19 are 3.8 GHz E-cores on the Core Ultra 9 185H); OMP/MKL threads = 4; mid-video checkpoints every 250 samples (`<vid>.partial.npz`), resume tested.
- MediaPipe on 6 E-cores: ~230 ms/frame at CPU 65 °C (vs 89 ms on all cores at 90 °C+). Slower but sustainable.
- Gotcha: `pkill -f pattern` / `pgrep -f pattern` match the agent's own `bash -c` wrapper → killed my shell (exit 144). Filter with `ps -eo pid,args | awk '/[p]attern/ && !/bash/'`.
- Preliminary (3 models, 3 videos): pose models agree on rep counts (60/60/60, 59/60/58, 60/60/60); RTMPose ≈ ViTPose scores; YOLO ~2× jitter; scores rise 7→8→11 Nov (~68 → 76 → 85).

## 2026-11-19 15:20–16:05 Finish (all 16 extractions done, no more crashes)

- MediaPipe all 4 + ViTPose 15 on E-cores with the hysteresis guard. Peaks CPU 83 °C / GPU 75 °C. User's Chrome (~350% CPU) kept idle CPU at ~70 °C, above the 65 °C resume threshold → ViTPose stalled; restarted with RESUME_CPU_C=72 from its checkpoint.
- Bugs found by looking at the data, not the code:
  - `near_side` ranked by rounded "fraction present" first; these models emit every keypoint, so it picked the far (left) side on 7 Nov. Now: mean confidence.
  - 15 Nov: you pike at the top of each rep. The old "≥80% of the rep within 40° of straight" rule dropped those reps instead of scoring them. Now: plank at the bottom, <60° bend for 80% of the rep.
  - YOLO's jittery elbow trace split one bottom into two dips (backlight); MediaPipe split a paused bottom. Fix: rep bottoms ≥0.7 s apart (fastest real reps ~0.85 s).
  - Clustering rep bottoms at 0.45 s split one rep across two candidates when models' bottoms differed by ~0.4 s → 0.6 s (safe given the 0.7 s gap).
  - JS object keys "11"/"15" are integer-like and sort before "07"/"08" → explicit sort.
  - CSS `display:flex` on components overrode the `hidden` attribute → global `[hidden]{display:none!important}`.
- Adjudicated counts 60/60/60/50; 7 disputes ruled by eye (data/truth.json).
- Story: sag (7 Nov, 95% of reps) → fixed (11 Nov, 87/100) → overcorrected pike (15 Nov, 98%, median 36°). The user confirmed consciously improving form after 7 Nov.
- Camera control (side agent's concern): floor tilt −0.7…−1.6°, incline 17.3–18.4°, body length 73–82% → angles comparable across days.
- Stability (500 perturbations of thresholds ±30% of span, weights ×0.5–1.5): 11 Nov best 100% (ensemble/RTMPose/ViTPose); 7 vs 15 Nov flips by model.
- VLMs: Argon's prose matches the geometry; its numbers don't (15 Nov = 82, tied best). Flash gives 1–3 distinct scores per session.
- Page tested in headless Edge (Playwright, executable_path=/opt/microsoft/msedge/msedge): no console errors; all 5 modes; light/dark; 390 px no overflow; cell click seeks to the proving frame; keyboard shortcuts.
- Not done: Lighthouse audit (skipped to avoid more CPU heat); ground-truth keypoints (none exist; agreement + audit used instead).

## 2026-11-19 16:50 Slimming the commit

- Images: JPEG → WebP from lossless PNG sources (`cwebp -q 40 -m 6 -sharp_yuv`; screenshot q50 for its small text). 1.25 MB → 0.55 MB, skeletons and labels still crisp.
- Page data: int16 time-deltas + zlib + base64, quantised to 1/5000 frame (~0.4 px) and whole degrees (labels show integers). 4.1 MB → 2.2 MB. The browser inflates with `DecompressionStream("deflate")` (works on file://). Round-trip checked: ≤0.2 px, ≤0.5°, reps identical. Git compresses objects anyway, so the repo-size win is smaller (~20%) than the on-disk one (~45%).
- Dropped `data/summary.json` (duplicate of `data/site/summary.js`); shared `common.load_js()` reads the JS files. Gemini JSON minified.
- Model weights (`*.pt`, `.task`): never committed; the scripts fetch them from upstream.
- Raw keypoints (9.2 MB, 16 npz): needed only to re-analyse, but cost ~3 h and two crashes to make → GitHub release `push-ups-keypoints-2026-11` (tagged on the then-remote main, 8f2e851). Download verified byte-identical.

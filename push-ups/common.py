"""Shared keypoint schema + video loop for the pose extractors.

Every extractor writes data/raw/<model>/<video>.npz with:
  kp:    float32 [samples, len(KP), 3] = (x, y, confidence); x, y normalised to 0..1 of the frame; NaN when the model has no such point
  frame: int32 [samples] source frame index (every STRIDE-th frame)
  fps:   float source frame rate
  ms:    float32 [samples] inference time per frame (ms)
"""

import os
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

KP = [
    "nose",
    "l_eye",
    "r_eye",
    "l_ear",
    "r_ear",
    "l_shoulder",
    "r_shoulder",
    "l_elbow",
    "r_elbow",
    "l_wrist",
    "r_wrist",
    "l_hip",
    "r_hip",
    "l_knee",
    "r_knee",
    "l_ankle",
    "r_ankle",
    "l_heel",
    "r_heel",
    "l_toe",
    "r_toe",
]  # first 17 = COCO order
ROOT = Path(__file__).parent
VIDEO_DIR = Path(os.environ.get("VIDEO_DIR", ROOT / "work" / "v720"))  # 720p H.264 transcodes (see README)
VIDEOS = ["07", "08", "11", "15"]
STRIDE = int(os.environ.get("STRIDE", 2))  # ~15 fps is plenty for 1.5-3 s reps and halves the load
# The laptop hard-rebooted twice under sustained load (2nd time: CPU 89-97 °C, GPU 78-85 °C, fan maxed for ~30 min; see notes.md).
# So: pause at PAUSE_*, resume only below RESUME_* (hysteresis), check CPU every frame, run pinned to E-cores (see README).
PAUSE_GPU_C, PAUSE_CPU_C = int(os.environ.get("PAUSE_GPU_C", 75)), int(os.environ.get("PAUSE_CPU_C", 80))
RESUME_GPU_C, RESUME_CPU_C = int(os.environ.get("RESUME_GPU_C", 62)), int(os.environ.get("RESUME_CPU_C", 65))
CHECKPOINT = 250  # samples between partial saves, so a crash loses minutes, not a whole video
_CPU = next(Path(h, "temp1_input") for h in Path("/sys/class/hwmon").iterdir() if Path(h, "name").read_text().strip() == "coretemp")
_gpu_c = 0


def temps(gpu: bool = True) -> tuple[int, int]:
    """(GPU °C, CPU package °C). nvidia-smi costs ~30 ms, so callers can reuse the last GPU reading."""
    global _gpu_c
    if gpu:
        _gpu_c = int(
            subprocess.run(
                ["nvidia-smi", "--query-gpu=temperature.gpu", "--format=csv,noheader"], capture_output=True, text=True
            ).stdout.split()[0]
        )
    return _gpu_c, int(_CPU.read_text()) // 1000


def cool_down(tag: str, check_gpu: bool) -> None:
    """If CPU or GPU is at its pause limit, block until both are below their resume limits."""
    gpu, cpu = temps(check_gpu)
    if gpu < PAUSE_GPU_C and cpu < PAUSE_CPU_C:
        return
    t0 = time.time()
    while gpu > RESUME_GPU_C or cpu > RESUME_CPU_C:
        time.sleep(3)
        gpu, cpu = temps()
    print(f"{tag} cooled for {time.time() - t0:.0f}s", flush=True)


def run(model: str, infer, videos: list[str] | None = None, limit: int | None = None) -> None:
    """Call infer(bgr_frame, frame_index, fps) -> [len(KP), 3] array in pixel coords for every STRIDE-th frame; save npz.

    Resumable per video, and within a video from <vid>.partial.npz. infer must tolerate starting at any frame index."""
    import cv2  # lazy: vlm_gemini.py imports this module without OpenCV

    cv2.setNumThreads(2)
    for vid in videos or sys.argv[1:] or VIDEOS:
        out = ROOT / "data" / "raw" / model / (f"{vid}-sample.npz" if limit else f"{vid}.npz")
        part = out.with_name(f"{vid}.partial.npz")
        if out.exists() and not limit:
            print(f"[{model}] {vid}: exists, skipping", flush=True)
            continue
        out.parent.mkdir(parents=True, exist_ok=True)
        cap = cv2.VideoCapture(str(VIDEO_DIR / f"{vid}.mp4"))
        fps, n = cap.get(cv2.CAP_PROP_FPS), int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        n = min(n, limit or n)
        frames = np.arange(0, n, STRIDE, dtype=np.int32)
        kps, ms, start = np.full((len(frames), len(KP), 3), np.nan, np.float32), np.zeros(len(frames), np.float32), 0
        if part.exists() and not limit:
            z = np.load(part)
            start = int(z["done"])
            kps[:start], ms[:start] = z["kp"][:start], z["ms"][:start]
            cap.set(cv2.CAP_PROP_POS_FRAMES, int(frames[start]))
        print(f"[{model}] {vid}: {len(frames)} of {n} frames @ {fps:.2f} fps, starting at sample {start}", flush=True)
        t0 = time.time()
        for s in range(start, len(frames)):
            for _ in range(STRIDE - 1 if s > start else 0):
                cap.grab()
            ok, frame = cap.read()
            if not ok:
                frames, kps, ms = frames[:s], kps[:s], ms[:s]
                break
            h, w = frame.shape[:2]
            t = time.perf_counter()
            kp = infer(frame, int(frames[s]), fps)
            ms[s] = (time.perf_counter() - t) * 1000
            if kp is not None:
                kps[s] = kp
                kps[s, :, 0] /= w
                kps[s, :, 1] /= h
            cool_down(f"[{model}] {vid}:", check_gpu=s % 10 == 0)
            if s % CHECKPOINT == 0 and s > start:
                if not limit:
                    np.savez(part, kp=kps, ms=ms, done=s + 1)
                gpu, cpu = temps(False)
                print(f"[{model}] {vid}: {s}/{len(frames)} ({time.time() - t0:.0f}s) GPU {gpu}°C CPU {cpu}°C", flush=True)
        np.savez_compressed(out, kp=kps, frame=frames, fps=fps, ms=ms)
        part.unlink(missing_ok=True)
        print(f"[{model}] {vid}: done in {time.time() - t0:.0f}s, median {np.median(ms):.1f} ms/frame -> {out}", flush=True)


def load_js(path: Path) -> dict:
    """Read a data/site/*.js file written by analyze.write_js: `(window.PUSHUPS ||= {})["key"] = {...};`."""
    import json

    return json.loads(path.read_text().split("] = ", 1)[1].rstrip(";\n"))


def biggest(boxes: np.ndarray) -> int:
    """Index of the largest box [x1, y1, x2, y2] — the exerciser fills the frame; avoids picking reflections / posters."""
    return int(np.argmax((boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])))

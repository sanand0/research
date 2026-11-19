#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["opencv-python", "numpy"]
# ///
"""Contact sheet: same frames, one column per model, skeleton drawn on top. For eyeballing keypoint accuracy.

Usage: uv run audit.py VIDEO FRAME[,FRAME...] OUT.png [--suffix -sample]
       uv run audit.py VIDEO auto OUT.png   # 4 adjudicated rep bottoms where the models disagree most (needs analyze.py output)
"""

import sys

import cv2
import numpy as np

from common import KP, ROOT, VIDEO_DIR, load_js

MODELS = ["mediapipe-heavy", "yolo26x", "rtmpose-x", "vitpose-h"]
BONES = [
    ("ear", "shoulder"),
    ("shoulder", "elbow"),
    ("elbow", "wrist"),
    ("shoulder", "hip"),
    ("hip", "knee"),
    ("knee", "ankle"),
    ("ankle", "heel"),
    ("ankle", "toe"),
]
COL = {"l": (255, 160, 0), "r": (0, 0, 255)}  # BGR: left = blue-ish, right = red
KI = {k: i for i, k in enumerate(KP)}


def draw(img, kp):
    h, w = img.shape[:2]
    for side in "lr":
        for a, b in BONES:
            p, q = kp[KI[f"{side}_{a}"]], kp[KI[f"{side}_{b}"]]
            if np.isnan(p[:2]).any() or np.isnan(q[:2]).any():
                continue
            cv2.line(img, (int(p[0] * w), int(p[1] * h)), (int(q[0] * w), int(q[1] * h)), COL[side], 3, cv2.LINE_AA)
        for k in KP:
            if k.startswith(side) and not np.isnan(kp[KI[k], 0]):
                cv2.circle(img, (int(kp[KI[k], 0] * w), int(kp[KI[k], 1] * h)), 5, COL[side], -1)
    if not np.isnan(kp[0, 0]):
        cv2.circle(img, (int(kp[0, 0] * w), int(kp[0, 1] * h)), 6, (0, 255, 0), -1)


def disputed_frames(vid: str, data: dict, n: int = 4) -> list[int]:
    """Source frame numbers of the adjudicated rep bottoms with the largest spread between models' near-side keypoints."""

    summary = load_js(ROOT / "data" / "site" / "summary.js")["videos"][vid]
    z = np.load(ROOT / "data" / "raw" / MODELS[0] / f"{vid}.npz")
    t = z["frame"] / float(z["fps"])
    idx = [KI[f"{summary['side']}_{p}"] for p in ["shoulder", "elbow", "wrist", "hip", "knee", "ankle"]]
    pts = np.stack([data[m][:, idx, :2] for m in MODELS])  # [models, S, 6, 2]
    spread = np.nanmedian(np.linalg.norm(pts - np.nanmedian(pts, 0), axis=-1), axis=(0, 2))
    samples = sorted({int(np.argmin(np.abs(t - b))) for b in summary["truth_t"]}, key=lambda s: -spread[s])
    return [int(z["frame"][s]) for s in samples[:n]]


def main(vid: str, frames: str, out: str, suffix: str = ""):
    data = {m: np.load(ROOT / "data" / "raw" / m / f"{vid}{suffix}.npz")["kp"] for m in MODELS}
    frame_of = np.load(ROOT / "data" / "raw" / MODELS[0] / f"{vid}{suffix}.npz")["frame"]
    picks = disputed_frames(vid, data) if frames == "auto" else list(map(int, frames.split(",")))
    cap = cv2.VideoCapture(str(VIDEO_DIR / f"{vid}.mp4"))
    rows = []
    for f in picks:
        cap.set(cv2.CAP_PROP_POS_FRAMES, f)
        ok, img = cap.read()
        img = cv2.resize(img, (480, 270))
        cells = []
        for m in MODELS:
            c = img.copy()
            draw(c, data[m][int(np.argmin(np.abs(frame_of - f)))])  # npz holds every STRIDE-th frame
            cv2.putText(c, f"{m} f{f}", (8, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 4)
            cv2.putText(c, f"{m} f{f}", (8, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)
            cells.append(c)
        rows.append(np.hstack(cells))
    cv2.imwrite(out, np.vstack(rows))  # write PNG, then `cwebp -q 50 -m 6` (README): ~5× smaller than JPEG at equal clarity
    print(out, picks)


if __name__ == "__main__":
    args = sys.argv[1:]
    suffix = args[args.index("--suffix") + 1] if "--suffix" in args else ""
    main(*args[:3], suffix=suffix)

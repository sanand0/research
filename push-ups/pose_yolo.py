#!/usr/bin/env -S uv run --script
# /// script
# requires-python = "==3.12.*"
# dependencies = ["ultralytics>=8.3", "opencv-python", "numpy"]
# ///
"""Ultralytics YOLO26x-pose (one-stage, COCO-17; must run at its 640 training size — 1280 collapses the skeleton). Usage: uv run pose_yolo.py [07 08 ...]"""

import os

import numpy as np
from ultralytics import YOLO

from common import KP, biggest, run

model = YOLO(os.environ.get("YOLO_MODEL", "yolo26x-pose.pt"))


def infer(frame, i, fps):
    r = model(frame, verbose=False, imgsz=int(os.environ.get("IMGSZ", 640)))[0]
    if r.keypoints is None or len(r.boxes) == 0:
        return None
    j = biggest(r.boxes.xyxy.cpu().numpy())
    out = np.full((len(KP), 3), np.nan, np.float32)
    out[:17, :2] = r.keypoints.xy[j].cpu().numpy()
    out[:17, 2] = r.keypoints.conf[j].cpu().numpy()
    return out


if __name__ == "__main__":
    run(os.environ.get("YOLO_NAME", "yolo26x"), infer, limit=int(os.environ.get("LIMIT", 0)) or None)

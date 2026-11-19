#!/usr/bin/env -S uv run --script
# /// script
# requires-python = "==3.12.*"
# dependencies = ["mediapipe>=0.10.20", "opencv-python", "numpy", "httpx"]
# ///
"""MediaPipe Pose Landmarker (BlazePose GHUM heavy, 33 kpts, VIDEO mode = uses temporal tracking). Usage: uv run pose_mediapipe.py [07 ...]"""

import os

import cv2
import httpx
import mediapipe as mp
import numpy as np

from common import KP, ROOT, run

VARIANT = os.environ.get("MP_VARIANT", "heavy")
URL = f"https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_{VARIANT}/float16/latest/pose_landmarker_{VARIANT}.task"
MODEL = ROOT / "data" / "models" / f"pose_landmarker_{VARIANT}.task"
# BlazePose index for each KP name
MAP = dict(
    nose=0,
    l_eye=2,
    r_eye=5,
    l_ear=7,
    r_ear=8,
    l_shoulder=11,
    r_shoulder=12,
    l_elbow=13,
    r_elbow=14,
    l_wrist=15,
    r_wrist=16,
    l_hip=23,
    r_hip=24,
    l_knee=25,
    r_knee=26,
    l_ankle=27,
    r_ankle=28,
    l_heel=29,
    r_heel=30,
    l_toe=31,
    r_toe=32,
)
IDX = [MAP[k] for k in KP]

if not MODEL.exists():
    MODEL.parent.mkdir(parents=True, exist_ok=True)
    MODEL.write_bytes(httpx.get(URL, follow_redirects=True).raise_for_status().content)

landmarker = None


def infer(frame, i, fps):
    global landmarker
    if landmarker is None or i == 0:  # new video (or resumed run): timestamps restart, so recreate the tracker
        opts = mp.tasks.vision.PoseLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path=str(MODEL)), running_mode=mp.tasks.vision.RunningMode.VIDEO, num_poses=1
        )
        landmarker = mp.tasks.vision.PoseLandmarker.create_from_options(opts)
    h, w = frame.shape[:2]
    img = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    res = landmarker.detect_for_video(img, int(i * 1000 / fps))
    if not res.pose_landmarks:
        return None
    lm = res.pose_landmarks[0]
    return np.array([[lm[j].x * w, lm[j].y * h, lm[j].visibility] for j in IDX], np.float32)


if __name__ == "__main__":
    run(f"mediapipe-{VARIANT}", infer, limit=int(os.environ.get("LIMIT", 0)) or None)

#!/usr/bin/env -S uv run --script
# /// script
# requires-python = "==3.12.*"
# dependencies = ["rtmlib>=0.0.13", "onnxruntime-gpu[cuda,cudnn]>=1.20", "opencv-python", "numpy"]
# [tool.uv]
# override-dependencies = ["onnxruntime; sys_platform == 'never'"]  # rtmlib pins CPU onnxruntime, which shadows the GPU build
# ///
"""RTMPose-x Halpe26 (body + feet) with YOLOX detector via rtmlib/ONNX. Usage: uv run pose_rtmpose.py [07 ...]"""

import os

import numpy as np
import onnxruntime as ort
from rtmlib import BodyWithFeet

from common import run

ort.preload_dlls()  # load pip-installed CUDA/cuDNN
DEVICE = "cuda" if "CUDAExecutionProvider" in ort.get_available_providers() else "cpu"
model = BodyWithFeet(mode=os.environ.get("RTM_MODE", "performance"), backend="onnxruntime", device=DEVICE)
# Halpe26: 0-16 COCO, 17 head, 18 neck, 19 hip, 20/21 L/R big toe, 22/23 L/R small toe, 24/25 L/R heel
HALPE = list(range(17)) + [24, 25, 20, 21]


def infer(frame, i, fps):
    kps, scores = model(frame)
    if len(kps) == 0:
        return None
    j = int(np.argmax(np.ptp(kps[:, :, 0], axis=1) * np.ptp(kps[:, :, 1], axis=1)))  # largest person
    return np.c_[kps[j][HALPE], scores[j][HALPE]].astype(np.float32)


if __name__ == "__main__":
    print("device", DEVICE, flush=True)
    run("rtmpose-x", infer, limit=int(os.environ.get("LIMIT", 0)) or None)

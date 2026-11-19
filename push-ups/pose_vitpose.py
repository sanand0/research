#!/usr/bin/env -S uv run --script
# /// script
# requires-python = "==3.12.*"
# dependencies = ["transformers>=4.50", "torch", "accelerate", "opencv-python", "numpy", "pillow", "scipy"]
# ///
"""ViTPose++ (HF transformers) top-down, with RT-DETR person detector. Usage: uv run pose_vitpose.py [07 ...]"""

import os

import cv2
import numpy as np
import torch
from PIL import Image
from transformers import AutoProcessor, RTDetrForObjectDetection, VitPoseForPoseEstimation

from common import KP, biggest, run

DEV = "cuda"
POSE = os.environ.get("VITPOSE", "usyd-community/vitpose-plus-huge")
det_proc = AutoProcessor.from_pretrained("PekingU/rtdetr_r50vd_coco_o365")
det = RTDetrForObjectDetection.from_pretrained("PekingU/rtdetr_r50vd_coco_o365").to(DEV).eval()
pose_proc = AutoProcessor.from_pretrained(POSE)
pose = VitPoseForPoseEstimation.from_pretrained(POSE, torch_dtype=torch.float16).to(DEV).eval()


@torch.inference_mode()
def infer(frame, i, fps):
    img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    inp = det_proc(images=img, return_tensors="pt").to(DEV)
    r = det_proc.post_process_object_detection(det(**inp), target_sizes=[(img.height, img.width)], threshold=0.3)[0]
    boxes = r["boxes"][r["labels"] == 0].cpu().numpy()
    if len(boxes) == 0:
        return None
    b = boxes[biggest(boxes)]
    box = [[b[0], b[1], b[2] - b[0], b[3] - b[1]]]  # COCO xywh
    inp = pose_proc(img, boxes=[box], return_tensors="pt").to(DEV)
    inp["pixel_values"] = inp["pixel_values"].half()
    kw = {"dataset_index": torch.tensor([0], device=DEV)} if "plus" in POSE else {}  # ViTPose++ MoE head 0 = COCO
    o = pose(**inp, **kw)
    o.heatmaps = o.heatmaps.float()  # post-processing (scipy) rejects fp16
    p = pose_proc.post_process_pose_estimation(o, boxes=[box])[0][0]
    out = np.full((len(KP), 3), np.nan, np.float32)
    out[:17, :2] = p["keypoints"].float().cpu().numpy()
    out[:17, 2] = p["scores"].float().cpu().numpy()
    return out


if __name__ == "__main__":
    run("vitpose-h", infer, limit=int(os.environ.get("LIMIT", 0)) or None)

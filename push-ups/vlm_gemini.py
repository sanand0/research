#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["google-genai>=1.30", "numpy"]
# ///
"""End-to-end VLM "coach": Gemini watches the video and scores each rep. No keypoints, so no overlay — only timestamps + scores.

Usage: GEMINI_API_KEY=$(llm keys get gemini) uv run vlm_gemini.py MODEL [07 08 ...]
Writes data/vlm/<model>/<video>.json. Resumable.
"""

import json
import os
import sys
import time
from pathlib import Path

from google import genai
from google.genai import types

from common import ROOT, VIDEOS

VIDEO_DIR = Path(os.environ.get("VLM_VIDEO_DIR", ROOT / "work" / "v480"))
PROMPT = """You are a strength coach reviewing a side-view video of one person doing push-ups.
Find EVERY standard push-up repetition (plank position, chest lowers by bending the elbows, then presses back up).
Ignore rests, stretches, walking, setting up, and pike / downward-dog movements (hips high) — but list those separately in "other_movements".

For each rep give timestamps in seconds (decimal, e.g. 12.4) for start (top), bottom (lowest point) and end (top again), and score 0-100:
- back: straight line ears-shoulders-hips-ankles; penalise sagging or piked hips
- depth: 100 = elbows at or below 90 degrees / chest near floor; lower for shallow reps
- lockout: 100 = arms fully straight at the top
- head: 100 = neutral neck in line with the spine; penalise dropping or craning the head
- overall: your holistic form score
Add a short note (max 12 words) on the main fault, if any. Be precise and consistent; do not invent reps."""
SCHEMA = {
    "type": "object",
    "properties": {
        "reps": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "start": {"type": "number"},
                    "bottom": {"type": "number"},
                    "end": {"type": "number"},
                    "back": {"type": "integer"},
                    "depth": {"type": "integer"},
                    "lockout": {"type": "integer"},
                    "head": {"type": "integer"},
                    "overall": {"type": "integer"},
                    "note": {"type": "string"},
                },
                "required": ["start", "bottom", "end", "back", "depth", "lockout", "head", "overall", "note"],
            },
        },
        "other_movements": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"start": {"type": "number"}, "end": {"type": "number"}, "what": {"type": "string"}},
                "required": ["start", "end", "what"],
            },
        },
        "summary": {"type": "string"},
    },
    "required": ["reps", "other_movements", "summary"],
}
FPS = float(os.environ.get("VLM_FPS", 5))  # reps last ~1.5-3 s, default 1 fps would miss bottoms


def main(model: str, videos: list[str]):
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    for vid in videos or VIDEOS:
        out = ROOT / "data" / "vlm" / model / f"{vid}.json"
        if out.exists():
            print(f"[{model}] {vid}: exists, skipping", flush=True)
            continue
        print(f"[{model}] {vid}: uploading", flush=True)
        f = client.files.upload(file=VIDEO_DIR / f"{vid}.mp4")
        while f.state.name == "PROCESSING":
            time.sleep(3)
            f = client.files.get(name=f.name)
        print(f"[{model}] {vid}: generating", flush=True)
        t0 = time.time()
        part = types.Part(file_data=types.FileData(file_uri=f.uri, mime_type="video/mp4"), video_metadata=types.VideoMetadata(fps=FPS))
        r = client.models.generate_content(
            model=model,
            contents=[part, PROMPT],
            config=types.GenerateContentConfig(response_mime_type="application/json", response_json_schema=SCHEMA, temperature=0),
        )
        data = json.loads(r.text) | {
            "model": model,
            "fps": FPS,
            "seconds": round(time.time() - t0, 1),
            "usage": r.usage_metadata.model_dump(exclude_none=True) if r.usage_metadata else None,
        }
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(data, separators=(",", ":")))
        print(f"[{model}] {vid}: {len(data['reps'])} reps in {data['seconds']}s", flush=True)
        client.files.delete(name=f.name)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])

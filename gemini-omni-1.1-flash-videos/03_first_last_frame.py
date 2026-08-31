#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["google-genai>=2.19.0", "pillow>=11"]
# ///
"""Experiment 3: interpolate a controlled move between supplied endpoint frames."""

import argparse
import json
import subprocess
from pathlib import Path

from PIL import Image

from common import Log, ROOT, client, generate_step, print_result, state_for, upload_part, write_json

EXPERIMENT = "03-first-last-frame"
PROMPT = "[# Sources <FIRST_FRAME>@Image1 <LAST_FRAME>@Image2] Smooth cinematic camera move from the supplied first frame to the supplied last frame. Preserve the exact woman, cobalt-blue apron, payment terminal, red mug, counter, plants, shop layout and warm lighting. The camera smoothly moves from the left-hand viewpoint to the right-hand viewpoint with natural parallax. Single continuous shot, constant smooth camera speed, no jump cuts. Subtle shop ambience. No dialogue. Use Image1 as the exact starting frame and Image2 as the exact final frame."


def default_frames(output_dir: Path) -> tuple[Path, Path]:
    """Create two endpoint views locally from the successful merchant scene."""
    source = ROOT / "output/01-fix-one-thing/final/edited.mp4"
    if not source.exists():
        raise FileNotFoundError(f"Default source missing: {source}; pass --first-frame/--last-frame")
    assets = output_dir / "assets"
    first, last, raw = assets / "first.png", assets / "last.png", assets / "source.png"
    if first.exists() and last.exists():
        return first, last
    assets.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "4", "-i", str(source), "-frames:v", "1", str(raw)], check=True)
    image = Image.open(raw).convert("RGB")
    w, h = image.size
    # Two overlapping crops create distinct viewpoints while preserving every scene element.
    crop_w = int(w * 0.88)
    left = image.crop((0, 0, crop_w, h)).resize((w, h), Image.Resampling.LANCZOS)
    right = image.crop((w - crop_w, 0, w, h)).resize((w, h), Image.Resampling.LANCZOS)
    left.save(first)
    right.save(last)
    raw.unlink()
    return first, last


def assemble_demo(first: Path, video: Path, last: Path, output: Path, log: Log) -> None:
    if output.exists():
        log.emit("resume.skip", step="assemble", output=str(output)); return
    log.emit("assemble.start", step="assemble", output=str(output))
    output.parent.mkdir(parents=True, exist_ok=True)
    vf = (
        "[0:v]scale=1280:720,drawtext=text='I SUPPLIED THIS START FRAME':x=(w-text_w)/2:y=40:fontsize=42:fontcolor=white:box=1:boxcolor=black@0.65,fps=24,trim=duration=1.5,setpts=PTS-STARTPTS[a];"
        "[1:v]scale=1280:720,drawtext=text='GEMINI GENERATED EVERYTHING BETWEEN':x=(w-text_w)/2:y=40:fontsize=38:fontcolor=white:box=1:boxcolor=black@0.65,setpts=PTS-STARTPTS[b];"
        "[2:v]scale=1280:720,drawtext=text='...AND THIS END FRAME':x=(w-text_w)/2:y=40:fontsize=42:fontcolor=white:box=1:boxcolor=black@0.65,fps=24,trim=duration=1.5,setpts=PTS-STARTPTS[c];"
        "[a][b][c]concat=n=3:v=1:a=0[v]"
    )
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", str(first), "-i", str(video), "-loop", "1", "-i", str(last), "-filter_complex", vf, "-map", "[v]", "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", str(output)], check=True)
    log.emit("assemble.done", step="assemble", output=str(output))


def main() -> None:
    p = argparse.ArgumentParser(description="Generate motion constrained by supplied first and last frames.")
    p.add_argument("--first-frame"); p.add_argument("--last-frame")
    p.add_argument("--output-dir", default="output/03-first-last-frame")
    p.add_argument("--candidates", type=int, default=3); p.add_argument("--phase", choices=["explore", "final", "all"], default="all")
    p.add_argument("--dry-run", action="store_true"); p.add_argument("--describe", action="store_true"); p.add_argument("--format", choices=["human", "json"], default="human")
    args = p.parse_args()
    desc = {"experiment": EXPERIMENT, "defaults": {"candidates": 3, "frames": "derived locally from Experiment 1 unless supplied"}, "resume": "per-step MP4+JSON"}
    if args.describe or args.dry_run:
        print(json.dumps(desc | ({"prompt": PROMPT, "phase": args.phase} if args.dry_run else {}), indent=2)); return
    if (args.first_frame is None) != (args.last_frame is None): p.error("provide both --first-frame and --last-frame, or neither")
    if not 1 <= args.candidates <= 9: p.error("--candidates must be 1..9")
    output_dir = ROOT / args.output_dir; output_dir.mkdir(parents=True, exist_ok=True)
    first, last = (Path(args.first_frame), Path(args.last_frame)) if args.first_frame else default_frames(output_dir)
    write_json(output_dir / "manifest.json", {"experiment": EXPERIMENT, "prompt": PROMPT, "first_frame": str(first), "last_frame": str(last)})
    log, state, c = Log(output_dir), state_for(output_dir, EXPERIMENT), client()
    try:
        parts = [upload_part(c, first, "image", log), upload_part(c, last, "image", log), {"type": "text", "text": PROMPT}]
        if args.phase in {"explore", "all"}:
            for i in range(1, args.candidates + 1):
                generate_step(c, output_dir, state, log, step=f"explore-{i:02d}", prompt=PROMPT, output_rel=f"explore/candidate-{i:02d}.mp4", resolution="360p", duration=8, input_parts=parts)
        if args.phase in {"final", "all"}:
            generate_step(c, output_dir, state, log, step="final", prompt=PROMPT, output_rel="final/video.mp4", resolution="720p", duration=8, input_parts=parts)
            assemble_demo(first, output_dir / "final/video.mp4", last, output_dir / "final/demo.mp4", log)
        final = output_dir / "final/demo.mp4" if (output_dir / "final/demo.mp4").exists() else output_dir / "explore/candidate-01.mp4"
        print_result(output_dir, state, args.format, final=str(final.relative_to(ROOT)))
    finally: c.close()

if __name__ == "__main__": main()

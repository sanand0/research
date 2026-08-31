#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["google-genai>=2.19.0", "pillow>=11"]
# ///
"""Experiment 4: transfer unmistakable choreography from a short reference video."""

import argparse
import json
import math
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw

from common import Log, ROOT, client, generate_step, print_result, state_for, upload_part, write_json

EXPERIMENT = "04-video-reference-motion"
PROMPT = "[# References <VIDEO_REF_0>@Video1] Copy only the body movement from <VIDEO_REF_0>. A faceless cobalt-blue training mannequin on a brightly lit football pitch performs the same unusual sequence of full-body poses, in the same order and with the same relative timing as the reference. Reproduce the motion faithfully; do not simplify it into a generic wave or exercise. Full body visible throughout. Fixed camera. Single continuous shot. No cuts. Do not copy the reference figure's appearance, colors, text or background. No dialogue. Use Video1 as a movement reference, not as a source for video editing."


def default_reference(output_dir: Path) -> Path:
    """Render a simple 3s stick-figure choreography locally; no API spend."""
    assets = output_dir / "assets"; video = assets / "motion-reference.mp4"
    if video.exists(): return video
    frames = assets / "frames"; frames.mkdir(parents=True, exist_ok=True)
    W, H, fps, n = 640, 360, 24, 72
    poses = [
        # right arm up; both arms horizontal; crouch; left arm diagonal up
        ((-35, 65), (18, -70), 0), ((-70, 0), (70, 0), 0), ((-45, 45), (45, 45), 45), ((-18, -70), (55, -45), 0)
    ]
    for i in range(n):
        t = i / (n - 1); phase = min(3, int(t * 4)); local = t * 4 - phase if phase < 3 else min(1, t * 4 - 3)
        a = poses[phase]; b = poses[min(3, phase + 1)]
        interp = lambda x, y: x + (y - x) * (0.5 - 0.5 * math.cos(math.pi * local))
        la = (interp(a[0][0], b[0][0]), interp(a[0][1], b[0][1])); ra = (interp(a[1][0], b[1][0]), interp(a[1][1], b[1][1])); crouch = interp(a[2], b[2])
        im = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(im)
        d.rectangle((0, 290, W, H), fill=(235, 240, 235)); d.line((0, 290, W, 290), fill=(80, 140, 80), width=4)
        cx, shoulder_y = 320, 150 + crouch; hip_y = 225 + crouch
        red = (220, 45, 45)
        d.ellipse((cx-20, shoulder_y-55, cx+20, shoulder_y-15), outline=red, width=8)
        d.line((cx, shoulder_y-15, cx, hip_y), fill=red, width=10)
        def arm(angle):
            rad = math.radians(angle); return cx + 75*math.sin(rad), shoulder_y + 75*math.cos(rad)
        # Angle convention: 0 down, +/-90 horizontal, +/-180 up.
        lx, ly = arm(la[0]); rx, ry = arm(ra[0])
        # Coordinates above encode x/y directly for readability; map vectors to endpoints.
        lx, ly = cx + la[0], shoulder_y + la[1]; rx, ry = cx + ra[0], shoulder_y + ra[1]
        d.line((cx, shoulder_y, lx, ly), fill=red, width=10); d.line((cx, shoulder_y, rx, ry), fill=red, width=10)
        leg = 55 - crouch * 0.3
        d.line((cx, hip_y, cx-35, hip_y+leg), fill=red, width=10); d.line((cx, hip_y, cx+35, hip_y+leg), fill=red, width=10)
        d.text((18, 18), "MOTION REFERENCE — 3 SECONDS", fill="black")
        im.save(frames / f"{i:04d}.png")
    assets.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(fps), "-i", str(frames / "%04d.png"), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-t", "3", str(video)], check=True)
    for f in frames.glob("*.png"): f.unlink()
    frames.rmdir()
    return video


def assemble_demo(reference: Path, generated: Path, output: Path, log: Log) -> None:
    if output.exists(): log.emit("resume.skip", step="assemble", output=str(output)); return
    log.emit("assemble.start", step="assemble", output=str(output)); output.parent.mkdir(parents=True, exist_ok=True)
    fg = (
        "[0:v]setpts=PTS*8/3,fps=24,trim=duration=8,scale=640:720:force_original_aspect_ratio=decrease,pad=640:720:(ow-iw)/2:(oh-ih)/2,drawtext=text='3-SECOND REFERENCE - SLOWED TO MATCH':x=(w-text_w)/2:y=40:fontsize=25:fontcolor=white:box=1:boxcolor=black@0.65[r];"
        "[1:v]scale=640:720:force_original_aspect_ratio=decrease,pad=640:720:(ow-iw)/2:(oh-ih)/2,drawtext=text='NEW SCENE - MOTION NOT DESCRIBED':x=(w-text_w)/2:y=40:fontsize=25:fontcolor=white:box=1:boxcolor=black@0.65[g];"
        "[r][g]hstack=inputs=2[v]"
    )
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-stream_loop", "-1", "-i", str(reference), "-i", str(generated), "-filter_complex", fg, "-map", "[v]", "-map", "1:a?", "-c:v", "libx264", "-crf", "20", "-c:a", "aac", "-shortest", str(output)], check=True)
    log.emit("assemble.done", step="assemble", output=str(output))


def main() -> None:
    p = argparse.ArgumentParser(description="Transfer choreography from a <=3s reference video.")
    p.add_argument("--reference-video"); p.add_argument("--output-dir", default="output/04-video-reference-motion")
    p.add_argument("--candidates", type=int, default=3); p.add_argument("--select", type=int, default=1); p.add_argument("--phase", choices=["explore", "final", "all"], default="all")
    p.add_argument("--dry-run", action="store_true"); p.add_argument("--describe", action="store_true"); p.add_argument("--format", choices=["human", "json"], default="human")
    args = p.parse_args(); desc = {"experiment": EXPERIMENT, "defaults": {"candidates": 3, "reference": "locally rendered 3s choreography unless supplied"}, "resume": "per-step MP4+JSON"}
    if args.describe or args.dry_run: print(json.dumps(desc | ({"prompt": PROMPT, "phase": args.phase} if args.dry_run else {}), indent=2)); return
    if not 1 <= args.candidates <= 9: p.error("--candidates must be 1..9")
    if not 1 <= args.select <= args.candidates: p.error("--select must be within generated candidates")
    output_dir = ROOT / args.output_dir; output_dir.mkdir(parents=True, exist_ok=True)
    ref = Path(args.reference_video) if args.reference_video else default_reference(output_dir)
    write_json(output_dir / "manifest.json", {"experiment": EXPERIMENT, "prompt": PROMPT, "reference_video": str(ref)})
    log, state, c = Log(output_dir), state_for(output_dir, EXPERIMENT), client()
    try:
        parts = [upload_part(c, ref, "video", log), {"type": "text", "text": PROMPT}]
        if args.phase in {"explore", "all"}:
            for i in range(1, args.candidates + 1):
                generate_step(c, output_dir, state, log, step=f"explore-{i:02d}", prompt=PROMPT, output_rel=f"explore/candidate-{i:02d}.mp4", resolution="360p", duration=8, input_parts=parts)
        if args.phase in {"final", "all"}:
            generate_step(c, output_dir, state, log, step="final", prompt=PROMPT, output_rel="final/video.mp4", resolution="720p", duration=8, input_parts=parts)
            selected = output_dir / f"explore/candidate-{args.select:02d}.mp4"
            assemble_demo(ref, selected, output_dir / "final/demo.mp4", log)
        final = output_dir / "final/demo.mp4" if (output_dir / "final/demo.mp4").exists() else output_dir / "explore/candidate-01.mp4"
        print_result(output_dir, state, args.format, final=str(final.relative_to(ROOT)))
    finally: c.close()

if __name__ == "__main__": main()

#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["google-genai>=2.19.0"]
# ///
"""Experiment 2: test multi-turn continuity across 30 seconds."""

import argparse
import json
import subprocess
from common import Log, ROOT, client, generate_step, print_result, state_for, write_json

EXPERIMENT = "02-still-me-at-30-seconds"
PROMPTS = [
    "Exactly 10 seconds. Single continuous locked-off medium shot, no cuts. A woman in a distinctive cobalt-blue jacket stands behind a small-business counter. A red ceramic mug is on her left and a blue payment terminal on her right. Warm morning light. In the first six seconds, she says in a crisp calm Indian-English voice: 'Ten seconds used to be the wall. Continuing meant starting over.' Then she stays silent for the rest of the shot and slowly picks up the red mug. No music. Natural room ambience.",
    "Continue the same unbroken scene for exactly 10 more seconds. Preserve exactly the same woman, voice, clothing, room, camera, lighting and ambience. In the first six seconds of this extension, she sets the mug down and says: 'Same face. Same voice. Same room. This is the second ten seconds.' Then she stays silent for the rest of this extension. No music.",
    "Continue the same unbroken scene for exactly 10 more seconds. Preserve exactly the same woman, voice, clothing, room, camera, lighting and ambience. In the first six seconds of this extension, she says: 'Thirty seconds. One continuous story, not three unrelated clips.' Then she stays silent and smiles naturally until the end. No music.",
]


def assemble_demo(output_dir, raw, log):
    """Add deterministic captions and extension markers without touching generated media."""
    output = output_dir / "demo.mp4"
    captions = output_dir / "captions.srt"
    if output.exists():
        log.emit("resume.skip", step="assemble", output=str(output))
        return output
    captions.write_text("""1
00:00:00,000 --> 00:00:05,500
Ten seconds used to be the wall.
Continuing meant starting over.

2
00:00:10,800 --> 00:00:16,800
Same face. Same voice.
This is the second ten seconds.

3
00:00:20,000 --> 00:00:26,500
Thirty seconds. One continuous story,
not three unrelated clips.
""")
    log.emit("assemble.start", step="assemble", output=str(output))
    vf = (
        "drawbox=x=0:y=0:w=iw:h=50:color=black@0.58:t=fill,"
        "drawtext=text='10s GENERATED  +10s EXTENSION  +10s EXTENSION':x=(w-text_w)/2:y=12:fontsize=24:fontcolor=white,"
        "drawtext=text='+10s':x=(w-text_w)/2:y=62:fontsize=24:fontcolor=white:box=1:boxcolor=black@0.65:enable='between(t,9.65,10.65)',"
        "drawtext=text='+10s':x=(w-text_w)/2:y=62:fontsize=24:fontcolor=white:box=1:boxcolor=black@0.65:enable='between(t,19.65,20.65)',"
        f"subtitles={captions}:force_style='FontSize=20,MarginV=28,Outline=2'"
    )
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw), "-vf", vf,
                    "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-c:a", "copy", str(output)], check=True)
    log.emit("assemble.done", step="assemble", output=str(output))
    return output


def main() -> None:
    p = argparse.ArgumentParser(description="Test 30-second identity, voice, scene and audio continuity.")
    p.add_argument("--output-dir", default="output/02-still-me-at-30-seconds")
    p.add_argument("--resolution", choices=["360p", "720p"], default="360p")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--describe", action="store_true")
    p.add_argument("--format", choices=["human", "json"], default="human")
    args = p.parse_args()
    desc = {"experiment": EXPERIMENT, "steps": ["base", "extension-1", "extension-2"], "resume": "per-step MP4+JSON"}
    if args.describe or args.dry_run:
        print(json.dumps(desc | {"prompts": PROMPTS} if args.dry_run else desc, indent=2)); return
    output_dir = ROOT / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True); write_json(output_dir / "manifest.json", {"experiment": EXPERIMENT, "prompts": PROMPTS})
    log, state, c = Log(output_dir), state_for(output_dir, EXPERIMENT), client()
    try:
        prev = None
        for i, prompt in enumerate(PROMPTS):
            rec = generate_step(c, output_dir, state, log, step=["base", "extension-1", "extension-2"][i], prompt=prompt,
                output_rel=f"sequence/{i+1:02d}.mp4", resolution=args.resolution, duration=10,
                previous_interaction_id=prev)
            prev = rec["interaction_id"]
        demo = assemble_demo(output_dir, output_dir / "sequence/03.mp4", log)
        print_result(output_dir, state, args.format, final=str(demo.relative_to(ROOT)))
    finally: c.close()

if __name__ == "__main__": main()

#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["google-genai>=2.19.0"]
# ///
"""Experiment 5: make cheap 360p variants, then finish one at 720p."""

import argparse
import json
from common import Log, ROOT, client, generate_step, print_result, state_for, write_json

EXPERIMENT = "05-fail-cheaply"
PROMPT = "Exactly 5 seconds. Single continuous product shot of a cobalt-blue payment terminal on a warm modern small-business counter. A merchant hand taps once, the terminal gives a subtle confirmation glow, and the camera makes a gentle 10-degree push-in. Premium natural commercial lighting. No text. No dialogue."


def main() -> None:
    p = argparse.ArgumentParser(description="Generate several cheap drafts and one final-resolution winner.")
    p.add_argument("--variants", type=int, default=6); p.add_argument("--select", type=int, default=1); p.add_argument("--output-dir", default="output/05-fail-cheaply")
    p.add_argument("--dry-run", action="store_true"); p.add_argument("--describe", action="store_true"); p.add_argument("--format", choices=["human", "json"], default="human")
    args = p.parse_args(); desc = {"experiment": EXPERIMENT, "defaults": {"variants": 6, "select": 1}, "resume": "per-step MP4+JSON"}
    if args.describe or args.dry_run: print(json.dumps(desc | ({"prompt": PROMPT} if args.dry_run else {}), indent=2)); return
    if not 1 <= args.select <= args.variants: p.error("--select must be between 1 and --variants")
    output_dir = ROOT / args.output_dir; output_dir.mkdir(parents=True, exist_ok=True); write_json(output_dir / "manifest.json", {"experiment": EXPERIMENT, "prompt": PROMPT, "variants": args.variants, "select": args.select})
    log, state, c = Log(output_dir), state_for(output_dir, EXPERIMENT), client()
    try:
        for i in range(1, args.variants + 1):
            generate_step(c, output_dir, state, log, step=f"draft-{i:02d}", prompt=PROMPT, output_rel=f"drafts/{i:02d}.mp4", resolution="360p", duration=5)
        generate_step(c, output_dir, state, log, step="final", prompt=PROMPT, output_rel="final/video.mp4", resolution="720p", duration=5)
        print_result(output_dir, state, args.format, final=str((output_dir / "final/video.mp4").relative_to(ROOT)))
    finally: c.close()

if __name__ == "__main__": main()

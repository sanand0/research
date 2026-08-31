#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["google-genai>=2.19.0"]
# ///
"""Experiment 1: test surgical stateful video editing."""

import argparse
import json
from pathlib import Path

from common import Log, ROOT, assemble_side_by_side, client, generate_step, print_result, state_for, write_json

EXPERIMENT = "01-fix-one-thing"
BASE_PROMPT = """Exactly 8 seconds. Single continuous locked-off shot, no cuts.

A small-business owner in a cobalt-blue apron stands behind a modern neighbourhood shop counter. An ORANGE payment terminal is clearly visible on the counter. A red ceramic mug sits to the left and a green plant to the right.

She scans one parcel, taps the orange terminal once, puts a receipt into a paper bag, then smiles.

Natural shop ambience. No dialogue. No music. No text overlays."""
EDIT_PROMPT = "Change only the orange payment terminal to cobalt blue. Keep everything else the same."


def describe() -> dict:
    return {
        "experiment": EXPERIMENT,
        "purpose": "Show that one video error can be edited without collateral changes.",
        "arguments": {
            "--phase": ["explore", "final", "all"],
            "--candidates": "1-9 exploratory 360p base generations; default 3",
            "--select": "1-based exploratory candidate to edit; default 1",
            "--output-dir": "default output/01-fix-one-thing",
            "--dry-run": "print plan without API calls",
            "--format": ["human", "json"],
        },
        "resume": "Completed steps with both MP4 and JSON are skipped on rerun.",
    }


def main() -> None:
    p = argparse.ArgumentParser(description=describe()["purpose"])
    p.add_argument("--phase", choices=["explore", "final", "all"], default="all")
    p.add_argument("--candidates", type=int, default=3)
    p.add_argument("--select", type=int, default=1)
    p.add_argument("--output-dir", default="output/01-fix-one-thing")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--describe", action="store_true")
    p.add_argument("--format", choices=["human", "json"], default="human")
    args = p.parse_args()
    if args.describe:
        print(json.dumps(describe(), indent=2))
        return
    if not 1 <= args.candidates <= 9:
        p.error("--candidates must be between 1 and 9")
    if not 1 <= args.select <= args.candidates:
        p.error("--select must be between 1 and --candidates")

    output_dir = (ROOT / args.output_dir).resolve()
    if ROOT not in output_dir.parents:
        p.error("--output-dir must be inside this repository")
    plan = {
        "experiment": EXPERIMENT,
        "phase": args.phase,
        "candidates": args.candidates,
        "selected_candidate": args.select,
        "base_prompt": BASE_PROMPT,
        "edit_prompt": EDIT_PROMPT,
    }
    if args.dry_run:
        print(json.dumps(plan, indent=2))
        return

    output_dir.mkdir(parents=True, exist_ok=True)
    write_json(output_dir / "manifest.json", plan)
    log = Log(output_dir)
    state = state_for(output_dir, EXPERIMENT)
    c = client()
    try:
        if args.phase in {"explore", "all"}:
            bases = []
            for i in range(1, args.candidates + 1):
                bases.append(generate_step(c, output_dir, state, log, step=f"explore-base-{i:02d}", prompt=BASE_PROMPT,
                    output_rel=f"explore/candidate-{i:02d}/base.mp4", resolution="360p", duration=8))
            chosen = bases[args.select - 1]
            generate_step(c, output_dir, state, log, step=f"explore-edit-{args.select:02d}", prompt=EDIT_PROMPT,
                output_rel=f"explore/candidate-{args.select:02d}/edited.mp4", resolution="360p", duration=8,
                previous_interaction_id=chosen["interaction_id"])

        if args.phase in {"final", "all"}:
            base = generate_step(c, output_dir, state, log, step="final-base", prompt=BASE_PROMPT,
                output_rel="final/base.mp4", resolution="720p", duration=8)
            generate_step(c, output_dir, state, log, step="final-edit", prompt=EDIT_PROMPT,
                output_rel="final/edited.mp4", resolution="720p", duration=8,
                previous_interaction_id=base["interaction_id"])
            assemble_side_by_side(output_dir / "final/base.mp4", output_dir / "final/edited.mp4", output_dir / "final/compare.mp4", log)

        print_result(output_dir, state, args.format, compare=str((output_dir / "final/compare.mp4").relative_to(ROOT)))
    finally:
        c.close()


if __name__ == "__main__":
    main()

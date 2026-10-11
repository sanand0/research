#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14"
# dependencies = []
# ///
"""Check the pinned game snapshot's shape and perfect reference playthrough."""
import json
from pathlib import Path

raw = Path(__file__).with_name("game.js").read_text()
data = json.loads(raw.split("window.GAME = ", 1)[1].removesuffix(";\n"))
assert data["totals"] == {
    "rooms": 15, "puzzles": 18, "items": 26, "findables": 8,
    "curiosities": 11, "sigils": 6, "points": 375
}
assert len(data["route"]) == 21
assert len({r["room"] for r in data["route"]}) == 15
assert data["route"][-1]["score"] == 375
assert len(data["council"]) == 6
assert len(data["zen"]) == 19
assert set(data["puzzles"]) == set(k for r in data["route"] for k in r["answer"])
print("PASS: 15 rooms / 18 puzzles / 8 floor souvenirs / 11 secrets / 375 points")

#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["numpy"]
# ///
"""Does the session ranking survive other reasonable thresholds / weights / models? Re-scores stored per-rep metrics.

Usage: uv run stability.py   (reads data/site/*.js; prints how often each ranking occurs)
"""

import numpy as np

from analyze import SCORING, VIDEOS
from common import ROOT, load_js

rng = np.random.default_rng(0)
site = {v: load_js(ROOT / "data" / "site" / f"{v}.js") for v in VIDEOS}


def session_scores(model, sc):
    out = {}
    for v in VIDEOS:
        reps = site[v]["models"][model]["reps"]
        rs = []
        for r in reps:
            parts = {
                k: np.clip(100 * (x - sc[k]["bad"]) / (sc[k]["good"] - sc[k]["bad"]), 0, 100)
                for k, x in r["metrics"].items()
                if x is not None
            }
            w = sum(sc[k]["weight"] for k in parts)
            rs.append(sum(parts[k] * sc[k]["weight"] for k in parts) / w)
        out[v] = np.mean(rs)
    return out


def perturb():
    """Each threshold ±30% of its good–bad span, each weight ×0.5–1.5."""
    sc = {}
    for k, s in SCORING.items():
        span = abs(s["good"] - s["bad"])
        sc[k] = dict(
            good=s["good"] + rng.uniform(-0.3, 0.3) * span,
            bad=s["bad"] + rng.uniform(-0.3, 0.3) * span,
            weight=s["weight"] * rng.uniform(0.5, 1.5),
        )
    return sc


rank = lambda s: " > ".join(sorted(s, key=s.get, reverse=True))
print(f"{'model':16s} {'base ranking':22s} P(11 best)  P(08 2nd)  P(07 > 15)")
for m in ["ensemble", "rtmpose-x", "vitpose-h", "mediapipe-heavy", "yolo26x"]:
    base = session_scores(m, SCORING)
    runs = [session_scores(m, perturb()) for _ in range(500)]
    order = [sorted(r, key=r.get, reverse=True) for r in runs]
    p = lambda f, order=order, runs=runs: f"{100 * np.mean([f(o, r) for o, r in zip(order, runs, strict=True)]):5.1f}%"
    print(
        f"{m:16s} {rank(base):22s} {p(lambda o, r: o[0] == '11'):>10s} {p(lambda o, r: o[1] == '08'):>10s} {p(lambda o, r: r['07'] > r['15']):>11s}"
    )

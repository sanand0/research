#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["mrestimator==0.2.0", "numpy>=2", "scipy>=1.10"]
# ///
"""Post-first-mouse stress test: can state changes invalidate a single-MR fit?

Specified after one discovery mouse and primary-literature evidence of Allen state
transitions. This is a method diagnostic, never confirmatory biological evidence.
"""
from __future__ import annotations

import json
from pathlib import Path

import mrestimator as mre
import numpy as np

from c002_fixed_neuron_calibrate import (
    DT_MS,
    MEAN_OBSERVED_PER_BIN,
    MODULE_SIZE,
    N_MODULES,
    N_NEURONS,
    N_SUBSETS,
    SEEDS,
    SUBSET_N,
    neuron_weights,
    observe_subset,
    subset_probabilities,
)
from c002_mr_calibrate import estimate_m

SEGMENT_LENGTH = 75_000  # 300 s at 4 ms
N_SEGMENTS = 3


def simulate_piecewise(schedule: list[list[float]], seed: int) -> list[np.ndarray]:
    if len(schedule) != N_SEGMENTS or any(len(x) != N_MODULES for x in schedule):
        raise ValueError("schedule shape mismatch")
    mean_module = (MEAN_OBSERVED_PER_BIN * N_NEURONS / SUBSET_N) / N_MODULES
    modules: list[np.ndarray] = []
    for g in range(N_MODULES):
        parts = []
        for s in range(N_SEGMENTS):
            m = schedule[s][g]
            h = mean_module * (1 - m)
            part = np.asarray(
                mre.simulate_branching(
                    m=m,
                    h=h,
                    length=SEGMENT_LENGTH,
                    seed=seed + 1009 * g + 100_003 * s,
                )
            ).reshape(-1).astype(np.int64)
            parts.append(part)
        modules.append(np.concatenate(parts))
    return modules


def run_scenario(name: str, schedule: list[list[float]], seed: int) -> dict:
    weights = neuron_weights(seed + 17)
    modules = simulate_piecewise(schedule, seed)
    rng = np.random.default_rng(seed + 29)
    rows = []
    for rep in range(N_SUBSETS):
        subset = np.sort(rng.choice(N_NEURONS, size=SUBSET_N, replace=False))
        q = subset_probabilities(subset, weights)
        y = observe_subset(modules, q, seed + 20_000 + rep)
        full = estimate_m(y, kmax=200)
        segments = []
        for s in range(N_SEGMENTS):
            z = y[s * SEGMENT_LENGTH : (s + 1) * SEGMENT_LENGTH]
            segments.append({"segment": s, **estimate_m(z, kmax=200)})
        rows.append(
            {
                "replicate": rep,
                "mean_count_per_bin": float(y.mean()),
                "full": full,
                "segments": segments,
            }
        )
    return {"name": name, "schedule": schedule, "seed": seed, "rows": rows}


def summarize(scenarios: list[dict], name: str) -> dict:
    rows = [r for s in scenarios if s["name"] == name for r in s["rows"]]
    full = [r["full"] for r in rows]
    seg = [x for r in rows for x in r["segments"]]
    return {
        "n_subsets": len(rows),
        "full_applicable": sum(bool(x["applicable"]) for x in full),
        "full_applicable_fraction": sum(bool(x["applicable"]) for x in full) / len(full),
        "full_r2_range": [float(min(x["r2"] for x in full)), float(max(x["r2"] for x in full))],
        "segment_applicable": sum(bool(x["applicable"]) for x in seg),
        "segment_total": len(seg),
        "segment_applicable_fraction": sum(bool(x["applicable"]) for x in seg) / len(seg),
        "segment_r2_range": [float(min(x["r2"] for x in seg)), float(max(x["r2"] for x in seg))],
    }


def main() -> None:
    global_switch = [
        [0.90] * N_MODULES,
        [0.99] * N_MODULES,
        [0.90] * N_MODULES,
    ]
    asynchronous = [
        [0.90, 0.90, 0.90, 0.90, 0.99, 0.99, 0.99, 0.99],
        [0.99, 0.90, 0.90, 0.99, 0.99, 0.90, 0.99, 0.90],
        [0.99, 0.99, 0.99, 0.99, 0.90, 0.90, 0.90, 0.90],
    ]
    scenarios = []
    for seed in SEEDS:
        scenarios.append(run_scenario("global_state_switch", global_switch, seed))
        scenarios.append(run_scenario("asynchronous_module_switch", asynchronous, seed))
    result = {
        "status": "post_first_mouse_method_diagnostic",
        "warning": "Specified after one Allen discovery mouse and state-transition literature were inspected; not confirmatory evidence.",
        "dt_ms": DT_MS,
        "segment_duration_s": SEGMENT_LENGTH * DT_MS / 1000,
        "n_segments": N_SEGMENTS,
        "summary": {
            "global_state_switch": summarize(scenarios, "global_state_switch"),
            "asynchronous_module_switch": summarize(scenarios, "asynchronous_module_switch"),
        },
        "scenarios": scenarios,
    }
    out = Path(__file__).parents[1] / "results" / "c002_state_switch_calibration.json"
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result["summary"], indent=2))


if __name__ == "__main__":
    main()

#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["mrestimator==0.2.0", "numpy>=2", "scipy>=1.10"]
# ///
"""Post-first-mouse calibration of MR under fixed-neuron observation.

This is a METHOD diagnostic, not confirmatory evidence: one Allen discovery mouse had
already been inspected before this simulation family was specified.
"""
from __future__ import annotations

import json
from pathlib import Path

import mrestimator as mre
import numpy as np

from c002_mr_calibrate import DT_MS, estimate_m

N_NEURONS = 512
N_MODULES = 8
MODULE_SIZE = N_NEURONS // N_MODULES
SUBSET_N = 32
LENGTH = 225_000  # 900 s at 4 ms
MEAN_OBSERVED_PER_BIN = 0.40  # roughly first Allen 32-unit V1 subset
SEEDS = [101, 211, 307]
N_SUBSETS = 10


def neuron_weights(seed: int, sigma: float = 0.8) -> np.ndarray:
    """Fixed heterogeneous event-allocation probabilities within each module."""
    rng = np.random.default_rng(seed)
    weights = np.empty((N_MODULES, MODULE_SIZE), dtype=float)
    for g in range(N_MODULES):
        x = rng.lognormal(mean=0.0, sigma=sigma, size=MODULE_SIZE)
        weights[g] = x / x.sum()
    return weights


def module_for_neuron(neuron_id: int) -> tuple[int, int]:
    if not 0 <= neuron_id < N_NEURONS:
        raise ValueError(neuron_id)
    return divmod(neuron_id, MODULE_SIZE)


def subset_probabilities(subset: np.ndarray, weights: np.ndarray) -> np.ndarray:
    """Probability an event in each module lands on an observed fixed neuron."""
    q = np.zeros(N_MODULES, dtype=float)
    for neuron_id in np.asarray(subset, dtype=int):
        g, j = module_for_neuron(int(neuron_id))
        q[g] += weights[g, j]
    return q


def simulate_modules(ms: list[float], seed: int) -> list[np.ndarray]:
    """Independent module-level branching processes with equal stationary mean."""
    if len(ms) != N_MODULES:
        raise ValueError("one m per module required")
    # Expected fraction of all neurons observed is 32/512. To obtain ~0.4 observed
    # events/bin, target ~6.4 events/bin across the full 512-neuron population.
    mean_module = (MEAN_OBSERVED_PER_BIN * N_NEURONS / SUBSET_N) / N_MODULES
    out = []
    for g, m in enumerate(ms):
        h = mean_module * (1 - m)
        x = np.asarray(
            mre.simulate_branching(m=m, h=h, length=LENGTH, seed=seed + 1009 * g)
        ).reshape(-1).astype(np.int64)
        out.append(x)
    return out


def observe_subset(modules: list[np.ndarray], q: np.ndarray, seed: int) -> np.ndarray:
    """Observe a fixed neuron subset by module-specific binomial event allocation."""
    rng = np.random.default_rng(seed)
    y = np.zeros_like(modules[0], dtype=np.int64)
    for x, p in zip(modules, q, strict=True):
        y += rng.binomial(x, float(p))
    return y


def run_scenario(name: str, ms: list[float], seed: int) -> dict:
    weights = neuron_weights(seed + 17)
    modules = simulate_modules(ms, seed)
    rng = np.random.default_rng(seed + 29)
    rows = []
    for rep in range(N_SUBSETS):
        subset = np.sort(rng.choice(N_NEURONS, size=SUBSET_N, replace=False))
        q = subset_probabilities(subset, weights)
        y = observe_subset(modules, q, seed + 10_000 + rep)
        est = estimate_m(y, kmax=200)
        rows.append(
            {
                "replicate": rep,
                "mean_count_per_bin": float(y.mean()),
                "module_observation_probabilities": q.tolist(),
                **est,
            }
        )
    applicable = [r for r in rows if r["applicable"]]
    return {
        "name": name,
        "module_ms": ms,
        "seed": seed,
        "n_subsets": len(rows),
        "n_applicable": len(applicable),
        "m_range_applicable": (
            [float(min(r["m"] for r in applicable)), float(max(r["m"] for r in applicable))]
            if applicable
            else None
        ),
        "r2_range": [float(min(r["r2"] for r in rows)), float(max(r["r2"] for r in rows))],
        "rows": rows,
    }


def main() -> None:
    homogeneous = [0.98] * N_MODULES
    # Prespecified broad mixed-timescale stress case. There is intentionally no single
    # true m: a one-exponential fit is misspecified if a subset mixes these modules.
    mixed = [0.85, 0.90, 0.94, 0.96, 0.975, 0.985, 0.99, 0.995]
    scenarios = []
    for seed in SEEDS:
        scenarios.append(run_scenario("common_m_heterogeneous_rates", homogeneous, seed))
        scenarios.append(run_scenario("mixed_module_timescales", mixed, seed))

    def summarize(name: str) -> dict:
        rows = [r for s in scenarios if s["name"] == name for r in s["rows"]]
        applicable = [r for r in rows if r["applicable"]]
        return {
            "n_subsets": len(rows),
            "n_applicable": len(applicable),
            "applicable_fraction": len(applicable) / len(rows),
            "m_range_applicable": (
                [float(min(r["m"] for r in applicable)), float(max(r["m"] for r in applicable))]
                if applicable else None
            ),
            "r2_range": [float(min(r["r2"] for r in rows)), float(max(r["r2"] for r in rows))],
            "mean_count_per_bin_range": [
                float(min(r["mean_count_per_bin"] for r in rows)),
                float(max(r["mean_count_per_bin"] for r in rows)),
            ],
        }

    result = {
        "status": "post_first_mouse_method_diagnostic",
        "warning": "Simulation family was specified after one discovery mouse was inspected; it cannot validate a confirmatory biological claim.",
        "dt_ms": DT_MS,
        "duration_s": LENGTH * DT_MS / 1000,
        "n_neurons": N_NEURONS,
        "n_modules": N_MODULES,
        "subset_n": SUBSET_N,
        "neuron_rate_heterogeneity": "lognormal fixed module weights, sigma=0.8",
        "observation_model": "fixed neuron identities; module events allocated with fixed neuron probabilities; observed subset induces module-specific binomial thinning",
        "summary": {
            "common_m_heterogeneous_rates": summarize("common_m_heterogeneous_rates"),
            "mixed_module_timescales": summarize("mixed_module_timescales"),
        },
        "scenarios": scenarios,
    }
    out = Path(__file__).parents[1] / "results" / "c002_fixed_neuron_calibration.json"
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result["summary"], indent=2))


if __name__ == "__main__":
    main()

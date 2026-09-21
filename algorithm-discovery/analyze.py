"""Summarize development runs with problem-level uncertainty."""

from __future__ import annotations

import csv
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

import numpy as np

LEDGER = Path("results/runs.csv")
OUT = Path("results/development-summary.json")
ALGORITHMS = [
    "scipy-best-p2-halton",
    "scipy-best-p5-halton",
    "scipy-best-p5-halton-deferred",
    "scipy-best-p5-halton-cr1",
    "pairde-p5-halton",
    "rejde-p5-halton",
    "rejde-off-p5-halton",
    "cma-s30",
    "modde-lshade-p2",
    "modde-lshade-p4",
    "modde-lshade-p6",
]
MILESTONES = ("err_20d", "err_50d", "err_100d", "err_200d")


def logerr(x: str) -> float:
    return math.log10(max(float(x), 1e-12))


def ci_bootstrap(values: list[float], statistic, seed: int = 20260910) -> list[float]:
    rng = np.random.default_rng(seed)
    a = np.asarray(values, dtype=float)
    reps = np.empty(10000)
    for i in range(len(reps)):
        reps[i] = statistic(rng.choice(a, size=len(a), replace=True))
    return [float(np.quantile(reps, 0.025)), float(np.quantile(reps, 0.975))]


def main() -> None:
    rows = [r for r in csv.DictReader(LEDGER.open()) if r["phase"] == "pilot" and r["algorithm"] in ALGORITHMS]
    by_alg = defaultdict(list)
    for r in rows:
        by_alg[r["algorithm"]].append(r)

    summary: dict = {"n_rows": len(rows), "algorithms": {}, "pairde_vs_matched": {}}
    for alg in ALGORITHMS:
        rs = by_alg[alg]
        item = {
            "runs": len(rs),
            "success_1e-2": sum(bool(r["hit_1e-2"]) for r in rs),
            "success_1e-5": sum(bool(r["hit_1e-5"]) for r in rs),
            "median_nfev_per_dim_to_1e-2_given_success": statistics.median(int(r["hit_1e-2"]) / int(r["dimension"]) for r in rs if r["hit_1e-2"]) if any(r["hit_1e-2"] for r in rs) else None,
            "median_nfev_per_dim_to_1e-5_given_success": statistics.median(int(r["hit_1e-5"]) / int(r["dimension"]) for r in rs if r["hit_1e-5"]) if any(r["hit_1e-5"] for r in rs) else None,
            "median_overhead_us_per_eval": statistics.median(float(r["overhead_us_per_eval"]) for r in rs),
            "median_log10_error": {m: statistics.median(logerr(r[m]) for r in rs) for m in MILESTONES},
        }
        summary["algorithms"][alg] = item

    # Problem is the unit of uncertainty; median over the two stochastic seeds first.
    unit = defaultdict(lambda: defaultdict(dict))
    for r in rows:
        k = (int(r["fid"]), int(r["instance"]), int(r["dimension"]))
        unit[r["algorithm"]][k].setdefault("rows", []).append(r)
    for alg in ALGORITHMS:
        for k, d in unit[alg].items():
            rs = d["rows"]
            for m in MILESTONES:
                d[m] = statistics.median(logerr(r[m]) for r in rs)

    base = unit["scipy-best-p5-halton-deferred"]
    cand = unit["pairde-p5-halton"]
    for m in MILESTONES:
        deltas = [base[k][m] - cand[k][m] for k in sorted(base)]  # positive = PairDE better
        summary["pairde_vs_matched"][m] = {
            "problem_units": len(deltas),
            "mean_log10_advantage": statistics.mean(deltas),
            "mean_95pct_problem_bootstrap": ci_bootstrap(deltas, np.mean),
            "median_log10_advantage": statistics.median(deltas),
            "median_95pct_problem_bootstrap": ci_bootstrap(deltas, np.median),
            "wins": sum(x > 0 for x in deltas),
            "losses": sum(x < 0 for x in deltas),
        }

    groups = {"separable": (1, 3), "moderate": (6, 8), "ill_conditioned": (10, 12), "multimodal_global": (15, 17), "multimodal_weak": (20, 23)}
    by_group = {}
    for name, fids in groups.items():
        vals = []
        for k in sorted(base):
            if k[0] in fids:
                vals.append(base[k]["err_200d"] - cand[k]["err_200d"])
        by_group[name] = {
            "n_problem_units": len(vals),
            "mean_log10_advantage": statistics.mean(vals),
            "median_log10_advantage": statistics.median(vals),
            "wins": sum(v > 0 for v in vals),
        }
    summary["pairde_200d_by_group"] = by_group

    # Current low-budget baseline comparisons after Batch 3 tuning.
    current = {}
    pairs = [
        ("scipy-best-p2-halton", "scipy-best-p5-halton"),
        ("scipy-best-p2-halton", "cma-s30"),
        ("scipy-best-p2-halton", "modde-lshade-p4"),
    ]
    for a, b in pairs:
        ua, ub = unit[a], unit[b]
        deltas = [ub[k]["err_200d"] - ua[k]["err_200d"] for k in sorted(set(ua) & set(ub))]
        current[f"{a}_vs_{b}"] = {
            "problem_units": len(deltas),
            "mean_log10_advantage": statistics.mean(deltas),
            "median_log10_advantage": statistics.median(deltas),
            "mean_95pct_problem_bootstrap": ci_bootstrap(deltas, np.mean),
            "wins": sum(x > 0 for x in deltas),
        }
    summary["current_baseline_comparisons"] = current

    OUT.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

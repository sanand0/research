"""Analyze the frozen Batch-7 BBOB confirmation without retuning."""
from __future__ import annotations

import csv
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

import numpy as np

LEDGER = Path("results/confirmation-runs.csv")
PROTOCOL = Path("results/confirmation-protocol.json")
OUT = Path("results/confirmation-summary.json")
MILESTONES = (50, 100, 200)


def logerr(x: str) -> float:
    return math.log10(max(float(x), 1e-12))


def unit_values(rows, algorithm: str, milestone: int) -> dict[tuple[int, int], float]:
    grouped = defaultdict(list)
    field = f"err_{milestone}d"
    for r in rows:
        if r["algorithm"] == algorithm:
            grouped[(int(r["fid"]), int(r["instance"]))].append(logerr(r[field]))
    return {k: statistics.median(v) for k, v in grouped.items()}


def compare(rows, a: str, b: str, milestone: int) -> dict:
    # Positive advantage => a has lower error than b.
    ua = unit_values(rows, a, milestone)
    ub = unit_values(rows, b, milestone)
    keys = sorted(set(ua) & set(ub))
    vals = [ub[k] - ua[k] for k in keys]
    rng = np.random.default_rng(20260920 + milestone)
    arr = np.asarray(vals, float)
    means = np.array([np.mean(rng.choice(arr, len(arr), replace=True)) for _ in range(20000)])
    medians = np.array([np.median(rng.choice(arr, len(arr), replace=True)) for _ in range(20000)])
    return {
        "problem_units": len(vals),
        "mean_log10_advantage": statistics.mean(vals),
        "median_log10_advantage": statistics.median(vals),
        "wins": sum(v > 0 for v in vals),
        "win_rate": sum(v > 0 for v in vals) / len(vals),
        "ties": sum(v == 0 for v in vals),
        "mean_95pct_bootstrap": [float(x) for x in np.quantile(means, [0.025, 0.975])],
        "median_95pct_bootstrap": [float(x) for x in np.quantile(medians, [0.025, 0.975])],
        "per_unit": [
            {"fid": k[0], "instance": k[1], "log10_advantage": v}
            for k, v in zip(keys, vals, strict=True)
        ],
    }


def algorithm_summary(rows, alg: str) -> dict:
    rs = [r for r in rows if r["algorithm"] == alg]
    out = {
        "runs": len(rs),
        "nfev_min": min(int(r["nfev"]) for r in rs),
        "nfev_max": max(int(r["nfev"]) for r in rs),
        "overshoots": sum(int(r["nfev"]) > int(r["budget"]) for r in rs),
        "median_overhead_us_per_eval": statistics.median(float(r["overhead_us_per_eval"]) for r in rs),
        "success_1e-2": sum(bool(r["hit_1e-2"]) for r in rs),
        "success_1e-5": sum(bool(r["hit_1e-5"]) for r in rs),
    }
    for md in MILESTONES:
        vals = [logerr(r[f"err_{md}d"]) for r in rs]
        out[f"median_log10_error_{md}d"] = statistics.median(vals)
        out[f"mean_log10_error_{md}d"] = statistics.mean(vals)
    for target, field in [("1e-2", "hit_1e-2"), ("1e-5", "hit_1e-5")]:
        hits = [int(r[field]) / int(r["dimension"]) for r in rs if r[field]]
        out[f"median_nfev_per_d_to_{target}_given_success"] = statistics.median(hits) if hits else None
    return out


def by_function(rows, a: str, b: str, milestone: int) -> dict:
    comp = compare(rows, a, b, milestone)
    grouped = defaultdict(list)
    for item in comp["per_unit"]:
        grouped[item["fid"]].append(item["log10_advantage"])
    return {
        str(fid): {
            "median_log10_advantage": statistics.median(vals),
            "mean_log10_advantage": statistics.mean(vals),
            "wins": sum(v > 0 for v in vals),
            "instances": len(vals),
        }
        for fid, vals in sorted(grouped.items())
    }


def main() -> None:
    rows = list(csv.DictReader(LEDGER.open()))
    protocol = json.loads(PROTOCOL.read_text())
    algs = list(protocol["algorithms"])

    primary = {
        str(md): compare(rows, "scipy-p2-halton", "scipy-default-p15", md)
        for md in MILESTONES
    }
    threshold = float(protocol["primary_criterion"]["median_log10_advantage_min"])
    win_min = float(protocol["primary_criterion"]["problem_unit_win_rate_min"])
    required = [str(x) for x in protocol["primary_criterion"]["milestones_d"]]
    pass_details = {
        md: {
            "median_pass": primary[md]["median_log10_advantage"] >= threshold,
            "win_rate_pass": primary[md]["win_rate"] >= win_min,
        }
        for md in required
    }
    passed = all(v["median_pass"] and v["win_rate_pass"] for v in pass_details.values())

    out = {
        "protocol_sha256_note": "Protocol was frozen before first held-out run; see confirmation-protocol.json.",
        "rows": len(rows),
        "unique_keys": len({(r["algorithm"], r["fid"], r["instance"], r["dimension"], r["seed"], r["budget"]) for r in rows}),
        "budget_overshoots": sum(int(r["nfev"]) > int(r["budget"]) for r in rows),
        "primary_criterion": {
            "passed": passed,
            "threshold_median_log10_advantage": threshold,
            "threshold_win_rate": win_min,
            "milestones": pass_details,
            "comparison": primary,
        },
        "algorithms": {alg: algorithm_summary(rows, alg) for alg in algs},
        "secondary": {
            "p2_vs_cma": {str(md): compare(rows, "scipy-p2-halton", "cma-s30", md) for md in MILESTONES},
            "lshade_vs_cma": {str(md): compare(rows, "lshade-p2", "cma-s30", md) for md in MILESTONES},
            "p2_vs_lshade": {str(md): compare(rows, "scipy-p2-halton", "lshade-p2", md) for md in MILESTONES},
            "p2_vs_default_by_function": {str(md): by_function(rows, "scipy-p2-halton", "scipy-default-p15", md) for md in MILESTONES},
        },
    }
    OUT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

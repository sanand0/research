"""Fixed 2x2 ablation: SciPy DE population size x initialization design."""
from __future__ import annotations

import csv
import json
import math
import os
import statistics
import time
from pathlib import Path

import numpy as np

from bench import run_scipy
from pk_transfer import BudgetedPK, DIMENSION, FIELDS, MILESTONES_D, make_protocol

OUT = Path("results/pk-ablation.csv")
SUMMARY = Path("results/pk-ablation-summary.json")

CONFIGS = {
    "scipy-p2-lhs": {"strategy": "best1bin", "popsize": 2, "updating": "immediate", "init": "latinhypercube", "mutation": (0.5, 1.0), "recombination": 0.7},
    "scipy-p15-halton": {"strategy": "best1bin", "popsize": 15, "updating": "immediate", "init": "halton", "mutation": (0.5, 1.0), "recombination": 0.7},
}


def key(r):
    return tuple(str(r[k]) for k in ("algorithm", "subject", "seed", "budget"))


def append(row):
    new = not OUT.exists()
    with OUT.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new:
            w.writeheader()
        w.writerow(row)
        f.flush()
        os.fsync(f.fileno())


def run_case(name, cfg, subject, seed, budget_d=200):
    obj = BudgetedPK(np.asarray(subject["unit_truth"], float), budget_d * DIMENSION)
    t = time.perf_counter()
    run_scipy(obj, seed, cfg)
    wall = time.perf_counter() - t
    obj.fill_snapshots()
    objective_s = obj.objective_ns / 1e9
    def sv(md, field):
        return obj.snapshots[md][field]
    append({
        "algorithm": name, "family": "scipy", "subject": subject["subject"], "seed": seed,
        "budget": budget_d * DIMENSION, "nfev": obj.nfev,
        "obj_50d": f"{sv(50,'objective'):.17g}", "obj_100d": f"{sv(100,'objective'):.17g}", "obj_200d": f"{sv(200,'objective'):.17g}",
        "param_50d": f"{sv(50,'parameter_error'):.17g}", "param_100d": f"{sv(100,'parameter_error'):.17g}", "param_200d": f"{sv(200,'parameter_error'):.17g}",
        "hit_obj_1e-4": obj.objective_hits[1e-4] or "", "hit_obj_1e-6": obj.objective_hits[1e-6] or "",
        "hit_param_005": obj.parameter_hits[0.05] or "", "hit_param_001": obj.parameter_hits[0.01] or "",
        "final_objective": f"{obj.best_y:.17g}", "final_parameter_error": f"{obj.parameter_error():.17g}",
        "best_x_json": json.dumps(obj.best_x.tolist(), separators=(",", ":")),
        "wall_s": f"{wall:.9g}", "objective_s": f"{objective_s:.9g}",
        "overhead_us_per_eval": f"{max(0.0,wall-objective_s)*1e6/max(1,obj.nfev):.9g}",
        "config_json": json.dumps(cfg, sort_keys=True, separators=(",", ":")),
    })


def main():
    protocol = make_protocol()
    done = set()
    if OUT.exists():
        done = {key(r) for r in csv.DictReader(OUT.open())}
    for name, cfg in CONFIGS.items():
        for subject in protocol["subjects"]:
            for seed in protocol["optimizer_seeds"]:
                probe = {"algorithm": name, "subject": subject["subject"], "seed": seed, "budget": 200 * DIMENSION}
                if key(probe) not in done:
                    run_case(name, cfg, subject, seed)

    primary = list(csv.DictReader(open("results/pk-runs.csv")))
    extra = list(csv.DictReader(OUT.open()))
    names = ["scipy-default-p15", "scipy-p15-halton", "scipy-p2-lhs", "scipy-p2-halton"]
    allrows = {name: [r for r in primary + extra if r["algorithm"] == name] for name in names}
    summary = {}
    for name in names:
        rs = allrows[name]
        summary[name] = {
            "runs": len(rs),
            **{f"median_log10_obj_{md}d": statistics.median(math.log10(max(float(r[f"obj_{md}d"]),1e-16)) for r in rs) for md in MILESTONES_D},
            **{f"median_param_{md}d": statistics.median(float(r[f"param_{md}d"]) for r in rs) for md in MILESTONES_D},
        }
    SUMMARY.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

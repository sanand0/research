"""Frozen Batch-7 confirmation on the untouched BBOB reserve.

Do not change algorithms, functions, instances, dimension, seeds, budgets, or
the preregistered pass criterion after running this script.
"""
from __future__ import annotations

import csv
import json
import math
import os
import time
from pathlib import Path

from bench import BudgetedBBOB, FIELDS, run_cma, run_lshade, run_scipy

FUNCTIONS = (2, 7, 11, 16, 21)
INSTANCES = (11, 12, 13, 14, 15)
DIMENSION = 20
SEEDS = (1, 2)
BUDGET_D = 200
LEDGER = Path("results/confirmation-runs.csv")
PROTOCOL = Path("results/confirmation-protocol.json")

ALGORITHMS = {
    "scipy-default-p15": ("scipy", {
        "strategy": "best1bin", "popsize": 15, "updating": "immediate",
        "init": "latinhypercube", "mutation": (0.5, 1.0), "recombination": 0.7,
    }),
    "scipy-p2-halton": ("scipy", {
        "strategy": "best1bin", "popsize": 2, "updating": "immediate",
        "init": "halton", "mutation": (0.5, 1.0), "recombination": 0.7,
    }),
    "lshade-p2": ("lshade", {"lambda_per_d": 2, "bound_correction": "saturate"}),
    "cma-s30": ("cma", {"sigma_frac": 0.30, "popsize_mult": 1.0}),
}
RUNNERS = {"scipy": run_scipy, "lshade": run_lshade, "cma": run_cma}


def freeze_protocol() -> dict:
    protocol = {
        "functions": list(FUNCTIONS),
        "instances": list(INSTANCES),
        "dimension": DIMENSION,
        "seeds": list(SEEDS),
        "budget_d": BUDGET_D,
        "milestones_d": [50, 100, 200],
        "algorithms": ALGORITHMS,
        "primary_criterion": {
            "comparison": "scipy-p2-halton vs scipy-default-p15",
            "median_log10_advantage_min": 0.5,
            "milestones_d": [50, 100],
            "problem_unit_win_rate_min": 0.70,
            "problem_unit": "function x instance; median over seeds first",
        },
        "secondary_questions": [
            "Does early p2 vs late CMA crossover persist at unseen 20D problems?",
            "Does L-SHADE p2 improve robustness relative to plain p2?",
            "Do target success and NFE-to-target tell the same story as fixed-budget errors?",
        ],
        "post_confirmation_rule": "No parameter changes or reinterpretation against failures.",
    }
    PROTOCOL.parent.mkdir(parents=True, exist_ok=True)
    canonical = json.loads(json.dumps(protocol, sort_keys=True))
    if PROTOCOL.exists():
        old = json.loads(PROTOCOL.read_text())
        if old != canonical:
            raise RuntimeError("Frozen confirmation protocol differs from existing file")
    else:
        PROTOCOL.write_text(json.dumps(canonical, indent=2, sort_keys=True) + "\n")
    return canonical


def key(row: dict) -> tuple:
    return tuple(str(row[k]) for k in ("algorithm", "fid", "instance", "dimension", "seed", "budget"))


def done_keys() -> set[tuple]:
    if not LEDGER.exists():
        return set()
    return {key(r) for r in csv.DictReader(LEDGER.open())}


def append(row: dict) -> None:
    new = not LEDGER.exists()
    with LEDGER.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new:
            w.writeheader()
        w.writerow(row)
        f.flush()
        os.fsync(f.fileno())


def run_case(algorithm: str, fid: int, instance: int, seed: int) -> None:
    family, cfg = ALGORITHMS[algorithm]
    budget = BUDGET_D * DIMENSION
    obj = BudgetedBBOB(fid, instance, DIMENSION, budget)
    start = time.perf_counter()
    RUNNERS[family](obj, seed, cfg)
    wall = time.perf_counter() - start
    obj.fill_snapshots()
    objective_s = obj.objective_ns / 1e9
    row = {
        "phase": "confirmation",
        "algorithm": algorithm,
        "family": family,
        "fid": fid,
        "instance": instance,
        "dimension": DIMENSION,
        "seed": seed,
        "budget": budget,
        "nfev": obj.nfev,
        "error": f"{obj.error:.17g}",
        "hit_1e-2": obj.target_hits[1e-2] or "",
        "hit_1e-5": obj.target_hits[1e-5] or "",
        "err_20d": f"{obj.snapshots.get(20, math.nan):.17g}",
        "err_50d": f"{obj.snapshots.get(50, math.nan):.17g}",
        "err_100d": f"{obj.snapshots.get(100, math.nan):.17g}",
        "err_200d": f"{obj.snapshots.get(200, math.nan):.17g}",
        "wall_s": f"{wall:.9g}",
        "objective_s": f"{objective_s:.9g}",
        "overhead_us_per_eval": f"{max(0.0,wall-objective_s)*1e6/max(1,obj.nfev):.9g}",
        "config_json": json.dumps(cfg, sort_keys=True, separators=(",", ":")),
    }
    append(row)


def main() -> None:
    freeze_protocol()
    done = done_keys()
    planned = len(ALGORITHMS) * len(FUNCTIONS) * len(INSTANCES) * len(SEEDS)
    print(f"planned={planned} already_done={len(done)} budget={BUDGET_D}D")
    start = time.perf_counter()
    new = 0
    for algorithm in ALGORITHMS:
        for fid in FUNCTIONS:
            for instance in INSTANCES:
                for seed in SEEDS:
                    probe = {
                        "algorithm": algorithm, "fid": fid, "instance": instance,
                        "dimension": DIMENSION, "seed": seed, "budget": BUDGET_D * DIMENSION,
                    }
                    if key(probe) in done:
                        continue
                    run_case(algorithm, fid, instance, seed)
                    new += 1
                    if new % 20 == 0:
                        print(f"completed {new} new runs in {time.perf_counter()-start:.1f}s", flush=True)
    print(f"done new_runs={new} wall_s={time.perf_counter()-start:.2f}")


if __name__ == "__main__":
    main()

"""Live fresh-problem experiment for the SciPy India 2026 talk.

The audience chooses a quadratic problem. A prediction is durably committed
before the first objective call. The reveal compares the four frozen methods
at equal 50D/100D/200D objective-call milestones.

This is a demonstration of an operating regime, not a p2-wins demo.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

import numpy as np

from bench import BudgetExhausted, run_cma, run_lshade, run_scipy

MILESTONES_D = (50, 100, 200)
DEFAULT_LOG = Path.home() / ".cache/algorithm-discovery/live-runs.jsonl"

LIVE_ALGORITHMS: dict[str, tuple[str, dict]] = {
    "scipy-p15": ("scipy", {
        "strategy": "best1bin", "popsize": 15, "updating": "immediate",
        "init": "latinhypercube", "mutation": (0.5, 1.0), "recombination": 0.7,
    }),
    "scipy-p2": ("scipy", {
        "strategy": "best1bin", "popsize": 2, "updating": "immediate",
        "init": "halton", "mutation": (0.5, 1.0), "recombination": 0.7,
    }),
    "lshade-p2": ("lshade", {
        "lambda_per_d": 2, "bound_correction": "saturate",
    }),
    "cma-s30": ("cma", {
        "sigma_frac": 0.30, "popsize_mult": 1.0,
    }),
}
RUNNERS = {"scipy": run_scipy, "lshade": run_lshade, "cma": run_cma}


class _State:
    def __init__(self, owner):
        self.owner = owner

    @property
    def evaluations(self):
        return self.owner.nfev

    @property
    def optimum_found(self):
        return False


class FreshQuadratic:
    """Strict-budget shifted quadratic; hidden optimum is only used for scoring."""

    def __init__(self, d: int, condition: float, rotated: bool, seed: int, budget: int):
        rng = np.random.default_rng(seed)
        self.dimension = d
        self.lb = np.full(d, -5.0)
        self.ub = np.full(d, 5.0)
        self.__xopt = rng.uniform(-2.0, 2.0, d)
        q, _ = np.linalg.qr(rng.normal(size=(d, d)))
        self.__q = q if rotated else np.eye(d)
        self.__weights = np.geomspace(1.0, condition, d)
        self.budget = int(budget)
        self.nfev = 0
        self.best_y = math.inf
        self.best_x = None
        self.objective_ns = 0
        self.meta_data = SimpleNamespace(n_variables=d)
        self.state = _State(self)
        self.snapshots: dict[int, float] = {}

    def __call__(self, x):
        if self.nfev >= self.budget:
            raise BudgetExhausted
        start = time.perf_counter_ns()
        z = self.__q @ (np.asarray(x, dtype=float) - self.__xopt)
        y = float(np.dot(self.__weights, z * z))
        self.objective_ns += time.perf_counter_ns() - start
        self.nfev += 1
        if y < self.best_y:
            self.best_y = y
            self.best_x = np.asarray(x, dtype=float).copy()
        for md in MILESTONES_D:
            if self.nfev == md * self.dimension:
                self.snapshots[md] = self.best_y
        return y

    @property
    def error(self):
        return self.best_y

    def fill_snapshots(self):
        for md in MILESTONES_D:
            if md * self.dimension <= self.budget and md not in self.snapshots:
                self.snapshots[md] = self.best_y


def problem_key(d: int, condition: float, rotated: bool, seed: int) -> dict:
    return {
        "dimension": int(d),
        "condition": float(condition),
        "rotated": bool(rotated),
        "seed": int(seed),
    }


def canonical_hash(payload: dict) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(blob).hexdigest()


def load_prediction_problems(path: Path) -> set[str]:
    if not path.exists():
        return set()
    seen = set()
    with path.open() as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            if rec.get("type") == "prediction":
                seen.add(canonical_hash(rec["problem"]))
    return seen


def append_record(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as f:
        f.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")
        f.flush()
        os.fsync(f.fileno())


def commit_prediction(
    path: Path,
    problem: dict,
    algorithms: list[str],
    budget_d: int,
    prediction: str,
    allow_repeat: bool = False,
) -> str:
    fingerprint = canonical_hash(problem)
    if not allow_repeat and fingerprint in load_prediction_problems(path):
        raise SystemExit(
            "This exact problem already appears in the live log. "
            "Choose a fresh audience seed/settings, or pass --allow-repeat for rehearsal."
        )
    payload = {
        "type": "prediction",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "problem": problem,
        "algorithms": algorithms,
        "budget_d": int(budget_d),
        "prediction": prediction,
    }
    commitment = canonical_hash(payload)
    payload["commitment_sha256"] = commitment
    append_record(path, payload)
    return commitment


def main():
    p = argparse.ArgumentParser(
        description="Commit a prediction, then run a fresh equal-budget quadratic experiment."
    )
    p.add_argument("--dimension", type=int, choices=(5, 10, 20), required=True)
    p.add_argument("--condition", type=float, required=True)
    p.add_argument("--rotated", action=argparse.BooleanOptionalAction, default=True)
    p.add_argument("--seed", type=int, required=True, help="Audience-selected fresh problem seed.")
    p.add_argument("--budget-d", type=int, choices=(50, 100, 200), default=200)
    p.add_argument(
        "--prediction",
        required=True,
        help="Prediction stated aloud before computation. It may name any expected winner/ordering.",
    )
    p.add_argument(
        "--algorithms",
        nargs="+",
        choices=tuple(LIVE_ALGORITHMS),
        default=list(LIVE_ALGORITHMS),
    )
    p.add_argument("--log", type=Path, default=DEFAULT_LOG)
    p.add_argument(
        "--allow-repeat",
        action="store_true",
        help="Allow an already logged problem; use only for rehearsal/plumbing checks.",
    )
    args = p.parse_args()

    if args.condition < 1:
        raise SystemExit("--condition must be >= 1")

    problem = problem_key(args.dimension, args.condition, args.rotated, args.seed)
    commitment = commit_prediction(
        args.log, problem, args.algorithms, args.budget_d, args.prediction, args.allow_repeat
    )

    print(f"PREDICTION: {args.prediction}")
    print(f"COMMITMENT SHA256: {commitment}")
    print(
        f"PROBLEM: d={args.dimension}, condition={args.condition:g}, "
        f"rotated={args.rotated}, seed={args.seed}, budget={args.budget_d}D"
    )
    print(f"LOGGED BEFORE FIRST OBJECTIVE CALL: {args.log}", flush=True)

    results = []
    for index, name in enumerate(args.algorithms):
        family, cfg = LIVE_ALGORITHMS[name]
        obj = FreshQuadratic(
            args.dimension, args.condition, args.rotated, args.seed,
            args.budget_d * args.dimension,
        )
        start = time.perf_counter()
        RUNNERS[family](obj, 1000 + args.seed + index, cfg)
        wall = time.perf_counter() - start
        obj.fill_snapshots()
        results.append({
            "algorithm": name,
            "nfev": obj.nfev,
            "wall_s": wall,
            "snapshots": {str(md): obj.snapshots.get(md) for md in MILESTONES_D
                          if md <= args.budget_d},
        })

    print("\nREVEAL — lower error is better; every column uses the same NFE budget")
    header = ["algorithm"] + [f"{md}D" for md in MILESTONES_D if md <= args.budget_d]
    print("  ".join(f"{h:>14s}" for h in header))
    for row in results:
        vals = [row["algorithm"]]
        vals.extend(f"{row['snapshots'][str(md)]:.4g}" for md in MILESTONES_D if md <= args.budget_d)
        print("  ".join(f"{v:>14s}" for v in vals))

    winners = {}
    for md in MILESTONES_D:
        if md <= args.budget_d:
            winner = min(results, key=lambda r: r["snapshots"][str(md)])
            winners[str(md)] = winner["algorithm"]
    print("\nWINNERS BY BUDGET:", ", ".join(f"{md}D={name}" for md, name in winners.items()))

    outcome = {
        "type": "outcome",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "commitment_sha256": commitment,
        "problem": problem,
        "prediction": args.prediction,
        "budget_d": args.budget_d,
        "results": results,
        "winners": winners,
    }
    append_record(args.log, outcome)


if __name__ == "__main__":
    main()

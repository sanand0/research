"""Trace low-population best/1/bin DE one objective call at a time.

This is a diagnostic implementation, not a candidate optimizer. It exposes the
within-generation sequence that SciPy's public result/callback API does not.
The objective supplies values only; benchmark identity/optimum is never read.
"""
from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

import numpy as np
from scipy.stats import qmc

from bench import BudgetExhausted, BudgetedBBOB, PILOT_FUNCTIONS
from geometry_probe import quadratic


def _trial(pop: np.ndarray, vals: np.ndarray, i: int, scale: float, cr: float, rng: np.random.Generator,
           lb: np.ndarray, ub: np.ndarray) -> np.ndarray:
    n, d = pop.shape
    eligible = np.delete(np.arange(n), i)
    a, b = rng.choice(eligible, 2, replace=False)
    best = pop[int(np.argmin(vals))]
    donor = best + scale * (pop[int(a)] - pop[int(b)])
    mask = rng.random(d) < cr
    mask[rng.integers(d)] = True
    x = np.where(mask, donor, pop[i]).copy()
    bad = (x < lb) | (x > ub)
    if bad.any():
        x[bad] = rng.uniform(lb[bad], ub[bad])
    return x


def trace_de(obj, seed: int, problem: dict, budget_d: int = 200, pop_per_d: int = 2,
             cr: float = 0.7, mutation: tuple[float, float] = (0.5, 1.0)) -> list[dict]:
    d = obj.dimension
    n = pop_per_d * d
    rng = np.random.default_rng(seed)
    pop = qmc.scale(qmc.Halton(d, scramble=True, seed=seed).random(n), obj.lb, obj.ub)
    vals = np.array([obj(x) for x in pop])
    rows: list[dict] = []
    generation = 0
    while obj.nfev < budget_d * d:
        generation += 1
        scale = float(rng.uniform(*mutation))
        gen_start_best = float(vals.min())
        gen_start_median = float(np.median(vals))
        spread = max(abs(gen_start_median - gen_start_best), abs(gen_start_best), 1e-12)
        remaining = min(n, budget_d * d - obj.nfev)
        for pos, i in enumerate(range(remaining), start=1):
            parent_y = float(vals[i])
            best_before = float(vals.min())
            x = _trial(pop, vals, i, scale, cr, rng, obj.lb, obj.ub)
            y = float(obj(x))
            accepted = y <= parent_y
            parent_improvement = max(0.0, parent_y - y)
            if accepted:
                pop[i] = x
                vals[i] = y
            best_after = float(vals.min())
            rows.append({
                **problem,
                "seed": seed,
                "dimension": d,
                "budget_d": budget_d,
                "pop_per_d": pop_per_d,
                "population": n,
                "generation": generation,
                "position": pos,
                "generation_size": remaining,
                "F": scale,
                "CR": cr,
                "accepted": int(accepted),
                "parent_improvement": parent_improvement,
                "parent_improvement_norm": parent_improvement / spread,
                "incumbent_improvement": max(0.0, best_before - best_after),
                "incumbent_improvement_norm": max(0.0, best_before - best_after) / spread,
                "generation_start_best": gen_start_best,
            })
    return rows


class BudgetedQuadratic:
    def __init__(self, d: int, condition: float, rotated: bool, problem_seed: int, budget: int):
        self.h, self.center = quadratic(d, condition, rotated, problem_seed)
        self.dimension = d
        self.budget = budget
        self.nfev = 0
        self.lb = np.full(d, -5.0)
        self.ub = np.full(d, 5.0)
        self.best_y = math.inf

    def __call__(self, x):
        if self.nfev >= self.budget:
            raise BudgetExhausted
        e = np.asarray(x, float) - self.center
        y = float(e @ self.h @ e)
        self.nfev += 1
        self.best_y = min(self.best_y, y)
        return y


def split_for_bbob(fid: int, instance: int, seed: int) -> str | None:
    discovery = {1, 6, 10, 15, 20}
    validation = {3, 8, 12, 17, 23}
    if fid in discovery and instance == 1 and 1 <= seed <= 5:
        return "discovery"
    if fid in validation and instance == 2 and 6 <= seed <= 10:
        return "validation"
    return None


def generate_bbob(budget_d: int) -> list[dict]:
    out: list[dict] = []
    for fid in PILOT_FUNCTIONS:
        for instance in (1, 2):
            for d in (5, 10):
                for seed in range(1, 11):
                    split = split_for_bbob(fid, instance, seed)
                    if split is None:
                        continue
                    obj = BudgetedBBOB(fid, instance, d, budget_d * d)
                    out += trace_de(obj, seed, {
                        "suite": "bbob", "split": split, "fid": fid, "instance": instance,
                        "condition": "", "rotated": "",
                    }, budget_d)
    return out


def generate_synthetic(budget_d: int) -> list[dict]:
    out: list[dict] = []
    for d in (5, 10):
        for condition in (1.0, 100.0, 10_000.0):
            for rotated in (False, True):
                for seed in range(1, 11):
                    split = "discovery" if seed <= 5 else "validation"
                    problem_seed = 300_000 + 1000 * d + int(condition) + 100 * int(rotated) + seed
                    obj = BudgetedQuadratic(d, condition, rotated, problem_seed, budget_d * d)
                    out += trace_de(obj, seed, {
                        "suite": "quadratic", "split": split, "fid": "", "instance": problem_seed,
                        "condition": condition, "rotated": int(rotated),
                    }, budget_d)
    return out


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path, default=Path.home() / ".cache/algorithm-discovery/generation-trials.csv")
    p.add_argument("--budget-d", type=int, default=200)
    args = p.parse_args()
    rows = generate_bbob(args.budget_d) + generate_synthetic(args.budget_d)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0])
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {len(rows)} trial rows to {args.output}")


if __name__ == "__main__":
    main()

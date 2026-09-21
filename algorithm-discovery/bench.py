"""Strict-budget BBOB benchmark harness for compact optimizer experiments."""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import time
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Callable

import cma
import ioh
import numpy as np
from modde.modularde import ModularDE
from scipy.optimize import differential_evolution, direct
from scipy.stats import qmc

from candidate import BalancedAntitheticBest1, PrefixResampleBest1, conditioned_halton_population, run_sequential_best1, RejectionWhitenedBest1

TARGETS = (1e-2, 1e-5)
MILESTONES_D = (20, 50, 100, 200)
TUNE_FUNCTIONS = (1, 6, 10, 15, 20)
PILOT_FUNCTIONS = (1, 3, 6, 8, 10, 12, 15, 17, 20, 23)


class BudgetExhausted(RuntimeError):
    """Raised before an objective call that would exceed the strict budget."""


class _StateView:
    def __init__(self, owner: "BudgetedBBOB") -> None:
        self.owner = owner

    @property
    def evaluations(self) -> int:
        return self.owner.nfev

    @property
    def optimum_found(self) -> bool:
        # Do not expose IOH's target/solution status to an optimizer.
        return False


class BudgetedBBOB:
    """BBOB callable that exposes only dimension/state needed by modDE.

    Optimum information is retained privately for post-run scoring but is never
    passed to an optimizer. Calls beyond the budget raise before IOH is invoked.
    """

    def __init__(self, fid: int, instance: int, dimension: int, budget: int) -> None:
        self._problem = ioh.get_problem(fid, instance, dimension)
        self._fopt = float(self._problem.optimum.y)
        self.budget = int(budget)
        self.nfev = 0
        self.best_y = math.inf
        self.best_x: np.ndarray | None = None
        self.objective_ns = 0
        self.target_hits: dict[float, int | None] = {t: None for t in TARGETS}
        self.snapshots: dict[int, float] = {}
        self.meta_data = SimpleNamespace(n_variables=dimension)
        self.state = _StateView(self)
        self.dimension = dimension
        self.lb = np.full(dimension, -5.0)
        self.ub = np.full(dimension, 5.0)

    def __call__(self, x: np.ndarray) -> float:
        if self.nfev >= self.budget:
            raise BudgetExhausted
        x = np.asarray(x, dtype=float)
        start = time.perf_counter_ns()
        y = float(self._problem(x))
        self.objective_ns += time.perf_counter_ns() - start
        self.nfev += 1
        if y < self.best_y:
            self.best_y = y
            self.best_x = x.copy()
        error = max(0.0, self.best_y - self._fopt)
        for target in TARGETS:
            if self.target_hits[target] is None and error <= target:
                self.target_hits[target] = self.nfev
        for md in MILESTONES_D:
            m = md * self.dimension
            if self.nfev == m:
                self.snapshots[md] = error
        return y

    @property
    def error(self) -> float:
        return max(0.0, self.best_y - self._fopt)

    def fill_snapshots(self) -> None:
        # Early termination means the incumbent would remain unchanged if we
        # score at a later fixed budget without granting extra evaluations.
        for md in MILESTONES_D:
            if md * self.dimension <= self.budget and md not in self.snapshots:
                self.snapshots[md] = self.error


def run_scipy(obj: BudgetedBBOB, seed: int, cfg: dict) -> None:
    init = cfg.get("init", "latinhypercube")
    if cfg.get("init_size") == "d+1":
        init = qmc.scale(qmc.Halton(obj.dimension, scramble=True, seed=seed).random(obj.dimension + 1), obj.lb, obj.ub)
    elif cfg.get("init_size") == "2d":
        init = qmc.scale(qmc.Halton(obj.dimension, scramble=True, seed=seed).random(2 * obj.dimension), obj.lb, obj.ub)
    elif cfg.get("init_size") == "conditioned":
        init = conditioned_halton_population(
            obj.dimension, obj.lb, obj.ub, seed,
            condition_limit=cfg.get("condition_limit", 20.0),
            max_per_d=cfg.get("max_per_d", 4),
        )
    kwargs = dict(
        func=obj,
        bounds=list(zip(obj.lb, obj.ub, strict=True)),
        strategy=cfg["strategy"],
        popsize=cfg.get("popsize", 1),
        mutation=cfg.get("mutation", (0.5, 1.0)),
        recombination=cfg.get("recombination", 0.7),
        init=init,
        updating=cfg.get("updating", "immediate"),
        rng=seed,
        tol=0.0,
        atol=0.0,
        polish=False,
        workers=1,
        maxiter=10**9,
    )
    try:
        differential_evolution(**kwargs)
    except BudgetExhausted:
        pass


def run_pairde(obj: BudgetedBBOB, seed: int, cfg: dict) -> None:
    strategy = BalancedAntitheticBest1(
        mutation=cfg.get("mutation", (0.5, 1.0)),
        recombination=cfg.get("recombination", 0.7),
    )
    pair_cfg = dict(cfg)
    pair_cfg["strategy"] = strategy
    pair_cfg["updating"] = "deferred"
    run_scipy(obj, seed, pair_cfg)



def _point_key(x: np.ndarray) -> bytes:
    return np.round(np.asarray(x, dtype=float), 12).tobytes()


def run_rejde(obj: BudgetedBBOB, seed: int, cfg: dict) -> None:
    """Run rejection-whitened DE through SciPy's public strategy/vectorized APIs."""
    strategy = RejectionWhitenedBest1(
        obj.dimension, obj.ub - obj.lb,
        mutation=cfg.get("mutation", (0.5, 1.0)),
        recombination=cfg.get("recombination", 0.7),
        active=cfg.get("active", True),
    )
    known: dict[bytes, float] = {}

    def vector_objective(x: np.ndarray) -> np.ndarray:
        points = np.asarray(x, dtype=float).T
        if points.ndim == 1:
            points = points[None, :]
        pending = len(strategy.pending_parents) == len(points) and len(points) > 0
        parent_values = None
        if pending:
            try:
                parent_values = np.array([known[_point_key(p)] for p in strategy.pending_parents])
            except KeyError as exc:
                raise RuntimeError("SciPy strategy parent was not found in evaluated-point history") from exc
        values = np.array([obj(point) for point in points])
        for point, value in zip(points, values, strict=True):
            known[_point_key(point)] = float(value)
        if pending and parent_values is not None:
            strategy.observe_batch(points, values, parent_values)
        return values

    try:
        differential_evolution(
            func=vector_objective,
            bounds=list(zip(obj.lb, obj.ub, strict=True)),
            strategy=strategy,
            popsize=cfg["popsize"],
            init=cfg.get("init", "latinhypercube"),
            updating="deferred",
            vectorized=True,
            rng=seed,
            tol=0.0, atol=0.0, polish=False, workers=1, maxiter=10**9,
        )
    except BudgetExhausted:
        pass

def run_switchf(obj: BudgetedBBOB, seed: int, cfg: dict) -> None:
    strategy = PrefixResampleBest1(
        mutation=cfg.get("mutation", (0.5, 1.0)),
        recombination=cfg.get("recombination", 0.7),
        active=cfg.get("active", True),
        switch_fraction=cfg.get("switch_fraction", 0.25),
    )
    run_scipy(obj, seed, {
        "strategy": strategy, "popsize": cfg.get("popsize", 2),
        "mutation": 0.5,  # ignored by callable strategy
        "recombination": cfg.get("recombination", 0.7),
        "init": cfg.get("init", "halton"), "updating": "immediate",
    })


def run_seqde(obj: BudgetedBBOB, seed: int, cfg: dict) -> dict[str, int]:
    return run_sequential_best1(
        obj,
        seed,
        pop_per_d=cfg.get("pop_per_d", 2),
        mutation=cfg.get("mutation", (0.5, 1.0)),
        recombination=cfg.get("recombination", 0.7),
        active=cfg.get("active", True),
        abort_fraction=cfg.get("abort_fraction", 0.25),
    )


def run_direct(obj: BudgetedBBOB, seed: int, cfg: dict) -> None:
    # DIRECT is deterministic; seed is accepted by the harness only for a
    # uniform run schema. The evaluator remains the authoritative budget.
    try:
        direct(
            obj,
            bounds=list(zip(obj.lb, obj.ub, strict=True)),
            maxfun=obj.budget,
            maxiter=10**9,
            locally_biased=cfg.get("locally_biased", True),
            eps=cfg.get("eps", 1e-4),
        )
    except BudgetExhausted:
        pass


def run_cma(obj: BudgetedBBOB, seed: int, cfg: dict) -> None:
    rng = np.random.default_rng(seed)
    x0 = rng.uniform(obj.lb, obj.ub)
    sigma0 = cfg["sigma_frac"] * float(obj.ub[0] - obj.lb[0])
    opts: dict = {
        "bounds": [obj.lb.tolist(), obj.ub.tolist()],
        "seed": seed,
        "verbose": -9,
        "verb_log": 0,
        "maxfevals": 10**12,
    }
    if cfg.get("popsize_mult", 1.0) != 1.0:
        default_pop = 4 + int(3 * np.log(obj.dimension))
        opts["popsize"] = max(4, int(round(default_pop * cfg["popsize_mult"])))
    es = cma.CMAEvolutionStrategy(x0, sigma0, opts)
    while obj.nfev < obj.budget and not es.stop():
        xs = es.ask()
        ys = []
        complete = True
        for x in xs:
            try:
                ys.append(obj(x))
            except BudgetExhausted:
                complete = False
                break
        if not complete:
            break
        es.tell(xs, ys)


def run_lshade(obj: BudgetedBBOB, seed: int, cfg: dict) -> None:
    lambda_ = max(8, int(round(cfg["lambda_per_d"] * obj.dimension)))
    try:
        alg = ModularDE(
            obj,
            base_sampler="uniform",
            mutation_base="target",
            mutation_reference="pbest",
            bound_correction=cfg.get("bound_correction", "saturate"),
            crossover="bin",
            lpsr=True,
            lambda_=lambda_,
            memory_size=6,
            use_archive=True,
            init_stats=False,
            adaptation_method_F="shade",
            adaptation_method_CR="shade",
            budget=obj.budget,
            lb=obj.lb.reshape(-1, 1),
            ub=obj.ub.reshape(-1, 1),
            seed=seed,
        )
        alg.run()
    except BudgetExhausted:
        pass


BASELINE_CONFIGS: dict[str, tuple[str, dict]] = {
    "scipy-best-p5-immediate": ("scipy", {"strategy": "best1bin", "popsize": 5, "updating": "immediate"}),
    "scipy-best-p5-deferred": ("scipy", {"strategy": "best1bin", "popsize": 5, "updating": "deferred"}),
    "scipy-currentbest-p5": ("scipy", {"strategy": "currenttobest1bin", "popsize": 5, "updating": "immediate"}),
    "scipy-rand-p5": ("scipy", {"strategy": "rand1bin", "popsize": 5, "updating": "immediate"}),
    "scipy-best-p10": ("scipy", {"strategy": "best1bin", "popsize": 10, "updating": "immediate"}),
    "scipy-best-p5-halton": ("scipy", {"strategy": "best1bin", "popsize": 5, "updating": "immediate", "init": "halton"}),
    "scipy-best-p5-halton-cr1": ("scipy", {"strategy": "best1bin", "popsize": 5, "updating": "immediate", "init": "halton", "recombination": 1.0}),
    "scipy-best-p1-halton": ("scipy", {"strategy": "best1bin", "popsize": 1, "updating": "immediate", "init": "halton"}),
    "scipy-best-dplus1-halton": ("scipy", {"strategy": "best1bin", "updating": "immediate", "init_size": "d+1"}),
    "scipy-best-custom2d-halton": ("scipy", {"strategy": "best1bin", "updating": "immediate", "init_size": "2d"}),
    "condinit20-halton": ("scipy", {"strategy": "best1bin", "updating": "immediate", "init_size": "conditioned", "condition_limit": 20.0, "max_per_d": 4}),
    "scipy-best-p2-halton": ("scipy", {"strategy": "best1bin", "popsize": 2, "updating": "immediate", "init": "halton"}),
    "scipy-best-p2-halton-cr05": ("scipy", {"strategy": "best1bin", "popsize": 2, "updating": "immediate", "init": "halton", "recombination": 0.5}),
    "scipy-best-p2-halton-cr09": ("scipy", {"strategy": "best1bin", "popsize": 2, "updating": "immediate", "init": "halton", "recombination": 0.9}),
    "scipy-best-p2-halton-f70": ("scipy", {"strategy": "best1bin", "popsize": 2, "updating": "immediate", "init": "halton", "mutation": 0.7}),
    "scipy-best-p3-halton": ("scipy", {"strategy": "best1bin", "popsize": 3, "updating": "immediate", "init": "halton"}),
    "scipy-best-p2-halton-cr1": ("scipy", {"strategy": "best1bin", "popsize": 2, "updating": "immediate", "init": "halton", "recombination": 1.0}),
    "scipy-best-p3-halton-cr1": ("scipy", {"strategy": "best1bin", "popsize": 3, "updating": "immediate", "init": "halton", "recombination": 1.0}),
    "scipy-best-p5-halton-cr1-f35": ("scipy", {"strategy": "best1bin", "popsize": 5, "updating": "immediate", "init": "halton", "recombination": 1.0, "mutation": 0.35}),
    "scipy-best-p5-halton-cr1-f70": ("scipy", {"strategy": "best1bin", "popsize": 5, "updating": "immediate", "init": "halton", "recombination": 1.0, "mutation": 0.7}),
    "scipy-best-p5-halton-deferred": ("scipy", {"strategy": "best1bin", "popsize": 5, "updating": "deferred", "init": "halton"}),
    "pairde-p5-halton": ("pairde", {"popsize": 5, "init": "halton", "mutation": (0.5, 1.0), "recombination": 0.7}),
    "rejde-p5-halton": ("rejde", {"popsize": 5, "init": "halton", "mutation": (0.5, 1.0), "recombination": 0.7, "active": True}),
    "rejde-off-p5-halton": ("rejde", {"popsize": 5, "init": "halton", "mutation": (0.5, 1.0), "recombination": 0.7, "active": False}),
    "seqde-off-p2-halton": ("seqde", {"pop_per_d": 2, "mutation": (0.5, 1.0), "recombination": 0.7, "active": False}),
    "seqde-quarter-p2-halton": ("seqde", {"pop_per_d": 2, "mutation": (0.5, 1.0), "recombination": 0.7, "active": True, "abort_fraction": 0.25}),
    "switchf-off-p2-halton": ("switchf", {"popsize": 2, "init": "halton", "mutation": (0.5, 1.0), "recombination": 0.7, "active": False}),
    "switchf-quarter-p2-halton": ("switchf", {"popsize": 2, "init": "halton", "mutation": (0.5, 1.0), "recombination": 0.7, "active": True, "switch_fraction": 0.25}),
    "cma-s10": ("cma", {"sigma_frac": 0.10, "popsize_mult": 1.0}),
    "direct-local": ("direct", {"locally_biased": True, "eps": 1e-4}),
    "direct-global": ("direct", {"locally_biased": False, "eps": 1e-4}),
    "cma-s20": ("cma", {"sigma_frac": 0.20, "popsize_mult": 1.0}),
    "cma-s50": ("cma", {"sigma_frac": 0.50, "popsize_mult": 1.0}),
    "cma-s30": ("cma", {"sigma_frac": 0.30, "popsize_mult": 1.0}),
    "cma-s20-p2": ("cma", {"sigma_frac": 0.20, "popsize_mult": 2.0}),
    "modde-lshade-p1": ("lshade", {"lambda_per_d": 1, "bound_correction": "saturate"}),
    "modde-lshade-p2": ("lshade", {"lambda_per_d": 2, "bound_correction": "saturate"}),
    "modde-lshade-p3": ("lshade", {"lambda_per_d": 3, "bound_correction": "saturate"}),
    "modde-lshade-p4": ("lshade", {"lambda_per_d": 4, "bound_correction": "saturate"}),
    "modde-lshade-p6": ("lshade", {"lambda_per_d": 6, "bound_correction": "saturate"}),
    "modde-lshade-p10": ("lshade", {"lambda_per_d": 10, "bound_correction": "saturate"}),
    "modde-lshade-p18": ("lshade", {"lambda_per_d": 18, "bound_correction": "saturate"}),
}

RUNNERS: dict[str, Callable[[BudgetedBBOB, int, dict], None]] = {
    "scipy": run_scipy,
    "pairde": run_pairde,
    "rejde": run_rejde,
    "seqde": run_seqde,
    "switchf": run_switchf,
    "cma": run_cma,
    "direct": run_direct,
    "lshade": run_lshade,
}

FIELDS = [
    "phase", "algorithm", "family", "fid", "instance", "dimension", "seed", "budget",
    "nfev", "error", "hit_1e-2", "hit_1e-5", "err_20d", "err_50d", "err_100d", "err_200d",
    "wall_s", "objective_s", "overhead_us_per_eval", "config_json",
]


def key(row: dict) -> tuple:
    return tuple(row[k] for k in ("phase", "algorithm", "fid", "instance", "dimension", "seed", "budget"))


def load_done(path: Path) -> set[tuple]:
    if not path.exists():
        return set()
    with path.open(newline="") as f:
        return {key(r) for r in csv.DictReader(f)}


def append_row(path: Path, row: dict) -> None:
    new = not path.exists()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new:
            w.writeheader()
        w.writerow(row)
        f.flush()
        os.fsync(f.fileno())


def run_case(path: Path, phase: str, algorithm: str, fid: int, instance: int, d: int, seed: int, budget_d: int) -> None:
    family, cfg = BASELINE_CONFIGS[algorithm]
    budget = budget_d * d
    obj = BudgetedBBOB(fid, instance, d, budget)
    start = time.perf_counter()
    RUNNERS[family](obj, seed, cfg)
    wall_s = time.perf_counter() - start
    obj.fill_snapshots()
    objective_s = obj.objective_ns / 1e9
    overhead_us = max(0.0, wall_s - objective_s) * 1e6 / max(1, obj.nfev)
    row = {
        "phase": phase,
        "algorithm": algorithm,
        "family": family,
        "fid": fid,
        "instance": instance,
        "dimension": d,
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
        "wall_s": f"{wall_s:.9g}",
        "objective_s": f"{objective_s:.9g}",
        "overhead_us_per_eval": f"{overhead_us:.9g}",
        "config_json": json.dumps(cfg, sort_keys=True, separators=(",", ":")),
    }
    append_row(path, row)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("tune", "pilot"), required=True)
    parser.add_argument("--ledger", type=Path, default=Path("results/runs.csv"))
    parser.add_argument("--algorithms", nargs="*", default=list(BASELINE_CONFIGS))
    parser.add_argument("--budget-d", type=int, default=200)
    args = parser.parse_args()

    unknown = sorted(set(args.algorithms) - BASELINE_CONFIGS.keys())
    if unknown:
        raise SystemExit(f"Unknown algorithms: {unknown}")
    functions = TUNE_FUNCTIONS if args.phase == "tune" else PILOT_FUNCTIONS
    instances = (1,) if args.phase == "tune" else (1, 2)
    dimensions = (5, 10)
    seeds = (1, 2)
    done = load_done(args.ledger)
    planned = len(args.algorithms) * len(functions) * len(instances) * len(dimensions) * len(seeds)
    print(f"phase={args.phase} planned={planned} already_done={len(done)} budget={args.budget_d}D", flush=True)
    started = time.perf_counter()
    n = 0
    for algorithm in args.algorithms:
        for fid in functions:
            for instance in instances:
                for d in dimensions:
                    for seed in seeds:
                        probe = {
                            "phase": args.phase, "algorithm": algorithm, "fid": str(fid), "instance": str(instance),
                            "dimension": str(d), "seed": str(seed), "budget": str(args.budget_d * d),
                        }
                        # CSV-loaded keys are strings; fresh keys are normalized likewise.
                        if key(probe) in done:
                            continue
                        run_case(args.ledger, args.phase, algorithm, fid, instance, d, seed, args.budget_d)
                        n += 1
                        if n % 20 == 0:
                            print(f"completed {n} new runs in {time.perf_counter()-started:.1f}s", flush=True)
    print(f"done new_runs={n} wall_s={time.perf_counter()-started:.2f}", flush=True)


if __name__ == "__main__":
    main()

"""Scientific transfer benchmark: oral two-compartment PK parameter fitting.

Five fitted parameters: ka, CL, Vc, Q, Vp. The optimizer works in a normalized
[0,1]^5 box mapped logarithmically to physical parameters. Synthetic data are
noiseless and generated from independently known truth.

The fast simulator uses the exact matrix exponential of the linear ODE system.
The verification function independently checks it against scipy.integrate.solve_ivp.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import statistics
import time
from pathlib import Path
from types import SimpleNamespace

import numpy as np
from scipy.integrate import solve_ivp
from scipy.linalg import expm
from scipy.stats import qmc

from bench import BudgetExhausted, run_cma, run_lshade, run_scipy

DIMENSION = 5
DOSE_MG = 100.0
TIMES_H = np.array([0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0, 8.0, 12.0, 16.0, 24.0, 36.0, 48.0])
PARAM_NAMES = ("ka", "CL", "Vc", "Q", "Vp")
PHYSICAL_BOUNDS = np.array([
    [0.4, 4.0],
    [0.5, 5.0],
    [5.0, 30.0],
    [0.5, 6.0],
    [10.0, 80.0],
], dtype=float)
OBJECTIVE_TARGETS = (1e-4, 1e-6)
PARAM_TARGETS = (0.05, 0.01)
MILESTONES_D = (50, 100, 200)

ALGORITHMS: dict[str, tuple[str, dict]] = {
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

PROTOCOL = Path("results/pk-protocol.json")
LEDGER = Path("results/pk-runs.csv")
SUMMARY = Path("results/pk-summary.json")


def to_physical(u: np.ndarray) -> np.ndarray:
    u = np.asarray(u, dtype=float)
    lo = np.log(PHYSICAL_BOUNDS[:, 0])
    hi = np.log(PHYSICAL_BOUNDS[:, 1])
    return np.exp(lo + u * (hi - lo))


def system_matrix(theta: np.ndarray) -> np.ndarray:
    ka, cl, vc, q, vp = map(float, theta)
    return np.array([
        [-ka, 0.0, 0.0],
        [ka, -(cl + q) / vc, q / vp],
        [0.0, q / vc, -q / vp],
    ])


def simulate_expm(theta: np.ndarray, times: np.ndarray = TIMES_H) -> np.ndarray:
    m = system_matrix(theta)
    y0 = np.array([DOSE_MG, 0.0, 0.0])
    vc = float(theta[2])
    return np.array([(expm(m * float(t)) @ y0)[1] / vc for t in times])


def simulate_ivp(theta: np.ndarray, times: np.ndarray = TIMES_H) -> np.ndarray:
    ka, cl, vc, q, vp = map(float, theta)

    def rhs(_t, y):
        depot, central, peripheral = y
        return [
            -ka * depot,
            ka * depot - (cl + q) / vc * central + q / vp * peripheral,
            q / vc * central - q / vp * peripheral,
        ]

    sol = solve_ivp(
        rhs, (0.0, float(times[-1])), [DOSE_MG, 0.0, 0.0],
        t_eval=times, method="DOP853", rtol=1e-11, atol=1e-13,
    )
    if not sol.success:
        raise RuntimeError(sol.message)
    return sol.y[1] / vc


def make_protocol() -> dict:
    sobol = qmc.Sobol(DIMENSION, scramble=True, seed=20260920)
    unit = 0.15 + 0.70 * sobol.random_base2(m=3)
    subjects = []
    for i, u in enumerate(unit, start=1):
        theta = to_physical(u)
        subjects.append({
            "subject": i,
            "unit_truth": [float(x) for x in u],
            "physical_truth": {name: float(value) for name, value in zip(PARAM_NAMES, theta, strict=True)},
        })
    protocol = {
        "dimension": DIMENSION,
        "dose_mg": DOSE_MG,
        "times_h": [float(x) for x in TIMES_H],
        "parameter_names": list(PARAM_NAMES),
        "physical_bounds": {name: [float(a), float(b)] for name, (a, b) in zip(PARAM_NAMES, PHYSICAL_BOUNDS, strict=True)},
        "truth_design": "scrambled Sobol seed=20260920, central 70% of each log-bound",
        "noise": "none",
        "objective": "mean squared natural-log concentration error",
        "objective_targets": list(OBJECTIVE_TARGETS),
        "parameter_error": "RMS natural-log fitted/truth ratio",
        "parameter_targets": list(PARAM_TARGETS),
        "budget_multipliers": list(MILESTONES_D),
        "optimizer_seeds": [1, 2, 3],
        "algorithms": ALGORITHMS,
        "subjects": subjects,
    }
    PROTOCOL.parent.mkdir(parents=True, exist_ok=True)
    PROTOCOL.write_text(json.dumps(protocol, indent=2, sort_keys=True) + "\n")
    return protocol


def verify_simulator(protocol: dict) -> dict:
    checks = []
    candidates = [np.array(list(s["physical_truth"].values()), float) for s in protocol["subjects"]]
    rng = np.random.default_rng(20260920)
    candidates += [to_physical(rng.uniform(0.05, 0.95, DIMENSION)) for _ in range(8)]
    for theta in candidates:
        a = simulate_expm(theta)
        b = simulate_ivp(theta)
        abs_err = float(np.max(np.abs(a - b)))
        rel_err = float(np.max(np.abs(a - b) / np.maximum(np.abs(b), 1e-12)))
        checks.append((abs_err, rel_err))
    out = {
        "cases": len(checks),
        "max_abs_concentration_error": max(x[0] for x in checks),
        "max_rel_concentration_error": max(x[1] for x in checks),
    }
    Path("results/pk-simulator-check.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    return out


class _PKState:
    def __init__(self, owner: "BudgetedPK") -> None:
        self.owner = owner

    @property
    def evaluations(self) -> int:
        return self.owner.nfev

    @property
    def optimum_found(self) -> bool:
        return False


class BudgetedPK:
    def __init__(self, truth_u: np.ndarray, budget: int):
        self.truth_u = np.asarray(truth_u, float)
        self.truth_theta = to_physical(self.truth_u)
        self.observed = simulate_expm(self.truth_theta)
        self.dimension = DIMENSION
        self.budget = int(budget)
        self.nfev = 0
        self.lb = np.zeros(DIMENSION)
        self.ub = np.ones(DIMENSION)
        self.best_y = math.inf
        self.best_x: np.ndarray | None = None
        self.objective_ns = 0
        self.meta_data = SimpleNamespace(n_variables=DIMENSION)
        self.state = _PKState(self)
        self.objective_hits = {t: None for t in OBJECTIVE_TARGETS}
        self.parameter_hits = {t: None for t in PARAM_TARGETS}
        self.snapshots: dict[int, dict] = {}

    def parameter_error(self, x: np.ndarray | None = None) -> float:
        if x is None:
            x = self.best_x
        if x is None:
            return math.inf
        theta = to_physical(x)
        return float(np.sqrt(np.mean(np.log(theta / self.truth_theta) ** 2)))

    def __call__(self, x: np.ndarray) -> float:
        if self.nfev >= self.budget:
            raise BudgetExhausted
        x = np.asarray(x, float)
        theta = to_physical(x)
        start = time.perf_counter_ns()
        pred = simulate_expm(theta)
        residual = np.log(np.maximum(pred, 1e-300)) - np.log(np.maximum(self.observed, 1e-300))
        y = float(np.mean(residual**2))
        self.objective_ns += time.perf_counter_ns() - start
        self.nfev += 1
        if y < self.best_y:
            self.best_y = y
            self.best_x = x.copy()
        pe = self.parameter_error()
        for target in OBJECTIVE_TARGETS:
            if self.objective_hits[target] is None and self.best_y <= target:
                self.objective_hits[target] = self.nfev
        for target in PARAM_TARGETS:
            if self.parameter_hits[target] is None and pe <= target:
                self.parameter_hits[target] = self.nfev
        for md in MILESTONES_D:
            if self.nfev == md * DIMENSION:
                self.snapshots[md] = {
                    "objective": self.best_y,
                    "parameter_error": pe,
                    "best_x": self.best_x.tolist() if self.best_x is not None else None,
                }
        return y

    def fill_snapshots(self) -> None:
        for md in MILESTONES_D:
            if md * DIMENSION <= self.budget and md not in self.snapshots:
                self.snapshots[md] = {
                    "objective": self.best_y,
                    "parameter_error": self.parameter_error(),
                    "best_x": self.best_x.tolist() if self.best_x is not None else None,
                }


FIELDS = [
    "algorithm", "family", "subject", "seed", "budget", "nfev",
    "obj_50d", "obj_100d", "obj_200d", "param_50d", "param_100d", "param_200d",
    "hit_obj_1e-4", "hit_obj_1e-6", "hit_param_005", "hit_param_001",
    "final_objective", "final_parameter_error", "best_x_json",
    "wall_s", "objective_s", "overhead_us_per_eval", "config_json",
]


def _key(r: dict) -> tuple:
    return tuple(str(r[k]) for k in ("algorithm", "subject", "seed", "budget"))


def load_done() -> set[tuple]:
    if not LEDGER.exists():
        return set()
    return {_key(r) for r in csv.DictReader(LEDGER.open())}


def append_row(row: dict) -> None:
    new = not LEDGER.exists()
    with LEDGER.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new:
            w.writeheader()
        w.writerow(row)
        f.flush()
        os.fsync(f.fileno())


def run_case(algorithm: str, subject: dict, seed: int, budget_d: int = 200) -> None:
    family, cfg = ALGORITHMS[algorithm]
    obj = BudgetedPK(np.asarray(subject["unit_truth"], float), budget_d * DIMENSION)
    start = time.perf_counter()
    RUNNERS[family](obj, seed, cfg)
    wall = time.perf_counter() - start
    obj.fill_snapshots()
    objective_s = obj.objective_ns / 1e9

    def sv(md, field):
        return obj.snapshots.get(md, {}).get(field, math.nan)

    row = {
        "algorithm": algorithm, "family": family, "subject": subject["subject"], "seed": seed,
        "budget": budget_d * DIMENSION, "nfev": obj.nfev,
        "obj_50d": f"{sv(50, 'objective'):.17g}", "obj_100d": f"{sv(100, 'objective'):.17g}", "obj_200d": f"{sv(200, 'objective'):.17g}",
        "param_50d": f"{sv(50, 'parameter_error'):.17g}", "param_100d": f"{sv(100, 'parameter_error'):.17g}", "param_200d": f"{sv(200, 'parameter_error'):.17g}",
        "hit_obj_1e-4": obj.objective_hits[1e-4] or "", "hit_obj_1e-6": obj.objective_hits[1e-6] or "",
        "hit_param_005": obj.parameter_hits[0.05] or "", "hit_param_001": obj.parameter_hits[0.01] or "",
        "final_objective": f"{obj.best_y:.17g}", "final_parameter_error": f"{obj.parameter_error():.17g}",
        "best_x_json": json.dumps(obj.best_x.tolist() if obj.best_x is not None else None, separators=(",", ":")),
        "wall_s": f"{wall:.9g}", "objective_s": f"{objective_s:.9g}",
        "overhead_us_per_eval": f"{max(0.0, wall-objective_s)*1e6/max(1,obj.nfev):.9g}",
        "config_json": json.dumps(cfg, sort_keys=True, separators=(",", ":")),
    }
    append_row(row)


def summarize(protocol: dict) -> dict:
    rows = list(csv.DictReader(LEDGER.open()))
    out = {"runs": len(rows), "algorithms": {}, "problem_unit_comparisons": {}}
    for alg in ALGORITHMS:
        rs = [r for r in rows if r["algorithm"] == alg]
        item = {
            "runs": len(rs),
            "success_obj_1e-4": sum(bool(r["hit_obj_1e-4"]) for r in rs),
            "success_obj_1e-6": sum(bool(r["hit_obj_1e-6"]) for r in rs),
            "success_param_005": sum(bool(r["hit_param_005"]) for r in rs),
            "success_param_001": sum(bool(r["hit_param_001"]) for r in rs),
            "median_overhead_us_per_eval": statistics.median(float(r["overhead_us_per_eval"]) for r in rs),
        }
        for md in MILESTONES_D:
            item[f"median_log10_obj_{md}d"] = statistics.median(math.log10(max(float(r[f"obj_{md}d"]), 1e-16)) for r in rs)
            item[f"median_param_error_{md}d"] = statistics.median(float(r[f"param_{md}d"]) for r in rs)
        out["algorithms"][alg] = item

    units = {}
    for alg in ALGORITHMS:
        units[alg] = {}
        for subject in range(1, len(protocol["subjects"]) + 1):
            rs = [r for r in rows if r["algorithm"] == alg and int(r["subject"]) == subject]
            units[alg][subject] = {
                md: statistics.median(math.log10(max(float(r[f"obj_{md}d"]), 1e-16)) for r in rs)
                for md in MILESTONES_D
            }
    base = units["scipy-default-p15"]
    for alg in ("scipy-p2-halton", "lshade-p2", "cma-s30"):
        out["problem_unit_comparisons"][f"{alg}_vs_default"] = {}
        for md in MILESTONES_D:
            vals = [base[s][md] - units[alg][s][md] for s in sorted(base)]
            out["problem_unit_comparisons"][f"{alg}_vs_default"][str(md)] = {
                "median_log10_advantage": statistics.median(vals),
                "mean_log10_advantage": statistics.mean(vals),
                "wins": sum(v > 0 for v in vals),
                "subjects": len(vals),
            }
    SUMMARY.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    return out


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--verify-only", action="store_true")
    p.add_argument("--budget-d", type=int, default=200)
    args = p.parse_args()

    protocol = make_protocol()
    check = verify_simulator(protocol)
    print("simulator_check", json.dumps(check, sort_keys=True))
    if args.verify_only:
        return

    done = load_done()
    planned = len(ALGORITHMS) * len(protocol["subjects"]) * len(protocol["optimizer_seeds"])
    print(f"planned={planned} already_done={len(done)} budget={args.budget_d}D", flush=True)
    started = time.perf_counter()
    new = 0
    for algorithm in ALGORITHMS:
        for subject in protocol["subjects"]:
            for seed in protocol["optimizer_seeds"]:
                probe = {"algorithm": algorithm, "subject": subject["subject"], "seed": seed, "budget": args.budget_d * DIMENSION}
                if _key(probe) in done:
                    continue
                run_case(algorithm, subject, seed, args.budget_d)
                new += 1
                if new % 12 == 0:
                    print(f"completed {new} new runs in {time.perf_counter()-started:.1f}s", flush=True)
    print(f"done new_runs={new} wall_s={time.perf_counter()-started:.2f}")
    print(json.dumps(summarize(protocol), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

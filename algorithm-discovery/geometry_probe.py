"""Test whether ordinary rejected DE trials contain recoverable curvature information."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np
from scipy.stats import qmc, spearmanr


def quadratic(d: int, condition: float, rotated: bool, seed: int):
    rng = np.random.default_rng(seed)
    eig = np.geomspace(1.0, condition, d)
    if rotated:
        q, _ = np.linalg.qr(rng.normal(size=(d, d)))
    else:
        q = np.eye(d)
    h = q @ np.diag(eig) @ q.T
    center = rng.uniform(-2.0, 2.0, d)
    return h, center


def failure_metric(steps: np.ndarray, deltas: np.ndarray, d: int, weighted: bool) -> np.ndarray:
    rejected = deltas > 0
    v = steps[rejected]
    if len(v) < 2:
        return np.eye(d)
    v = v / np.maximum(np.linalg.norm(v, axis=1, keepdims=True), 1e-15)
    if weighted:
        # Rank weights are invariant to affine rescaling/shifting of objective values.
        positive = deltas[rejected]
        order = np.argsort(np.argsort(positive))
        w = (order + 1) / len(order)
    else:
        w = np.ones(len(v))
    # Isotropic directions have E[d vv^T] = I. A d-unit identity prior
    # prevents tiny samples from creating spurious extreme anisotropy.
    scatter = np.einsum("i,ij,ik->jk", w, v, v)
    return (d * np.eye(d) + d * scatter) / (d + w.sum())


def selection_contrast(steps: np.ndarray, deltas: np.ndarray, d: int) -> tuple[np.ndarray, np.ndarray]:
    """Return proposal covariance and rejection contrast after proposal whitening."""
    u = steps / np.maximum(np.linalg.norm(steps, axis=1, keepdims=True), 1e-15)
    proposal = d * (u.T @ u) / len(u)
    evals, evecs = np.linalg.eigh(proposal + 1e-8 * np.eye(d))
    whitener = evecs @ np.diag(evals ** -0.5) @ evecs.T
    y = u @ whitener.T
    rejected = deltas > 0
    rejected_cov = d * (y[rejected].T @ y[rejected]) / max(1, rejected.sum())
    contrast = whitener.T @ (rejected_cov - np.eye(d)) @ whitener
    return proposal, contrast


def metric_quality(metric: np.ndarray, h: np.ndarray, rng: np.random.Generator, n: int = 2000) -> tuple[float, float]:
    z = rng.normal(size=(n, h.shape[0]))
    z /= np.linalg.norm(z, axis=1, keepdims=True)
    true = np.einsum("ij,jk,ik->i", z, h, z)
    pred = np.einsum("ij,jk,ik->i", z, metric, z)
    rho = float(spearmanr(true, pred).statistic)
    _, vh = np.linalg.eigh(h)
    _, vm = np.linalg.eigh(metric)
    top_cos2 = float((vh[:, -1] @ vm[:, -1]) ** 2)
    return rho, top_cos2


def run_case(d: int, condition: float, rotated: bool, seed: int, budget_d: int) -> dict:
    rng = np.random.default_rng(seed)
    h, center = quadratic(d, condition, rotated, 10_000 + seed)
    lb = np.full(d, -5.0)
    ub = np.full(d, 5.0)
    span = ub - lb
    pop_n = 5 * d
    sampler = qmc.Halton(d, scramble=True, seed=seed)
    pop = qmc.scale(sampler.random(pop_n), lb, ub)

    def f(x):
        e = x - center
        return float(e @ h @ e)

    vals = np.array([f(x) for x in pop])
    nfev = pop_n
    steps: list[np.ndarray] = []
    deltas: list[float] = []
    parent_quantiles: list[float] = []
    budget = budget_d * d

    while nfev < budget:
        best = pop[np.argmin(vals)]
        fscale = rng.uniform(0.5, 1.0)
        trials = []
        parents = []
        ranks = np.argsort(np.argsort(vals)) / max(1, pop_n - 1)
        for i in range(pop_n):
            eligible = np.delete(np.arange(pop_n), i)
            a, b = rng.choice(eligible, 2, replace=False)
            donor = best + fscale * (pop[a] - pop[b])
            mask = rng.random(d) < 0.7
            mask[rng.integers(d)] = True
            trial = np.where(mask, donor, pop[i])
            bad = (trial < lb) | (trial > ub)
            trial[bad] = rng.uniform(lb[bad], ub[bad])
            trials.append(trial)
            parents.append(i)
        remaining = budget - nfev
        for trial, i in zip(trials[:remaining], parents[:remaining], strict=True):
            y = f(trial)
            step = (trial - pop[i]) / span
            steps.append(step)
            deltas.append(y - vals[i])
            parent_quantiles.append(float(ranks[i]))
            nfev += 1
            if y <= vals[i]:
                pop[i] = trial
                vals[i] = y

    s = np.asarray(steps)
    delta = np.asarray(deltas)
    pq = np.asarray(parent_quantiles)
    nonzero = np.linalg.norm(s, axis=1) > 1e-14
    s, delta, pq = s[nonzero], delta[nonzero], pq[nonzero]
    rayleigh = np.einsum("ij,jk,ik->i", s, h, s) / np.einsum("ij,ij->i", s, s)
    rejected = delta > 0
    accepted = ~rejected
    curvature_ratio = float(np.median(rayleigh[rejected]) / np.median(rayleigh[accepted])) if accepted.any() else np.nan

    proposal, contrast = selection_contrast(s, delta, d)
    all_u = failure_metric(s, delta, d, weighted=False)
    all_w = failure_metric(s, delta, d, weighted=True)
    # Nearer-to-best parents reduce first-order-gradient contamination of one-sided failures.
    near = pq <= 0.5
    near_w = failure_metric(s[near], delta[near], d, weighted=True)
    eval_rng = np.random.default_rng(50_000 + seed)
    rho_prop, _ = metric_quality(proposal, h, eval_rng)
    rho_invprop, _ = metric_quality(np.linalg.inv(proposal + 1e-8 * np.eye(d)), h, eval_rng)
    rho_contrast, _ = metric_quality(contrast, h, eval_rng)
    rho_u, cos_u = metric_quality(all_u, h, eval_rng)
    rho_w, cos_w = metric_quality(all_w, h, eval_rng)
    rho_n, cos_n = metric_quality(near_w, h, eval_rng)
    return {
        "dimension": d,
        "condition": condition,
        "rotated": int(rotated),
        "seed": seed,
        "budget_d": budget_d,
        "trials": len(s),
        "reject_rate": float(rejected.mean()),
        "reject_accept_curvature_ratio": curvature_ratio,
        "rho_proposal": rho_prop,
        "rho_inverse_proposal": rho_invprop,
        "rho_rejection_contrast": rho_contrast,
        "rho_reject_unweighted": rho_u,
        "rho_reject_rankweighted": rho_w,
        "rho_nearbest_rankweighted": rho_n,
        "top_cos2_unweighted": cos_u,
        "top_cos2_rankweighted": cos_w,
        "top_cos2_nearbest": cos_n,
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path, default=Path("results/geometry-probe.csv"))
    p.add_argument("--budget-d", type=int, default=100)
    p.add_argument("--seeds", type=int, default=20)
    args = p.parse_args()
    rows = []
    for d in (5, 10):
        for condition in (1.0, 100.0, 10_000.0):
            for rotated in (False, True):
                for seed in range(1, args.seeds + 1):
                    rows.append(run_case(d, condition, rotated, seed, args.budget_d))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0])
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {len(rows)} rows to {args.output}")


if __name__ == "__main__":
    main()

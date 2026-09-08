#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2.0", "pandas>=2.2", "scipy>=1.13", "statsmodels>=0.14"]
# ///
"""Run frozen H002 only after the survival outcome file is unsealed."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import norm

ROOT = Path(__file__).resolve().parents[1]
PREDICTORS = ROOT / "candidates/replication-alberta-2018/p3hz4_predictors.csv"
OUTCOMES = ROOT / "candidates/replication-alberta-2018/p3hz4_survival.csv"
DRAWS = ROOT / "analysis/h002_predictability_draws.npz"
OUTPUT = ROOT / "analysis/h002_survival_results.json"
SEED = 20260908
N_IMPUTATIONS = 1000


def zscore(x: np.ndarray) -> np.ndarray:
    return (x - x.mean()) / x.std(ddof=1)


def combine(beta: list[float], variance: list[float]) -> dict[str, float]:
    b = np.asarray(beta)
    u = np.asarray(variance)
    qbar = float(b.mean())
    total_var = float(u.mean() + (1 + 1 / len(b)) * b.var(ddof=1))
    se = total_var**0.5
    lo, hi = qbar - 1.96 * se, qbar + 1.96 * se
    p = float(2 * norm.sf(abs(qbar / se)))
    return {
        "beta": qbar,
        "se": se,
        "ci95_beta": [lo, hi],
        "odds_ratio": float(np.exp(qbar)),
        "ci95_odds_ratio": [float(np.exp(lo)), float(np.exp(hi))],
        "p_two_sided": p,
        "between_imputation_sd_beta": float(b.std(ddof=1)),
    }


def run_threshold(
    threshold: int,
    ids: np.ndarray,
    log_sigma: np.ndarray,
    bird_mean: np.ndarray,
    bird_info: pd.DataFrame,
    outcomes: pd.DataFrame,
    draw_idx: np.ndarray,
    adjust_mean: bool = True,
) -> dict:
    eligible_ids = set(bird_info.loc[bird_info.n_obs >= threshold, "ID"])
    positions = [i for i, bird in enumerate(ids) if bird in eligible_ids]
    chosen_ids = ids[positions]
    frame = pd.DataFrame({"ID": chosen_ids}).merge(bird_info[["ID", "Sex"]], on="ID").merge(outcomes, on="ID")
    if len(frame) != len(chosen_ids):
        raise ValueError("Outcome join is incomplete for eligible H002 birds")
    pos_lookup = {bird: p for bird, p in zip(chosen_ids, positions, strict=True)}
    order = np.array([pos_lookup[bird] for bird in frame.ID])

    betas: list[float] = []
    variances: list[float] = []
    mean_betas: list[float] = []
    failures = 0
    for j in draw_idx:
        unpredictability = zscore(log_sigma[order, j])
        mean_latency = zscore(bird_mean[order, j])
        x = pd.DataFrame({"unpredictability": unpredictability, "Sex": frame.Sex.to_numpy(float)})
        if adjust_mean:
            x["mean_latency"] = mean_latency
        x = sm.add_constant(x, has_constant="add")
        try:
            result = sm.GLM(frame.survival2.to_numpy(int), x, family=sm.families.Binomial()).fit()
            betas.append(float(result.params["unpredictability"]))
            variances.append(float(result.cov_params().loc["unpredictability", "unpredictability"]))
            if adjust_mean:
                mean_betas.append(float(result.params["mean_latency"]))
        except Exception:
            failures += 1

    out = {
        "threshold_n_obs": threshold,
        "adjust_mean_latency": adjust_mean,
        "n_birds": int(len(frame)),
        "survivors": int(frame.survival2.sum()),
        "non_survivors": int((1 - frame.survival2).sum()),
        "successful_imputations": len(betas),
        "failed_imputations": failures,
        "unpredictability": combine(betas, variances),
    }
    if mean_betas:
        out["mean_latency_beta_across_imputations"] = {
            "mean": float(np.mean(mean_betas)),
            "sd": float(np.std(mean_betas, ddof=1)),
        }
    return out


def main() -> None:
    outcomes = pd.read_csv(OUTCOMES, dtype={"ID": str})
    if list(outcomes.columns) != ["ID", "survival2"]:
        raise ValueError("Outcome file must contain exactly ID,survival2")
    if not set(outcomes.survival2.unique()).issubset({0, 1}):
        raise ValueError("survival2 must be binary")

    predictors = pd.read_csv(PREDICTORS, dtype={"ID": str})
    bird_info = predictors.groupby("ID").agg(n_obs=("ID", "size"), Sex=("Sex", "first")).reset_index()
    if predictors.groupby("ID").Sex.nunique().max() != 1:
        raise ValueError("Sex varies within bird")

    pack = np.load(DRAWS)
    ids = pack["IDs"].astype(str)
    log_sigma = pack["log_sigma"]
    bird_mean = pack["bird_mean"]
    if log_sigma.shape != bird_mean.shape or log_sigma.shape[0] != len(ids):
        raise ValueError("Posterior draw shapes are inconsistent")

    rng = np.random.default_rng(SEED)
    draw_idx = np.sort(rng.choice(log_sigma.shape[1], N_IMPUTATIONS, replace=False))
    result = {
        "n_posterior_draws_available": int(log_sigma.shape[1]),
        "n_imputations": N_IMPUTATIONS,
        "primary_n_ge4": run_threshold(4, ids, log_sigma, bird_mean, bird_info, outcomes, draw_idx),
        "sensitivity_n_ge6": run_threshold(6, ids, log_sigma, bird_mean, bird_info, outcomes, draw_idx),
        "sensitivity_n_ge8": run_threshold(8, ids, log_sigma, bird_mean, bird_info, outcomes, draw_idx),
        "sensitivity_unadjusted_n_ge4": run_threshold(4, ids, log_sigma, bird_mean, bird_info, outcomes, draw_idx, adjust_mean=False),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

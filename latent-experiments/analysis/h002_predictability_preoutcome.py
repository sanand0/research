#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "arviz>=0.23",
#   "numpy>=2.0",
#   "pandas>=2.2",
#   "pymc>=6.3",
#   "scipy>=1.13",
# ]
# ///
"""Outcome-blind hierarchical location-scale screening for H002.

The input MUST NOT contain the survival column. Bird-specific residual log-SD is
partially pooled and treated as the candidate behavioral unpredictability trait.
"""

from __future__ import annotations

import json
from pathlib import Path

import arviz as az
import numpy as np
import pandas as pd
import pymc as pm
from scipy.stats import pearsonr, spearmanr

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "candidates/replication-alberta-2018/p3hz4_predictors.csv"
OUTPUT = ROOT / "analysis/h002_predictability_preoutcome.json"
SCORES = ROOT / "analysis/h002_predictability_scores.csv"
SEED = 20260908


def prepare() -> pd.DataFrame:
    d = pd.read_csv(INPUT)
    forbidden = {"survival", "Survival", "Survived"}.intersection(d.columns)
    if forbidden:
        raise ValueError(f"Outcome column present in predictor-only input: {sorted(forbidden)}")
    d = d.copy()
    d["ID"] = d["ID"].astype(str)
    d["logSec"] = np.log(d["Sec"].astype(float))
    d["cTemp"] = (d["TempDay"] - d["TempDay"].mean()) / d["TempDay"].std(ddof=1)
    return d


def design_matrix(d: pd.DataFrame, expanded: bool) -> tuple[np.ndarray, list[str]]:
    cols: dict[str, np.ndarray] = {
        "sex": d["Sex"].to_numpy(float),
        "temp": d["cTemp"].to_numpy(float),
    }
    for treatment in (2, 3, 4):
        indicator = (d["Treatment"].to_numpy() == treatment).astype(float)
        cols[f"treatment_{treatment}"] = indicator
        cols[f"treatment_{treatment}_x_temp"] = indicator * d["cTemp"].to_numpy(float)
    if expanded:
        for feeder in sorted(d["Feeder"].unique())[1:]:
            cols[f"feeder_{feeder}"] = (d["Feeder"].to_numpy() == feeder).astype(float)
        for rep in sorted(d["Rep"].unique())[1:]:
            cols[f"rep_{rep}"] = (d["Rep"].to_numpy() == rep).astype(float)
    return np.column_stack(list(cols.values())), list(cols)


def fit_model(d: pd.DataFrame, expanded: bool, draws: int, tune: int, seed: int, robust: bool = False):
    bird_levels = np.array(sorted(d["ID"].unique()))
    bird_lookup = {bird: i for i, bird in enumerate(bird_levels)}
    bird_idx = d["ID"].map(bird_lookup).to_numpy(int)
    x, names = design_matrix(d, expanded)
    y = d["logSec"].to_numpy(float)

    with pm.Model() as model:
        alpha = pm.Normal("alpha", mu=float(y.mean()), sigma=2.0)
        beta = pm.Normal("beta", mu=0.0, sigma=1.0, shape=x.shape[1])
        sigma_bird_mean = pm.HalfNormal("sigma_bird_mean", sigma=1.0)
        bird_mean_raw = pm.Normal("bird_mean_raw", mu=0.0, sigma=1.0, shape=len(bird_levels))
        bird_mean = pm.Deterministic("bird_mean", bird_mean_raw * sigma_bird_mean)

        log_sigma_pop = pm.Normal("log_sigma_pop", mu=float(np.log(y.std(ddof=1))), sigma=1.0)
        sigma_log_sigma = pm.HalfNormal("sigma_log_sigma", sigma=0.5)
        bird_log_sigma_raw = pm.Normal("bird_log_sigma_raw", mu=0.0, sigma=1.0, shape=len(bird_levels))
        bird_log_sigma = pm.Deterministic(
            "bird_log_sigma", log_sigma_pop + bird_log_sigma_raw * sigma_log_sigma
        )

        mu = alpha + pm.math.dot(x, beta) + bird_mean[bird_idx]
        if robust:
            pm.StudentT("obs", nu=5.0, mu=mu, sigma=pm.math.exp(bird_log_sigma[bird_idx]), observed=y)
        else:
            pm.Normal("obs", mu=mu, sigma=pm.math.exp(bird_log_sigma[bird_idx]), observed=y)

        idata = pm.sample(
            draws=draws,
            tune=tune,
            chains=4,
            cores=4,
            random_seed=[seed, seed + 1, seed + 2, seed + 3],
            target_accept=0.92,
            progressbar=False,
            return_inferencedata=True,
        )

    summary = az.summary(
        idata,
        var_names=["alpha", "beta", "sigma_bird_mean", "log_sigma_pop", "sigma_log_sigma", "bird_mean_raw", "bird_log_sigma_raw"],
        round_to=None,
    )
    max_rhat = float(summary["r_hat"].max())
    min_ess = float(summary["ess_bulk"].min())
    worst_rhat_parameter = str(summary["r_hat"].idxmax())
    worst_ess_parameter = str(summary["ess_bulk"].idxmin())
    divergences = int(idata.sample_stats["diverging"].sum().item())

    log_sigma_draws = idata.posterior["bird_log_sigma"].stack(sample=("chain", "draw")).values
    bird_mean_draws = idata.posterior["bird_mean"].stack(sample=("chain", "draw")).values
    score = pd.DataFrame(
        {
            "ID": bird_levels,
            "log_sigma_mean": log_sigma_draws.mean(axis=1),
            "log_sigma_sd": log_sigma_draws.std(axis=1, ddof=1),
            "log_sigma_q025": np.quantile(log_sigma_draws, 0.025, axis=1),
            "log_sigma_q975": np.quantile(log_sigma_draws, 0.975, axis=1),
            "mean_latency_effect": bird_mean_draws.mean(axis=1),
        }
    )
    score["unpredictability_z"] = (
        score["log_sigma_mean"] - score["log_sigma_mean"].mean()
    ) / score["log_sigma_mean"].std(ddof=1)
    counts = d.groupby("ID").size()
    score["n_obs"] = score["ID"].map(counts).astype(int)

    beta_mean = idata.posterior["beta"].mean(("chain", "draw")).values
    fixed = {name: float(value) for name, value in zip(names, beta_mean, strict=True)}
    tau = idata.posterior["sigma_log_sigma"].values.ravel()
    fit_summary = {
        "n_rows": int(len(d)),
        "n_birds": int(len(bird_levels)),
        "expanded_mean_model": expanded,
        "robust_student_t": robust,
        "max_rhat": max_rhat,
        "worst_rhat_parameter": worst_rhat_parameter,
        "min_ess_bulk": min_ess,
        "worst_ess_parameter": worst_ess_parameter,
        "divergences": divergences,
        "sigma_log_sigma_median": float(np.median(tau)),
        "sigma_log_sigma_q025": float(np.quantile(tau, 0.025)),
        "sigma_log_sigma_q975": float(np.quantile(tau, 0.975)),
        "fixed_effect_posterior_means": fixed,
    }
    return fit_summary, score, {"IDs": bird_levels, "log_sigma": log_sigma_draws, "bird_mean": bird_mean_draws}


def correlation(a: pd.DataFrame, b: pd.DataFrame) -> dict[str, float | int | list[float]]:
    x = a[["ID", "log_sigma_mean"]].merge(
        b[["ID", "log_sigma_mean"]], on="ID", suffixes=("_a", "_b")
    )
    a_values = x["log_sigma_mean_a"].to_numpy()
    b_values = x["log_sigma_mean_b"].to_numpy()
    rng = np.random.default_rng(SEED + len(x))
    boot = []
    for _ in range(4000):
        idx = rng.integers(0, len(x), len(x))
        rho = spearmanr(a_values[idx], b_values[idx]).statistic
        if np.isfinite(rho):
            boot.append(float(rho))
    return {
        "n": int(len(x)),
        "pearson_r": float(pearsonr(a_values, b_values).statistic),
        "spearman_rho": float(spearmanr(a_values, b_values).statistic),
        "spearman_bootstrap_95ci": [float(np.quantile(boot, 0.025)), float(np.quantile(boot, 0.975))],
    }


def main() -> None:
    d = prepare()
    primary_fit, primary, primary_draws = fit_model(d, expanded=False, draws=1000, tune=1000, seed=SEED)
    expanded_fit, expanded, _ = fit_model(d, expanded=True, draws=850, tune=850, seed=SEED + 10)
    robust_fit, robust, _ = fit_model(d, expanded=False, draws=850, tune=850, seed=SEED + 20, robust=True)

    split_scores: dict[str, pd.DataFrame] = {}
    split_fits: dict[str, dict] = {}
    for i, (label, reps) in enumerate(
        {"rep12": [1, 2], "rep34": [3, 4], "odd": [1, 3], "even": [2, 4]}.items()
    ):
        fit, score, _ = fit_model(
            d[d["Rep"].isin(reps)].copy(),
            expanded=False,
            draws=800,
            tune=800,
            seed=SEED + 100 + i * 10,
        )
        split_scores[label] = score
        split_fits[label] = fit

    count_rho = spearmanr(primary["log_sigma_mean"], primary["n_obs"]).statistic
    out = {
        "input": str(INPUT.relative_to(ROOT)),
        "outcome_columns_checked_absent": True,
        "primary_fit": primary_fit,
        "expanded_fit": expanded_fit,
        "robust_fit": robust_fit,
        "split_fits": split_fits,
        "reliability": {
            "rep12_vs_rep34": correlation(split_scores["rep12"], split_scores["rep34"]),
            "odd_vs_even": correlation(split_scores["odd"], split_scores["even"]),
        },
        "stability": {
            "primary_vs_expanded": correlation(primary, expanded),
            "primary_vs_robust_student_t": correlation(primary, robust),
            "spearman_log_sigma_vs_n_obs": float(count_rho),
            "spearman_log_sigma_vs_mean_latency": float(spearmanr(primary["log_sigma_mean"], primary["mean_latency_effect"]).statistic),
        },
        "acceptance_rules_set_before_hls_result": {
            "sampler": "max R-hat <= 1.01, no divergences, and minimum bulk ESS >= 200 for summarized global parameters",
            "split_reliability": "Spearman rho must be > 0 in both independent replicate partitions",
            "mean_model_stability": "primary vs expanded Spearman rho >= 0.80",
            "outlier_robustness": "primary Normal vs Student-t(nu=5) Spearman rho >= 0.80",
            "observation_count_dependence": "absolute Spearman rho < 0.30 preferred; otherwise flag as material limitation",
            "source_signal": "visual-containing treatment coefficients remain strongly positive on log latency scale",
        },
    }
    primary.to_csv(SCORES, index=False)
    np.savez_compressed(
        ROOT / "analysis/h002_predictability_draws.npz",
        IDs=primary_draws["IDs"],
        log_sigma=primary_draws["log_sigma"],
        bird_mean=primary_draws["bird_mean"],
    )
    OUTPUT.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()

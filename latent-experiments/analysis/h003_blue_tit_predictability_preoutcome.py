#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["arviz>=0.20", "numpy>=2", "pandas>=2", "pymc>=5.20", "scipy>=1.14"]
# ///
"""Outcome-blind H003 candidate: female-specific laying-date residual variability."""

from __future__ import annotations

import json
from pathlib import Path

import arviz as az
import numpy as np
import pandas as pd
import pymc as pm
from scipy.stats import spearmanr

DATA = Path("candidates/blue-tit-silwood/btoak_predictors.csv")
OUT = Path("candidates/blue-tit-silwood/h003_preoutcome.json")
SCORES = Path("candidates/blue-tit-silwood/h003_predictability_scores.csv")
SEED = 20260908


def prep(min_obs: int = 3) -> pd.DataFrame:
    d = pd.read_csv(DATA)
    last = d.groupby("female")["year"].max()
    d = d[d["female"].isin(last[last < 2019].index)].copy()
    d["age"] = d["f.age"].fillna("NA").astype(str)
    counts = d.groupby("female").size()
    d = d[d["female"].isin(counts[counts >= min_obs].index)].copy()
    d = d.sort_values(["female", "year"]).reset_index(drop=True)
    d["attempt"] = d.groupby("female").cumcount()
    return d


def fit(df: pd.DataFrame, label: str, draws: int = 700, tune: int = 700) -> tuple[pd.Series, dict]:
    birds = pd.Index(sorted(df["female"].unique()))
    years = pd.Index(sorted(df["year"].unique()))
    bird_idx = birds.get_indexer(df["female"])
    year_idx = years.get_indexer(df["year"])
    age_old = (df["age"] == ">1").astype(float).to_numpy()
    age_na = (df["age"] == "NA").astype(float).to_numpy()
    y = df["LD"].to_numpy(dtype=float)
    y_center = float(y.mean())
    y = y - y_center

    coords = {"bird": birds.astype(str), "year": years.astype(str), "obs": np.arange(len(df))}
    with pm.Model(coords=coords) as model:
        bidx = pm.Data("bird_idx", bird_idx, dims="obs")
        yidx = pm.Data("year_idx", year_idx, dims="obs")
        old = pm.Data("age_old", age_old, dims="obs")
        ana = pm.Data("age_na", age_na, dims="obs")

        intercept = pm.Normal("intercept", 0, 10)
        age_old_b = pm.Normal("age_old_b", 0, 5)
        age_na_b = pm.Normal("age_na_b", 0, 5)
        year_sd = pm.HalfNormal("year_sd", 5)
        year_z = pm.Normal("year_z", 0, 1, dims="year")
        year_eff = pm.Deterministic("year_eff", (year_z - pm.math.mean(year_z)) * year_sd, dims="year")

        female_mean_sd = pm.HalfNormal("female_mean_sd", 5)
        female_mean_z = pm.Normal("female_mean_z", 0, 1, dims="bird")
        female_mean = pm.Deterministic("female_mean", female_mean_z * female_mean_sd, dims="bird")

        log_sigma_pop = pm.Normal("log_sigma_pop", np.log(4), 1)
        sigma_log_sigma = pm.HalfNormal("sigma_log_sigma", 0.5)
        female_sigma_z = pm.Normal("female_sigma_z", 0, 1, dims="bird")
        female_log_sigma = pm.Deterministic(
            "female_log_sigma", log_sigma_pop + female_sigma_z * sigma_log_sigma, dims="bird"
        )
        female_sigma = pm.Deterministic("female_sigma", pm.math.exp(female_log_sigma), dims="bird")

        mu = intercept + age_old_b * old + age_na_b * ana + year_eff[yidx] + female_mean[bidx]
        pm.Normal("LD", mu=mu, sigma=female_sigma[bidx], observed=y, dims="obs")

        idata = pm.sample(
            draws=draws,
            tune=tune,
            chains=4,
            cores=4,
            random_seed=SEED,
            target_accept=0.92,
            progressbar=False,
            return_inferencedata=True,
        )

    score = idata.posterior["female_log_sigma"].mean(("chain", "draw")).to_series()
    score.index = birds
    summ = az.summary(
        idata,
        var_names=["sigma_log_sigma", "female_mean_sd", "year_sd", "age_old_b", "age_na_b", "female_log_sigma"],
        kind="diagnostics",
    )
    diagnostics = {
        "label": label,
        "rows": int(len(df)),
        "birds": int(len(birds)),
        "max_rhat": float(summ["r_hat"].max()),
        "min_ess_bulk": float(summ["ess_bulk"].min()),
        "divergences": int(idata.sample_stats["diverging"].sum()),
        "sigma_log_sigma_median": float(idata.posterior["sigma_log_sigma"].median()),
        "sigma_log_sigma_q03": float(np.quantile(idata.posterior["sigma_log_sigma"].values, .03)),
        "sigma_log_sigma_q97": float(np.quantile(idata.posterior["sigma_log_sigma"].values, .97)),
        "y_center": y_center,
    }
    return score, diagnostics


def main() -> None:
    full = prep(3)
    score_full, diag_full = fit(full, "full")

    four = prep(4)
    odd = four[four["attempt"] % 2 == 0].copy()
    even = four[four["attempt"] % 2 == 1].copy()
    score_odd, diag_odd = fit(odd, "odd", draws=600, tune=600)
    score_even, diag_even = fit(even, "even", draws=600, tune=600)
    common = score_odd.index.intersection(score_even.index)
    split_rho = float(spearmanr(score_odd.loc[common], score_even.loc[common]).statistic)

    counts = full.groupby("female").size()
    n_rho = float(spearmanr(score_full.loc[counts.index], counts).statistic)
    means = full.groupby("female")["LD"].mean()
    mean_rho = float(spearmanr(score_full.loc[means.index], means).statistic)

    result = {
        "full": diag_full,
        "odd": diag_odd,
        "even": diag_even,
        "odd_even_spearman": split_rho,
        "score_n_spearman": n_rho,
        "score_mean_LD_spearman": mean_rho,
        "gate_split_target": 0.20,
        "gate_split_pass": split_rho > 0.20,
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    pd.DataFrame({"female": score_full.index, "log_sigma_score": score_full.values}).to_csv(SCORES, index=False)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

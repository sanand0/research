#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2.0", "pandas>=2.2", "statsmodels>=0.14", "scipy>=1.13"]
# ///
"""Run the frozen chronotype -> apparent-survival analysis after outcome unsealing."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy.stats import norm

ROOT = Path(__file__).resolve().parents[1]
A = ROOT / "analysis"
SURVIVAL = ROOT / "candidates/chickadees/THC_Survival.csv"
RNG = np.random.default_rng(20260908)


def z(x: pd.Series) -> pd.Series:
    return (x - x.mean()) / x.std(ddof=1)


def fit_formula(df: pd.DataFrame, formula: str):
    model = smf.glm(formula, data=df, family=sm.families.Binomial()).fit()
    return model


def term_summary(model, term: str) -> dict:
    beta = float(model.params[term])
    se = float(model.bse[term])
    lo, hi = map(float, model.conf_int().loc[term])
    return {
        "beta": beta,
        "se": se,
        "z": float(beta / se),
        "p": float(model.pvalues[term]),
        "beta_ci95": [lo, hi],
        "odds_ratio": float(np.exp(beta)),
        "odds_ratio_ci95": [float(np.exp(lo)), float(np.exp(hi))],
        "supports_nonzero_95": bool(lo > 0 or hi < 0),
    }


def model_summary(name: str, df: pd.DataFrame, formula: str, term: str = "early_z") -> tuple[dict, object]:
    m = fit_formula(df, formula)
    out = {
        "name": name,
        "formula": formula,
        "n": int(m.nobs),
        "events_1": int(df.Survived.sum()),
        "events_0": int((1 - df.Survived).sum()),
        "converged": bool(m.converged),
        "aic": float(m.aic),
        "deviance": float(m.deviance),
        "term": term_summary(m, term),
        "all_coefficients": {k: float(v) for k, v in m.params.items()},
    }
    return out, m


def standardize_full(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    d["early_z"] = z(d["early_chronotype"])
    d["total_z"] = z(d["total_blup"])
    return d


def uncertainty_draws(d: pd.DataFrame, n_draws: int = 2000) -> dict:
    betas = []
    ses = []
    failed = 0
    first_mu = d["first_blup"].to_numpy()
    first_sd = d["first_blup_sd"].to_numpy()
    total_mu = d["total_blup"].to_numpy()
    total_sd = d["total_blup_sd"].to_numpy()
    for _ in range(n_draws):
        x = d.copy()
        x["early_z"] = z(pd.Series(-RNG.normal(first_mu, first_sd), index=x.index))
        x["total_z"] = z(pd.Series(RNG.normal(total_mu, total_sd), index=x.index))
        try:
            m = fit_formula(x, "Survived ~ early_z + total_z + C(AgeSex)")
            betas.append(float(m.params["early_z"]))
            ses.append(float(m.bse["early_z"]))
        except Exception:
            failed += 1
    betas = np.asarray(betas)
    ses = np.asarray(ses)
    beta = float(betas.mean())
    total_var = float(np.mean(ses**2) + np.var(betas, ddof=1))
    se = total_var**0.5
    lo, hi = beta - 1.96 * se, beta + 1.96 * se
    return {
        "draws_requested": n_draws,
        "draws_successful": int(len(betas)),
        "draws_failed": failed,
        "mean_beta": beta,
        "between_draw_sd_beta": float(betas.std(ddof=1)),
        "mean_within_model_se": float(ses.mean()),
        "combined_se": se,
        "beta_ci95": [lo, hi],
        "odds_ratio": float(np.exp(beta)),
        "odds_ratio_ci95": [float(np.exp(lo)), float(np.exp(hi))],
        "supports_nonzero_95": bool(lo > 0 or hi < 0),
        "beta_quantiles_from_phenotype_draws_only": [float(x) for x in np.quantile(betas, [0.025, 0.5, 0.975])],
    }


def main() -> None:
    survival = pd.read_csv(SURVIVAL)
    if set(survival.Survived.dropna().unique()) - {0, 1}:
        raise ValueError("Survived contains values outside {0,1}")

    full = pd.read_csv(A / "timing_phenotypes_full.csv").merge(survival, on="TransponderHexCode", how="inner")
    d = standardize_full(full)
    primary, primary_model = model_summary("primary", d, "Survived ~ early_z + total_z + C(AgeSex)")
    no_total, _ = model_summary("without_total_feeder_adjustment", d, "Survived ~ early_z + C(AgeSex)")

    # Illustrative probabilities, holding total use at its mean and using the modal/tied-first age-sex class.
    age_ref = d.AgeSex.value_counts().index[0]
    pred_df = pd.DataFrame({"early_z": [-1.0, 0.0, 1.0], "total_z": [0.0] * 3, "AgeSex": [age_ref] * 3})
    probs = primary_model.predict(pred_df)
    primary["illustrative_probabilities"] = {
        "AgeSex": age_ref,
        "total_z": 0.0,
        "by_early_z": {str(k): float(v) for k, v in zip([-1, 0, 1], probs)},
    }

    shared = pd.read_csv(A / "timing_phenotypes_shared_window.csv").merge(survival, on="TransponderHexCode", how="inner")
    shared["early_z"] = z(shared.early_chronotype)
    shared["total_z"] = z(shared.total_blup)
    shared_out, _ = model_summary("shared_window", shared, "Survived ~ early_z + total_z + C(AgeSex)")

    resid = pd.read_csv(A / "timing_phenotypes_residual_means.csv").merge(survival, on="TransponderHexCode", how="inner")
    resid["early_z"] = z(resid.early_resid_mean)
    resid["total_z"] = z(resid.total_resid_mean)
    resid_out, _ = model_summary("residual_mean_phenotype", resid, "Survived ~ early_z + total_z + C(AgeSex)")

    spatial = d.merge(pd.read_csv(A / "spatial_propensity.csv")[["TransponderHexCode", "offT_resid_mean"]], on="TransponderHexCode", how="inner")
    spatial["offT_z"] = z(spatial.offT_resid_mean)
    spatial_out, _ = model_summary("spatial_adjustment", spatial, "Survived ~ early_z + total_z + offT_z + C(AgeSex)")

    nonlinear = d.copy()
    nonlinear["early_z2"] = nonlinear.early_z**2
    nonlinear_out, nonlinear_model = model_summary("quadratic", nonlinear, "Survived ~ early_z + early_z2 + total_z + C(AgeSex)")
    nonlinear_out["quadratic_term"] = term_summary(nonlinear_model, "early_z2")

    unc = uncertainty_draws(d, 2000)

    sensitivity_terms = {
        "primary": primary["term"],
        "shared_window": shared_out["term"],
        "residual_mean": resid_out["term"],
        "spatial_adjustment": spatial_out["term"],
    }
    signs = {k: int(np.sign(v["beta"])) for k, v in sensitivity_terms.items()}
    interval_sides = {k: v["supports_nonzero_95"] for k, v in sensitivity_terms.items()}
    primary_sign = signs["primary"]
    first_three_same_sign = all(signs[k] == primary_sign for k in ["shared_window", "residual_mean", "spatial_adjustment"])
    first_three_same_support = all(interval_sides[k] == interval_sides["primary"] for k in ["shared_window", "residual_mean", "spatial_adjustment"])
    if not first_three_same_sign:
        stability = "FLIPS"
    elif first_three_same_support:
        stability = "STABLE"
    else:
        stability = "SENSITIVE"

    results = {
        "unsealed_outcome_summary": {
            "survival_rows": int(len(survival)),
            "survived_1": int(survival.Survived.sum()),
            "survived_0": int((1 - survival.Survived).sum()),
            "survival_rate": float(survival.Survived.mean()),
            "primary_join_n": int(len(d)),
        },
        "primary": primary,
        "without_total_feeder_adjustment": no_total,
        "phenotype_uncertainty_sensitivity": unc,
        "sensitivity": {
            "shared_window": shared_out,
            "residual_mean": resid_out,
            "spatial_adjustment": spatial_out,
            "quadratic": nonlinear_out,
        },
        "stability_classification": stability,
        "stability_details": {"signs": signs, "supports_nonzero_95": interval_sides},
        "interpretation_guardrail": "Association with next-fall detection/apparent survival only; not a causal or confirmed mortality effect.",
    }
    (A / "survival_results.json").write_text(json.dumps(results, indent=2))
    d.to_csv(A / "joined_primary_outcomes.csv", index=False)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()

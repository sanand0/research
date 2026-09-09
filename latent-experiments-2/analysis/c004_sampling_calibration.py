#!/usr/bin/env python3
"""Synthetic calibration for C004 sampling-representativeness logic.

No ABCFlux outcome values are used. We simulate two ecosystem strata with unequal
areas, deliberately oversample the high-flux stratum, and compare random sparse
measurement days with preferential sampling of high-flux days.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).parents[1]
DAYS = 30
MONTHS = 12
AREA = np.array([0.70, 0.30])
BASE = np.array([1.0, 3.0])  # arbitrary units; intentionally synthetic
N_SITES = np.array([35, 45])  # observational network oversamples high-flux class
N_DAYS = 3
N_REPS = 200


def one_rep(seed: int, preferential: bool) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    month = np.arange(MONTHS)
    seasonal = 0.55 + 0.45 * np.sin((month - 2) * 2 * np.pi / 12) ** 2
    true_class_month = BASE[:, None] * seasonal[None, :] * DAYS
    truth = float((AREA[:, None] * true_class_month).sum())

    chamber = []
    for c in range(2):
        for _site in range(int(N_SITES[c])):
            site_scale = rng.lognormal(mean=-0.5 * 0.25**2, sigma=0.25)
            for m in range(MONTHS):
                mean_daily = BASE[c] * seasonal[m] * site_scale
                # Positive skew / hot days; mean remains approximately mean_daily.
                daily = rng.gamma(shape=2.0, scale=mean_daily / 2.0, size=DAYS)
                if preferential:
                    # A field campaign more likely to sample high-flux/hot days.
                    p = daily + 0.05 * daily.mean()
                    p = p / p.sum()
                    idx = rng.choice(DAYS, N_DAYS, replace=False, p=p)
                else:
                    idx = rng.choice(DAYS, N_DAYS, replace=False)
                est_month = float(daily[idx].mean() * DAYS)
                chamber.append((c, m, est_month))

    arr = np.array(chamber, dtype=float)
    # Naive record-weighted annualized estimator: observational class imbalance persists.
    naive_month = np.array([arr[arr[:, 1] == m, 2].mean() for m in range(MONTHS)])
    naive = float(naive_month.sum())

    # Frozen candidate estimator: average sites within ecosystem x month, then target-area weight.
    cm = np.zeros((2, MONTHS))
    for c in range(2):
        for m in range(MONTHS):
            cm[c, m] = arr[(arr[:, 0] == c) & (arr[:, 1] == m), 2].mean()
    reweighted = float((AREA[:, None] * cm).sum())
    return {
        "truth": truth,
        "naive": naive,
        "reweighted": reweighted,
        "naive_rel_error": (naive - truth) / truth,
        "reweighted_rel_error": (reweighted - truth) / truth,
    }


def summarize(preferential: bool) -> dict:
    rows = [one_rep(20260909 + i, preferential) for i in range(N_REPS)]
    nerr = np.array([r["naive_rel_error"] for r in rows])
    rerr = np.array([r["reweighted_rel_error"] for r in rows])
    return {
        "preferential_high_flux_day_sampling": preferential,
        "n_reps": N_REPS,
        "naive_mean_relative_bias": float(nerr.mean()),
        "naive_rmse_relative": float(np.sqrt(np.mean(nerr**2))),
        "reweighted_mean_relative_bias": float(rerr.mean()),
        "reweighted_rmse_relative": float(np.sqrt(np.mean(rerr**2))),
        "reweighted_bias_q025_q975": [float(x) for x in np.quantile(rerr, [0.025, 0.975])],
    }


def run() -> dict:
    unbiased = summarize(False)
    hot = summarize(True)
    return {
        "claim_id": "C004",
        "status": "synthetic_feasibility_only",
        "real_flux_values_accessed": False,
        "synthetic_design": {
            "ecosystem_area_weights": AREA.tolist(),
            "synthetic_flux_bases": BASE.tolist(),
            "observed_site_counts": N_SITES.tolist(),
            "measurement_days_per_month": N_DAYS,
            "months": MONTHS,
        },
        "unbiased_sparse_sampling": unbiased,
        "preferential_hot_day_sampling": hot,
        "calibration_checks": {
            "area_month_reweighting_recovers_unbiased_sparse_sampling": abs(unbiased["reweighted_mean_relative_bias"]) < 0.03,
            "naive_estimator_is_materially_biased_by_class_oversampling": abs(unbiased["naive_mean_relative_bias"]) > 0.10,
            "area_month_reweighting_does_not_hide_within_stratum_preferential_sampling": hot["reweighted_mean_relative_bias"] > 0.10,
        },
        "interpretation": "Ecosystem×month reweighting can correct observed stratum imbalance, but cannot identify/correct preferential measurement days within a stratum. C004 therefore needs an empirical continuous-vs-sparse measurement comparison, not only coverage reweighting.",
    }


if __name__ == "__main__":
    out = run()
    path = ROOT / "results" / "c004_sampling_calibration.json"
    path.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))

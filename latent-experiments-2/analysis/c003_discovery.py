#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy>=2"]
# ///
"""Frozen C003 discovery analysis for BioTIME study 713 only."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np

from c003_margin_null import empirical_p, random_matrix
from c003_real_support_calibrate import load_plots, metrics_subset

ROOT = Path(__file__).parents[1]
N_NULL = 999
BASE_SEED = 20260909


def summarize_null(obs, refs):
    b = np.array([x["b"] for x in refs])
    cv = np.array([x["cvratio"] for x in refs])
    return {
        "b": {
            "observed": obs["b"],
            "null_median": float(np.median(b)),
            "null_q025": float(np.quantile(b, .025)),
            "null_q975": float(np.quantile(b, .975)),
            "lower_tail_p": empirical_p(obs["b"], b, "lower"),
        },
        "cvratio": {
            "observed": obs["cvratio"],
            "null_median": float(np.median(cv)),
            "null_q025": float(np.quantile(cv, .025)),
            "null_q975": float(np.quantile(cv, .975)),
            "upper_tail_p": empirical_p(obs["cvratio"], cv, "upper"),
        },
    }


def main():
    plots = load_plots()
    result = {
        "claim_id": "C003",
        "source": "BioTIME study 713",
        "null_replicates": N_NULL,
        "primary_rule": "b lower-tail p <= .025 AND CVratio upper-tail p <= .025",
        "study_gate": ">=2/3 plots pass under both exponential and lognormal null-weight families",
        "plots": {},
    }
    family_pass_counts = {"exponential": 0, "lognormal": 0}
    both_pass = 0
    for pidx, (plot, d) in enumerate(plots.items()):
        x, eligible = d["x"], d["eligible"]
        obs = metrics_subset(x, eligible)
        row, col, support = x.sum(axis=1), x.sum(axis=0), x > 0
        pd = {
            "n_years": x.shape[1],
            "all_species": x.shape[0],
            "eligible_species": int(eligible.sum()),
            "observed": obs,
            "families": {},
        }
        passes = []
        for fidx, family in enumerate(["exponential", "lognormal"]):
            rng = np.random.default_rng(BASE_SEED + 100000*pidx + 10000*fidx)
            refs = [metrics_subset(random_matrix(row, col, support, rng, family), eligible) for _ in range(N_NULL)]
            s = summarize_null(obs, refs)
            passed = bool(s["b"]["lower_tail_p"] <= .025 and s["cvratio"]["upper_tail_p"] <= .025)
            s["joint_pass"] = passed
            family_pass_counts[family] += int(passed)
            passes.append(passed)
            pd["families"][family] = s
        pd["both_families_pass"] = bool(all(passes))
        both_pass += int(pd["both_families_pass"])
        result["plots"][plot] = pd
    result["family_pass_counts"] = family_pass_counts
    result["both_families_pass_count"] = both_pass
    result["discovery_gate_pass"] = bool(both_pass >= 2 and all(v >= 2 for v in family_pass_counts.values()))
    out = ROOT / "results" / "c003_discovery_713.json"
    out.write_text(json.dumps(result, indent=2) + "\n")
    concise = {
        p: {
            "observed_b": d["observed"]["b"],
            "observed_cvratio": d["observed"]["cvratio"],
            "exp": {"pb": d["families"]["exponential"]["b"]["lower_tail_p"], "pcv": d["families"]["exponential"]["cvratio"]["upper_tail_p"], "pass": d["families"]["exponential"]["joint_pass"]},
            "logn": {"pb": d["families"]["lognormal"]["b"]["lower_tail_p"], "pcv": d["families"]["lognormal"]["cvratio"]["upper_tail_p"], "pass": d["families"]["lognormal"]["joint_pass"]},
        } for p,d in result["plots"].items()
    }
    concise["discovery_gate_pass"] = result["discovery_gate_pass"]
    print(json.dumps(concise, indent=2))

if __name__ == "__main__":
    main()

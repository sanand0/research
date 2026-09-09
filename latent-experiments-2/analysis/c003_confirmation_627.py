#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy>=2"]
# ///
"""Frozen C003 confirmation on BioTIME study 627."""
from __future__ import annotations
import csv
import json
import math
import re
from pathlib import Path
import numpy as np

from c003_margin_null import empirical_p, random_matrix
from c003_real_support_calibrate import metrics_subset

ROOT = Path(__file__).parents[1]
DATA = ROOT / "cache" / "c003-confirmation" / "raw_data_627.csv"
CLAIM = ROOT / "claims" / "C003.json"
N_NULL = 999
BASE_SEED = 20260909 + 627


def load_plots():
    claim = json.loads(CLAIM.read_text())
    if claim["confirmation"]["source"] != "BioTIME 2.0 study 627":
        raise RuntimeError("claim does not authorize study 627 confirmation")
    rows = list(csv.DictReader(DATA.open()))
    years = sorted({int(r["YEAR"]) for r in rows})
    plots = sorted({re.search(r"[0-9]+$", r["SAMPLE_DESC"]).group(0) for r in rows}, key=int)
    out = {}
    for plot in plots:
        rr = [r for r in rows if re.search(r"[0-9]+$", r["SAMPLE_DESC"]).group(0) == plot]
        seen_samples = {(int(r["YEAR"]), r["SAMPLE_DESC"]) for r in rr}
        if len({y for y,_ in seen_samples}) != len(years) or len(seen_samples) != len(years):
            raise RuntimeError(f"plot {plot}: not exactly one sample per census year")
        species = sorted({r["valid_name"] for r in rr})
        yi = {y:i for i,y in enumerate(years)}
        si = {s:i for i,s in enumerate(species)}
        x = np.zeros((len(species), len(years)), float)
        for r in rr:
            x[si[r["valid_name"]], yi[int(r["YEAR"])]] = float(r["BIOMAS"])
        present = (x > 0).sum(axis=1)
        eligible = (present >= math.ceil(.15 * len(years))) & (x.var(axis=1, ddof=1) > 0)
        out[plot] = {"x":x, "eligible":eligible, "all_species":len(species)}
    return years, out


def empirical_summary(obs, refs):
    b = np.array([r["b"] for r in refs])
    cv = np.array([r["cvratio"] for r in refs])
    pb = empirical_p(obs["b"], b, "lower")
    pc = empirical_p(obs["cvratio"], cv, "upper")
    return {
        "observed": obs,
        "b_null_median": float(np.median(b)),
        "b_null_q025": float(np.quantile(b,.025)),
        "cvratio_null_median": float(np.median(cv)),
        "cvratio_null_q975": float(np.quantile(cv,.975)),
        "b_lower_tail_p": pb,
        "cvratio_upper_tail_p": pc,
        "joint_pass": bool(pb <= .025 and pc <= .025),
    }, b, cv


def pseudo_extreme_flags(b, cv):
    """Apply the frozen .025/.025 joint rule to each null draw by within-null rank."""
    n = len(b)
    # With 999 draws, the lowest/highest 24 ranks satisfy the same <=.025 scale conservatively.
    k = int(np.floor(.025 * (n + 1))) - 1
    k = max(k, 1)
    b_order = np.argsort(np.argsort(b)) + 1
    cv_order_desc = np.argsort(np.argsort(-cv)) + 1
    return (b_order <= k) & (cv_order_desc <= k)


def main():
    years, plots = load_plots()
    if len(plots) < 5:
        raise RuntimeError("confirmation requires >=5 plots")
    result = {
        "claim_id":"C003",
        "source":"BioTIME study 627",
        "years":years,
        "n_plots":len(plots),
        "null_replicates":N_NULL,
        "plot_rule":"b lower-tail p<=.025 AND CVratio upper-tail p<=.025",
        "study_rule":"each family pass-count upper-tail p<=.025 AND >=20% plots pass under both families",
        "plots":{},
        "families":{},
    }
    family_flags = {"exponential":{}, "lognormal":{}}
    family_pseudo = {"exponential":{}, "lognormal":{}}
    for pidx,(plot,d) in enumerate(plots.items()):
        x, eligible = d["x"], d["eligible"]
        if int(eligible.sum()) < 4:
            result["plots"][plot] = {"eligible_species":int(eligible.sum()), "eligible":False}
            continue
        row,col,support = x.sum(axis=1), x.sum(axis=0), x>0
        obs = metrics_subset(x, eligible)
        pd = {"eligible":True,"all_species":d["all_species"],"eligible_species":int(eligible.sum()),"observed":obs,"families":{}}
        for fidx,family in enumerate(["exponential","lognormal"]):
            rng = np.random.default_rng(BASE_SEED + 100000*pidx + 10000*fidx)
            refs = [metrics_subset(random_matrix(row,col,support,rng,family), eligible) for _ in range(N_NULL)]
            s,b,cv = empirical_summary(obs, refs)
            pd["families"][family] = s
            family_flags[family][plot] = s["joint_pass"]
            family_pseudo[family][plot] = pseudo_extreme_flags(b,cv)
        pd["both_families_pass"] = bool(all(pd["families"][f]["joint_pass"] for f in ["exponential","lognormal"]))
        result["plots"][plot] = pd

    eligible_plots = [p for p,d in result["plots"].items() if d.get("eligible")]
    if len(eligible_plots) < 5:
        result["executable"] = False
        result["reason"] = "fewer than five plots have >=4 eligible species"
        result["confirmation_pass"] = False
    else:
        result["executable"] = True
        for family in ["exponential","lognormal"]:
            obs_count = sum(bool(family_flags[family][p]) for p in eligible_plots)
            pseudo_counts = np.array([sum(bool(family_pseudo[family][p][j]) for p in eligible_plots) for j in range(N_NULL)])
            study_p = float((1 + np.sum(pseudo_counts >= obs_count))/(N_NULL+1))
            result["families"][family] = {
                "observed_plot_pass_count":int(obs_count),
                "eligible_plots":len(eligible_plots),
                "study_pass_count_null_max":int(pseudo_counts.max()),
                "study_pass_count_null_q975":float(np.quantile(pseudo_counts,.975)),
                "study_upper_tail_p":study_p,
                "study_pass":bool(study_p <= .025),
            }
        both_count = sum(bool(result["plots"][p]["both_families_pass"]) for p in eligible_plots)
        both_fraction = both_count/len(eligible_plots)
        result["both_families_plot_pass_count"] = int(both_count)
        result["both_families_plot_pass_fraction"] = float(both_fraction)
        result["confirmation_pass"] = bool(both_fraction >= .20 and all(result["families"][f]["study_pass"] for f in ["exponential","lognormal"]))
    out = ROOT / "results" / "c003_confirmation_627.json"
    out.write_text(json.dumps(result,indent=2)+"\n")
    concise = {
        "executable":result.get("executable"),
        "eligible_plots":sum(1 for d in result["plots"].values() if d.get("eligible")),
        "both_pass_count":result.get("both_families_plot_pass_count"),
        "both_pass_fraction":result.get("both_families_plot_pass_fraction"),
        "families":result.get("families"),
        "confirmation_pass":result.get("confirmation_pass"),
        "plot_observed":{p:{"b":d.get("observed",{}).get("b"),"cvratio":d.get("observed",{}).get("cvratio"),"both":d.get("both_families_pass")} for p,d in result["plots"].items()},
    }
    print(json.dumps(concise,indent=2))

if __name__ == "__main__":
    main()

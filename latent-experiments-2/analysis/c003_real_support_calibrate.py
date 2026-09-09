#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy>=2"]
# ///
"""Calibrate C003 margin/support null on study 713 structure before observed Taylor slopes."""
from __future__ import annotations

import csv
import json
import math
import re
from pathlib import Path
import numpy as np

from c003_margin_null import balance_to_margins, empirical_p, random_matrix

ROOT = Path(__file__).parents[1]
DATA = ROOT / "cache" / "c003-discovery" / "raw_data_713.csv"


def load_plots():
    rows = list(csv.DictReader(DATA.open()))
    years = sorted({int(r["YEAR"]) for r in rows})
    out = {}
    for plot in sorted({re.search(r"Plot-\d+", r["SAMPLE_DESC"]).group(0) for r in rows}):
        rr = [r for r in rows if plot in r["SAMPLE_DESC"]]
        species = sorted({r["valid_name"] for r in rr})
        yi = {y: i for i, y in enumerate(years)}
        si = {s: i for i, s in enumerate(species)}
        x = np.zeros((len(species), len(years)), dtype=float)
        for r in rr:
            x[si[r["valid_name"]], yi[int(r["YEAR"])]] = float(r["BIOMAS"])
        present = (x > 0).sum(axis=1)
        eligible = (present >= math.ceil(0.15 * len(years))) & (x.var(axis=1, ddof=1) > 0)
        out[plot] = {"x": x, "species": species, "years": years, "eligible": eligible}
    return out


def metrics_subset(x, eligible):
    z = np.asarray(x, float)[eligible]
    means = z.mean(axis=1)
    var = z.var(axis=1, ddof=1)
    ok = (means > 0) & (var > 0)
    if ok.sum() < 4:
        raise ValueError("fewer than 4 eligible nonzero-variance species")
    means, var = means[ok], var[ok]
    b = float(np.polyfit(np.log(means), np.log(var), 1)[0])
    cv = np.sqrt(var) / means
    cvratio = float(cv.mean() / np.average(cv, weights=means))
    return {"b": b, "cvratio": cvratio, "n_species": int(ok.sum())}


def stabilized_like(x, rng):
    """Known positive: temporal positive-magnitude variability declines with species mean."""
    support = x > 0
    row = x.sum(axis=1)
    col = x.sum(axis=0)
    means = row / x.shape[1]
    rank = np.argsort(np.argsort(means)) / max(1, len(means) - 1)
    sigma = 1.4 - 1.15 * rank
    w = np.exp(rng.normal(0.0, sigma[:, None], size=x.shape))
    return balance_to_margins(w, row, col, support)[0]


def graph_df(support):
    """Dimension proxy E - V + components for the bipartite support graph."""
    nr, nc = support.shape
    parent = list(range(nr + nc))
    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    def union(a, b):
        a, b = find(a), find(b)
        if a != b:
            parent[b] = a
    for i, j in zip(*np.where(support)):
        union(int(i), nr + int(j))
    components = len({find(i) for i in range(nr + nc)})
    edges = int(support.sum())
    return {"support_edges": edges, "support_vertices": nr + nc, "support_components": components,
            "cycle_df_proxy": edges - (nr + nc) + components}


def calibrate_plot(x, eligible, family, seed, n_cases=20, n_null=199):
    row, col, support = x.sum(axis=1), x.sum(axis=0), x > 0
    rng = np.random.default_rng(seed)
    false_joint = 0
    positive_joint = 0
    for case in range(n_cases):
        obs0 = random_matrix(row, col, support, rng, family)
        m0 = metrics_subset(obs0, eligible)
        refs0 = [metrics_subset(random_matrix(row, col, support, np.random.default_rng(seed + 100000 + case*n_null + k), family), eligible) for k in range(n_null)]
        pb0 = empirical_p(m0["b"], [r["b"] for r in refs0], "lower")
        pc0 = empirical_p(m0["cvratio"], [r["cvratio"] for r in refs0], "upper")
        false_joint += int(pb0 <= .025 and pc0 <= .025)

        obs1 = stabilized_like(x, rng)
        m1 = metrics_subset(obs1, eligible)
        refs1 = [metrics_subset(random_matrix(row, col, support, np.random.default_rng(seed + 200000 + case*n_null + k), family), eligible) for k in range(n_null)]
        pb1 = empirical_p(m1["b"], [r["b"] for r in refs1], "lower")
        pc1 = empirical_p(m1["cvratio"], [r["cvratio"] for r in refs1], "upper")
        positive_joint += int(pb1 <= .025 and pc1 <= .025)
    return {
        "family": family,
        "n_cases": n_cases,
        "null_replicates_per_case": n_null,
        "joint_false_positives": false_joint,
        "joint_positive_detections": positive_joint,
        "joint_positive_power": positive_joint / n_cases,
        "pass": bool(false_joint <= 2 and positive_joint >= 16),
    }


def main():
    plots = load_plots()
    result = {"seed": 20260909, "rule": "Each plot/family passes if <=2/20 joint null false positives and >=16/20 injected-dominance detections.", "plots": {}}
    for pidx, (plot, d) in enumerate(plots.items()):
        x, eligible = d["x"], d["eligible"]
        info = {
            "n_years": x.shape[1],
            "all_species": x.shape[0],
            "eligible_species": int(eligible.sum()),
            **graph_df(x > 0),
            "families": {},
        }
        for fidx, family in enumerate(["exponential", "lognormal"]):
            info["families"][family] = calibrate_plot(x, eligible, family, 20260909 + 10000*pidx + 1000*fidx)
        result["plots"][plot] = info
    result["calibration_pass"] = all(v["pass"] for p in result["plots"].values() for v in p["families"].values())
    out = ROOT / "results" / "c003_real_support_calibration.json"
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({p: {"eligible": d["eligible_species"], "df": d["cycle_df_proxy"], "families": d["families"]} for p,d in result["plots"].items()} | {"calibration_pass": result["calibration_pass"]}, indent=2))


if __name__ == "__main__":
    main()

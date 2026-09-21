"""Audit whether early generation outcomes predict the remaining DE generation."""
from __future__ import annotations

import csv
import math
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

PATH = Path.home() / ".cache/algorithm-discovery/generation-trials.csv"


def auc(scores: np.ndarray, labels: np.ndarray) -> float:
    pos = scores[labels == 1]
    neg = scores[labels == 0]
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    # P(score_positive > score_negative) + half ties.
    return float((np.greater(pos[:, None], neg).sum() + 0.5 * np.equal(pos[:, None], neg).sum()) / (len(pos) * len(neg)))


def generations(rows: list[dict], frac: float = 0.25) -> list[dict]:
    grouped = defaultdict(list)
    keys = ("suite", "split", "fid", "instance", "dimension", "seed", "generation")
    for r in rows:
        grouped[tuple(r[k] for k in keys)].append(r)
    out = []
    for key, rs in grouped.items():
        rs.sort(key=lambda r: int(r["position"]))
        n = len(rs)
        # Exclude partial final generations: an abort decision there cannot save a full planned batch.
        if n != int(rs[0]["population"]):
            continue
        k = max(2, math.ceil(n * frac))
        early, late = rs[:k], rs[k:]
        if not late:
            continue
        out.append({
            "suite": key[0], "split": key[1], "fid": key[2], "instance": key[3],
            "dimension": int(key[4]), "seed": int(key[5]), "generation": int(key[6]),
            "F": float(rs[0]["F"]), "n": n, "k": k,
            "early_accept": sum(int(r["accepted"]) for r in early),
            "late_accept": sum(int(r["accepted"]) for r in late),
            "early_parent_gain": sum(float(r["parent_improvement_norm"]) for r in early),
            "late_parent_gain": sum(float(r["parent_improvement_norm"]) for r in late),
            "early_best_gain": sum(float(r["incumbent_improvement_norm"]) for r in early),
            "late_best_gain": sum(float(r["incumbent_improvement_norm"]) for r in late),
        })
    return out


def summarize(gs: list[dict], split: str, suite: str) -> dict:
    x = [g for g in gs if g["split"] == split and (suite == "all" or g["suite"] == suite)]
    early = np.array([g["early_accept"] for g in x], float)
    late = np.array([g["late_accept"] for g in x], float)
    early_gain = np.array([g["early_parent_gain"] for g in x], float)
    late_gain = np.array([g["late_parent_gain"] for g in x], float)
    labels = (late > 0).astype(int)
    abort = early == 0
    saved = np.array([(g["n"] - g["k"]) if a else 0 for g, a in zip(x, abort, strict=True)], float)
    planned = np.array([g["n"] for g in x], float)
    late_gain_total = late_gain.sum()
    late_accept_total = late.sum()
    return {
        "n_generations": len(x),
        "rho_accept": float(spearmanr(early, late).statistic),
        "rho_gain": float(spearmanr(early_gain, late_gain).statistic),
        "auc_early_accept_predicts_late_any": auc(early, labels),
        "abort_rate_zero_early": float(abort.mean()),
        "eval_fraction_saved_if_abort": float(saved.sum() / planned.sum()),
        "fraction_late_accepts_discarded": float(late[abort].sum() / late_accept_total) if late_accept_total else 0.0,
        "fraction_late_gain_discarded": float(late_gain[abort].sum() / late_gain_total) if late_gain_total else 0.0,
        "p_late_accept_given_zero_early": float((late[abort] > 0).mean()) if abort.any() else float("nan"),
        "p_late_accept_given_nonzero_early": float((late[~abort] > 0).mean()) if (~abort).any() else float("nan"),
    }


def main() -> None:
    rows = list(csv.DictReader(PATH.open()))
    gs = generations(rows)
    print("trial_rows", len(rows), "full_generations", len(gs))
    for suite in ("bbob", "quadratic", "all"):
        for split in ("discovery", "validation"):
            s = summarize(gs, split, suite)
            print(suite, split, " ".join(f"{k}={v:.3f}" if isinstance(v, float) else f"{k}={v}" for k, v in s.items()))
    # Fixed-policy sensitivity: half-generation check, no threshold tuning.
    gs_half = generations(rows, 0.5)
    print("\nHALF-GENERATION ZERO-ACCEPT SENSITIVITY")
    for suite in ("bbob", "quadratic", "all"):
        s = summarize(gs_half, "validation", suite)
        print(suite, "validation", " ".join(f"{k}={v:.3f}" if isinstance(v, float) else f"{k}={v}" for k, v in s.items()))


if __name__ == "__main__":
    main()

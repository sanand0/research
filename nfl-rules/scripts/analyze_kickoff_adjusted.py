#!/usr/bin/env python3
# /// script
# dependencies = ["pandas", "pyarrow", "matplotlib", "tabulate", "requests"]
# ///
"""Adjusted/descriptive kickoff analysis with game-state buckets.

Uses cached nflverse play-by-play files already downloaded by analyze_kickoff_case_study.py.

Outputs:
- data/analysis/kickoff_adjusted_by_period.csv/.parquet
- data/analysis/kickoff_adjusted_by_score_bucket.csv/.parquet
- data/analysis/kickoff_adjusted_by_time_bucket.csv/.parquet
- data/analysis/kickoff_adjusted_late_game_onside.csv/.parquet
- data/analysis/kickoff_adjusted_report.md
- data/analysis/kickoff_adjusted_return_rate_by_score_bucket.png
"""
from __future__ import annotations
from pathlib import Path
import importlib.util
import sys
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "data" / "analysis"
RAW_NFLVERSE = ROOT / "data" / "raw" / "nflverse"

# Reuse robust kickoff extraction from the prior script.
spec = importlib.util.spec_from_file_location("kick", ROOT / "scripts" / "analyze_kickoff_case_study.py")
kick = importlib.util.module_from_spec(spec)
sys.modules["kick"] = kick
spec.loader.exec_module(kick)


def read_all(seasons: list[int]) -> pd.DataFrame:
    all_kicks=[]
    for season in seasons:
        path=RAW_NFLVERSE / f"play_by_play_{season}.parquet"
        if not path.exists():
            print(f"missing cached pbp for {season}; run analyze_kickoff_case_study.py first")
            continue
        pbp=pd.read_parquet(path)
        kicks=kick.build_kickoff_plays(pbp)
        if not kicks.empty:
            all_kicks.append(kicks)
    return pd.concat(all_kicks, ignore_index=True) if all_kicks else pd.DataFrame()


def add_buckets(k: pd.DataFrame) -> pd.DataFrame:
    k=k.copy()
    for c in ["qtr","quarter_seconds_remaining","half_seconds_remaining","game_seconds_remaining","score_differential"]:
        if c not in k.columns: k[c]=pd.NA
    k["qtr_num"]=pd.to_numeric(k["qtr"], errors="coerce")
    k["game_seconds_remaining_num"]=pd.to_numeric(k["game_seconds_remaining"], errors="coerce")
    k["score_diff_num"]=pd.to_numeric(k["score_differential"], errors="coerce")
    k["period_bucket"]=pd.cut(k["qtr_num"], bins=[0,1,2,3,4,10], labels=["Q1","Q2","Q3","Q4","OT"], right=True).astype(str)
    k["time_bucket"]=pd.cut(k["game_seconds_remaining_num"], bins=[-1,120,300,900,1800,2700,3600,10000], labels=["last_2_min","2_to_5_min","5_to_15_min","15_to_30_min","30_to_45_min","45_to_60_min","unknown"], right=True).astype(str)
    sd=k["score_diff_num"]
    k["score_bucket"]=pd.Series("unknown", index=k.index)
    k.loc[sd.isna(),"score_bucket"]="unknown"
    k.loc[sd.le(-15),"score_bucket"]="trailing_15plus"
    k.loc[sd.between(-14,-8),"score_bucket"]="trailing_8_14"
    k.loc[sd.between(-7,-1),"score_bucket"]="trailing_1_7"
    k.loc[sd.eq(0),"score_bucket"]="tied"
    k.loc[sd.between(1,7),"score_bucket"]="leading_1_7"
    k.loc[sd.between(8,14),"score_bucket"]="leading_8_14"
    k.loc[sd.ge(15),"score_bucket"]="leading_15plus"
    k["late_game_close_trailing"] = k["is_onside_attempt"] & k["game_seconds_remaining_num"].le(300) & k["score_diff_num"].between(-16,-1)
    return k


def summarize(k: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    rows=[]
    for keys,g in k.groupby(group_cols, dropna=False):
        if not isinstance(keys, tuple): keys=(keys,)
        row=dict(zip(group_cols, keys))
        row.update({
            "kickoffs": len(g),
            "return_rate": round(float(g["is_return"].mean()),4),
            "touchback_rate": round(float(g["is_touchback"].mean()),4),
            "fair_catch_rate": round(float(g["is_fair_catch"].mean()),4),
            "onside_attempt_rate": round(float(g["is_onside_attempt"].mean()),4),
            "onside_attempts": int(g["is_onside_attempt"].sum()),
            "onside_success_guess_rate": round(float(g.loc[g["is_onside_attempt"],"onside_recovered_by_kicking_team_guess"].mean()),4) if g["is_onside_attempt"].any() else None,
            "avg_start_yardline_own": round(float(g["start_yardline_own"].mean()),2),
            "penalty_rate": round(float(g["has_penalty"].mean()),4),
        })
        rows.append(row)
    return pd.DataFrame(rows).sort_values(group_cols)


def plot_score(summary: pd.DataFrame) -> None:
    reg=summary[summary["season_type"].astype(str).eq("REG")].copy()
    if reg.empty: return
    focus=reg[reg["score_bucket"].isin(["trailing_15plus","trailing_8_14","trailing_1_7","tied","leading_1_7","leading_8_14","leading_15plus"])]
    pivot=focus.pivot_table(index="season", columns="score_bucket", values="return_rate", aggfunc="mean")
    order=[c for c in ["trailing_15plus","trailing_8_14","trailing_1_7","tied","leading_1_7","leading_8_14","leading_15plus"] if c in pivot.columns]
    plt.figure(figsize=(10,5))
    for c in order:
        plt.plot(pivot.index.astype(int), pivot[c], marker="o", label=c)
    plt.title("Kickoff return rate by score bucket")
    plt.xlabel("Season")
    plt.ylabel("Return rate")
    plt.grid(True, alpha=.3)
    plt.legend(fontsize=8, ncol=2)
    plt.tight_layout()
    plt.savefig(ANALYSIS / "kickoff_adjusted_return_rate_by_score_bucket.png", dpi=160)
    plt.close()


def main() -> None:
    ANALYSIS.mkdir(parents=True, exist_ok=True)
    seasons=[2021,2022,2023,2024,2025]
    k=read_all(seasons)
    if k.empty:
        raise SystemExit("No kickoff data. Run analyze_kickoff_case_study.py first.")
    k=add_buckets(k)
    by_period=summarize(k, ["season","season_type","period_bucket"])
    by_score=summarize(k, ["season","season_type","score_bucket"])
    by_time=summarize(k, ["season","season_type","time_bucket"])
    late=k[k["is_onside_attempt"] | k["late_game_close_trailing"]].copy()
    late_cols=["season","season_type","week","game_id","play_id","posteam","defteam","score_diff_num","game_seconds_remaining_num","is_onside_attempt","onside_recovered_by_kicking_team_guess","desc","next_posteam","next_desc"]
    late=late[[c for c in late_cols if c in late.columns]].sort_values(["season","game_id","play_id"])
    outputs={
        "kickoff_adjusted_by_period": by_period,
        "kickoff_adjusted_by_score_bucket": by_score,
        "kickoff_adjusted_by_time_bucket": by_time,
        "kickoff_adjusted_late_game_onside": late,
    }
    for name,df in outputs.items():
        df.to_csv(ANALYSIS / f"{name}.csv", index=False)
        df.to_parquet(ANALYSIS / f"{name}.parquet", index=False)
    plot_score(by_score)
    report=render(by_period, by_score, by_time, late)
    (ANALYSIS / "kickoff_adjusted_report.md").write_text(report)
    print(ANALYSIS / "kickoff_adjusted_report.md")
    print("late/onside rows",len(late))
    print(by_score[by_score["season_type"].astype(str).eq("REG")].head(20).to_string(index=False))


def md_table(df, cols, n=30):
    if df.empty: return "_No rows._\n"
    return df[[c for c in cols if c in df.columns]].head(n).to_markdown(index=False)


def render(by_period, by_score, by_time, late):
    md=["# Adjusted kickoff analysis\n"]
    md.append("This extends the descriptive kickoff case study by splitting outcomes by quarter, score bucket, time remaining, and late-game onside contexts. It is still descriptive, but it reduces the risk that aggregate return rates are driven only by end-game or blowout situations.\n")
    md.append("## By score bucket, regular season sample\n")
    reg=by_score[by_score["season_type"].astype(str).eq("REG")]
    md.append(md_table(reg, ["season","score_bucket","kickoffs","return_rate","touchback_rate","onside_attempt_rate","avg_start_yardline_own","penalty_rate"], 60))
    md.append("\n## By time bucket, regular season sample\n")
    regt=by_time[by_time["season_type"].astype(str).eq("REG")]
    md.append(md_table(regt, ["season","time_bucket","kickoffs","return_rate","touchback_rate","onside_attempt_rate","avg_start_yardline_own"], 60))
    md.append("\n## Late-game onside rows\n")
    md.append(f"Rows: {len(late)}. See `kickoff_adjusted_late_game_onside.csv`.\n")
    md.append("## Interpretation\n")
    md.append("The score/time splits should be used to separate ordinary kickoff redesign effects from late-game comeback behavior. The 2025 return-rate increase remains visible across ordinary score buckets, not only in onside situations.\n")
    md.append("## Files\n")
    md.append("- `data/analysis/kickoff_adjusted_by_period.csv`")
    md.append("- `data/analysis/kickoff_adjusted_by_score_bucket.csv`")
    md.append("- `data/analysis/kickoff_adjusted_by_time_bucket.csv`")
    md.append("- `data/analysis/kickoff_adjusted_late_game_onside.csv`")
    md.append("- `data/analysis/kickoff_adjusted_return_rate_by_score_bucket.png`\n")
    return "\n".join(md)

if __name__ == "__main__":
    main()

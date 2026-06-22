#!/usr/bin/env python3
# /// script
# dependencies = ["pandas", "pyarrow", "requests", "matplotlib", "tabulate"]
# ///
"""Analyze kickoff rule changes with cached nflverse play-by-play data.

Inputs:
- data/processed/rule_events.csv
- nflverse play-by-play parquet files, cached in data/raw/nflverse/

Outputs under data/analysis/:
- kickoff_rule_timeline.csv
- kickoff_pbp_summary_by_season.csv
- kickoff_pbp_summary_by_season_type.csv
- kickoff_examples.csv
- kickoff_case_study_report.md
- kickoff_return_touchback_rates.png
- kickoff_starting_field_position.png
"""
from __future__ import annotations

import argparse
import math
import re
from pathlib import Path
from urllib.parse import urlparse

import matplotlib.pyplot as plt
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
RAW_NFLVERSE = ROOT / "data" / "raw" / "nflverse"
ANALYSIS = ROOT / "data" / "analysis"
PROCESSED = ROOT / "data" / "processed"
PBP_URL = "https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_{season}.parquet"
UA = "Mozilla/5.0 (compatible; nfl-rules-research/0.1)"


def parse_seasons(text: str) -> list[int]:
    seasons: list[int] = []
    for part in text.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = [int(x) for x in part.split("-", 1)]
            seasons.extend(range(a, b + 1))
        else:
            seasons.append(int(part))
    return sorted(set(seasons))


def fetch_pbp(season: int, refresh: bool = False) -> Path | None:
    RAW_NFLVERSE.mkdir(parents=True, exist_ok=True)
    path = RAW_NFLVERSE / f"play_by_play_{season}.parquet"
    if path.exists() and path.stat().st_size > 0 and not refresh:
        return path
    url = PBP_URL.format(season=season)
    try:
        with requests.get(url, headers={"User-Agent": UA}, stream=True, timeout=120) as r:
            if r.status_code == 404:
                print(f"skip {season}: 404 {url}")
                return None
            r.raise_for_status()
            tmp = path.with_suffix(".parquet.tmp")
            with tmp.open("wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)
            tmp.replace(path)
        return path
    except Exception as e:
        print(f"skip {season}: {type(e).__name__}: {e}")
        return None


def read_pbp(path: Path) -> pd.DataFrame:
    # Read all columns. Annual parquet files are small enough for this case study.
    return pd.read_parquet(path)


def col(df: pd.DataFrame, name: str, default="") -> pd.Series:
    if name in df.columns:
        return df[name]
    return pd.Series([default] * len(df), index=df.index)


def boolish(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").fillna(0).astype(float) > 0


def build_kickoff_plays(pbp: pd.DataFrame) -> pd.DataFrame:
    df = pbp.copy()
    df["_row"] = range(len(df))
    for needed in ["season", "season_type", "week", "game_id", "play_id", "desc", "play_type", "posteam", "defteam", "yardline_100", "return_yards", "touchback", "epa"]:
        if needed not in df.columns:
            df[needed] = pd.NA

    desc = df["desc"].fillna("").astype(str)
    play_type = df["play_type"].fillna("").astype(str).str.lower()
    kickoff_attempt = boolish(df["kickoff_attempt"]) if "kickoff_attempt" in df.columns else pd.Series(False, index=df.index)
    is_kickoff = play_type.eq("kickoff") | kickoff_attempt | desc.str.contains(r"\bkicks?\b.*\b(?:kickoff|touchback|fair catch|onside|returned)\b", case=False, regex=True, na=False)

    kicks = df[is_kickoff].copy()
    if kicks.empty:
        return kicks

    kicks["is_touchback"] = boolish(kicks["touchback"]) if "touchback" in kicks.columns else False
    kicks["is_touchback"] = kicks["is_touchback"] | kicks["desc"].fillna("").str.contains("touchback", case=False, regex=False)
    kicks["is_fair_catch"] = kicks["desc"].fillna("").str.contains("fair catch", case=False, regex=False)
    kicks["is_onside_attempt"] = kicks["desc"].fillna("").str.contains("onside", case=False, regex=False)
    if "return_yards" in kicks.columns:
        return_yards = pd.to_numeric(kicks["return_yards"], errors="coerce")
    else:
        return_yards = pd.Series([math.nan] * len(kicks), index=kicks.index)
    kicks["return_yards_num"] = return_yards
    kicks["is_return"] = (~kicks["is_touchback"]) & ((return_yards.fillna(0) > 0) | kicks["desc"].fillna("").str.contains("return", case=False, regex=False))
    kicks["has_penalty"] = kicks["desc"].fillna("").str.contains("penalty", case=False, regex=False)

    # Find first following scrimmage/offensive play in same game to estimate starting field position.
    scrim_types = {"run", "pass", "no_play", "qb_kneel", "qb_spike"}
    df_sorted = df.sort_values(["game_id", "play_id", "_row"]).copy()
    df_sorted["_is_scrimmageish"] = df_sorted["play_type"].fillna("").astype(str).str.lower().isin(scrim_types) & df_sorted["posteam"].fillna("").astype(str).str.len().gt(0)
    scrims = df_sorted[df_sorted["_is_scrimmageish"]][["game_id", "play_id", "posteam", "yardline_100", "desc"]].copy()
    scrims = scrims.rename(columns={"play_id": "next_play_id", "posteam": "next_posteam", "yardline_100": "next_yardline_100", "desc": "next_desc"})

    next_rows = []
    for idx, k in kicks.sort_values(["game_id", "play_id", "_row"]).iterrows():
        cand = scrims[(scrims["game_id"] == k["game_id"]) & (pd.to_numeric(scrims["next_play_id"], errors="coerce") > pd.to_numeric(k["play_id"], errors="coerce"))]
        if cand.empty:
            next_rows.append((idx, pd.NA, pd.NA, pd.NA, pd.NA))
        else:
            n = cand.iloc[0]
            next_rows.append((idx, n["next_play_id"], n["next_posteam"], n["next_yardline_100"], n["next_desc"]))
    next_df = pd.DataFrame(next_rows, columns=["index", "next_play_id", "next_posteam", "next_yardline_100", "next_desc"]).set_index("index")
    kicks = kicks.join(next_df)
    kicks["next_yardline_100_num"] = pd.to_numeric(kicks["next_yardline_100"], errors="coerce")
    kicks["start_yardline_own"] = 100 - kicks["next_yardline_100_num"]
    kicks.loc[(kicks["start_yardline_own"] < 0) | (kicks["start_yardline_own"] > 100), "start_yardline_own"] = pd.NA

    # nflfastR kickoff rows use posteam as receiving team and defteam as kicking team on kickoffs.
    kicks["onside_recovered_by_kicking_team_guess"] = kicks["is_onside_attempt"] & kicks["defteam"].fillna("").astype(str).eq(kicks["next_posteam"].fillna("").astype(str))
    return kicks


def summarize_kickoffs(kicks: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    if kicks.empty:
        return pd.DataFrame(columns=group_cols + ["kickoffs"])
    g = kicks.groupby(group_cols, dropna=False)
    rows = []
    for keys, x in g:
        if not isinstance(keys, tuple):
            keys = (keys,)
        row = dict(zip(group_cols, keys))
        kickoffs = len(x)
        row.update({
            "kickoffs": kickoffs,
            "return_count": int(x["is_return"].sum()),
            "return_rate": round(float(x["is_return"].mean()), 4),
            "touchback_count": int(x["is_touchback"].sum()),
            "touchback_rate": round(float(x["is_touchback"].mean()), 4),
            "fair_catch_count": int(x["is_fair_catch"].sum()),
            "fair_catch_rate": round(float(x["is_fair_catch"].mean()), 4),
            "onside_attempt_count": int(x["is_onside_attempt"].sum()),
            "onside_attempt_rate": round(float(x["is_onside_attempt"].mean()), 4),
            "onside_success_guess_count": int(x["onside_recovered_by_kicking_team_guess"].sum()),
            "onside_success_guess_rate": round(float(x.loc[x["is_onside_attempt"], "onside_recovered_by_kicking_team_guess"].mean()), 4) if x["is_onside_attempt"].any() else None,
            "penalty_count": int(x["has_penalty"].sum()),
            "penalty_rate": round(float(x["has_penalty"].mean()), 4),
            "avg_return_yards": round(float(x.loc[x["is_return"], "return_yards_num"].mean()), 2) if x["is_return"].any() else None,
            "avg_start_yardline_own": round(float(x["start_yardline_own"].mean()), 2),
            "median_start_yardline_own": round(float(x["start_yardline_own"].median()), 2),
            "missing_start_yardline_count": int(x["start_yardline_own"].isna().sum()),
        })
        rows.append(row)
    return pd.DataFrame(rows).sort_values(group_cols)


def build_rule_timeline() -> pd.DataFrame:
    events = pd.read_csv(PROCESSED / "rule_events.csv").fillna("")
    manual = events["manual_lineage"].astype(str)
    auto = events["auto_lineage"].astype(str)
    kickoff = events[(manual.eq("kickoff")) | ((manual.eq("")) & auto.eq("kickoff")) | auto.eq("kickoff")].copy()
    cols = ["year", "status", "item_type", "proposal_number", "proposer", "canonical_change_id", "manual_title", "auto_sublineage", "status_lifecycle", "target_metric_guess", "summary", "source_key"]
    kickoff = kickoff[[c for c in cols if c in kickoff.columns]].sort_values(["year", "status", "source_key", "proposal_number"])
    return kickoff


def plot_summary(by_season: pd.DataFrame) -> None:
    if by_season.empty:
        return
    reg = by_season[by_season.get("season_type", "REG").astype(str).eq("REG")].copy() if "season_type" in by_season.columns else by_season.copy()
    if reg.empty:
        reg = by_season.copy()
    x = reg["season"].astype(int)

    plt.figure(figsize=(8, 4.5))
    plt.plot(x, reg["return_rate"], marker="o", label="Return rate")
    plt.plot(x, reg["touchback_rate"], marker="o", label="Touchback rate")
    plt.title("Kickoff return and touchback rates")
    plt.xlabel("Season")
    plt.ylabel("Rate")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(ANALYSIS / "kickoff_return_touchback_rates.png", dpi=160)
    plt.close()

    plt.figure(figsize=(8, 4.5))
    plt.plot(x, reg["avg_start_yardline_own"], marker="o", label="Average start yardline")
    plt.title("Estimated starting field position after kickoffs")
    plt.xlabel("Season")
    plt.ylabel("Own-yardline estimate")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(ANALYSIS / "kickoff_starting_field_position.png", dpi=160)
    plt.close()


def md_table(df: pd.DataFrame, cols: list[str], n: int = 20) -> str:
    if df.empty:
        return "_No rows._\n"
    return df[[c for c in cols if c in df.columns]].head(n).to_markdown(index=False)


def report(rule_timeline: pd.DataFrame, by_season: pd.DataFrame, by_type: pd.DataFrame, examples: pd.DataFrame, seasons: list[int], skipped: list[int]) -> str:
    out = []
    out.append("# Kickoff case study\n")
    out.append(f"Requested seasons: {', '.join(map(str, seasons))}.\n")
    if skipped:
        out.append(f"Skipped unavailable seasons: {', '.join(map(str, skipped))}.\n")
    out.append("## Why kickoff is the best first deep dive\n")
    out.append("Kickoff is the clearest current rule laboratory: the dataset shows historical kick-spot changes, wedge restrictions, the 2023 fair-catch experiment, the 2024 dynamic kickoff trial, 2025 permanent adoption/modification, and 2026 tuning proposals/approvals.\n")
    out.append("## Rule timeline rows\n")
    out.append(md_table(rule_timeline, ["year", "status", "proposal_number", "canonical_change_id", "auto_sublineage", "summary", "source_key"], 30))
    out.append("\n## Play-by-play summary by regular season\n")
    reg = by_type[by_type["season_type"].astype(str).eq("REG")] if "season_type" in by_type.columns else by_season
    out.append(md_table(reg, ["season", "season_type", "kickoffs", "return_rate", "touchback_rate", "fair_catch_rate", "onside_attempt_rate", "onside_success_guess_rate", "avg_return_yards", "avg_start_yardline_own", "penalty_rate"], 20))
    out.append("\n## Caveats\n")
    out.append("- `start_yardline_own` is estimated from the next scrimmage-like play in the same game.")
    out.append("- `onside_success_guess` assumes nflverse kickoff rows use `defteam` as the kicking team and compares it with the next offensive team.")
    out.append("- 2026 rules are included in the rule timeline but no 2026 play-by-play is expected at this date.")
    out.append("- The dynamic kickoff causal story should be written using 2021-2025 actuals plus 2026 rules as future design changes.")
    out.append("\n## Files\n")
    out.append("- `data/analysis/kickoff_rule_timeline.csv`")
    out.append("- `data/analysis/kickoff_pbp_summary_by_season.csv`")
    out.append("- `data/analysis/kickoff_pbp_summary_by_season_type.csv`")
    out.append("- `data/analysis/kickoff_examples.csv`")
    out.append("- `data/analysis/kickoff_return_touchback_rates.png`")
    out.append("- `data/analysis/kickoff_starting_field_position.png`")
    return "\n".join(out) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seasons", default="2021-2025", help="Comma/range list, e.g. 2021-2025 or 2023,2024")
    parser.add_argument("--refresh", action="store_true", help="Refetch cached nflverse parquet files")
    args = parser.parse_args()

    ANALYSIS.mkdir(parents=True, exist_ok=True)
    seasons = parse_seasons(args.seasons)
    all_kicks = []
    skipped = []
    for season in seasons:
        path = fetch_pbp(season, refresh=args.refresh)
        if path is None:
            skipped.append(season)
            continue
        pbp = read_pbp(path)
        kicks = build_kickoff_plays(pbp)
        if kicks.empty:
            skipped.append(season)
            continue
        all_kicks.append(kicks)
        print(f"season={season} pbp_rows={len(pbp)} kickoff_rows={len(kicks)} cache={path}")

    rule_timeline = build_rule_timeline()
    rule_timeline.to_csv(ANALYSIS / "kickoff_rule_timeline.csv", index=False)
    rule_timeline.to_parquet(ANALYSIS / "kickoff_rule_timeline.parquet", index=False)

    if all_kicks:
        kicks_all = pd.concat(all_kicks, ignore_index=True)
        by_season = summarize_kickoffs(kicks_all, ["season"])
        by_type = summarize_kickoffs(kicks_all, ["season", "season_type"])
        examples = kicks_all.sort_values(["season", "game_id", "play_id"]).head(200)
        ex_cols = ["season", "season_type", "week", "game_id", "play_id", "posteam", "defteam", "is_touchback", "is_return", "is_fair_catch", "is_onside_attempt", "return_yards_num", "start_yardline_own", "desc", "next_desc"]
        examples = examples[[c for c in ex_cols if c in examples.columns]]
    else:
        by_season = pd.DataFrame()
        by_type = pd.DataFrame()
        examples = pd.DataFrame()

    by_season.to_csv(ANALYSIS / "kickoff_pbp_summary_by_season.csv", index=False)
    by_type.to_csv(ANALYSIS / "kickoff_pbp_summary_by_season_type.csv", index=False)
    examples.to_csv(ANALYSIS / "kickoff_examples.csv", index=False)
    if not by_season.empty:
        by_season.to_parquet(ANALYSIS / "kickoff_pbp_summary_by_season.parquet", index=False)
    if not by_type.empty:
        by_type.to_parquet(ANALYSIS / "kickoff_pbp_summary_by_season_type.parquet", index=False)
    if not examples.empty:
        examples.to_parquet(ANALYSIS / "kickoff_examples.parquet", index=False)
    plot_summary(by_type)
    text = report(rule_timeline, by_season, by_type, examples, seasons, skipped)
    (ANALYSIS / "kickoff_case_study_report.md").write_text(text)
    print(ANALYSIS / "kickoff_case_study_report.md")
    if not by_type.empty:
        print(by_type.to_string(index=False))


if __name__ == "__main__":
    main()

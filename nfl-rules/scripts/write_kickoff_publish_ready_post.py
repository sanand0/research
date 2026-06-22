#!/usr/bin/env python3
# /// script
# dependencies = ["pandas", "tabulate"]
# ///
from __future__ import annotations
from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
ANALYSIS=ROOT/'data'/'analysis'
OUT=ANALYSIS/'kickoff_publish_ready_post.md'

def pct(x): return f"{float(x)*100:.1f}%"
def own(x): return f"own {float(x):.1f}"

def main():
    reg=pd.read_csv(ANALYSIS/'kickoff_pbp_summary_by_season_type.csv')
    reg=reg[reg.season_type.astype(str).eq('REG')].copy().sort_values('season')
    score=pd.read_csv(ANALYSIS/'kickoff_adjusted_by_score_bucket.csv')
    score=score[score.season_type.astype(str).eq('REG') & score.score_bucket.isin(['trailing_1_7','tied','leading_1_7'])].copy()
    def v(y,c): return float(reg.loc[reg.season.eq(y), c].iloc[0])
    table=reg[['season','return_rate','touchback_rate','avg_start_yardline_own','penalty_rate']].copy()
    table['return_rate']=table.return_rate.map(pct)
    table['touchback_rate']=table.touchback_rate.map(pct)
    table['penalty_rate']=table.penalty_rate.map(pct)
    table['avg_start_yardline_own']=table.avg_start_yardline_own.map(lambda x:f"{x:.1f}")
    table=table.rename(columns={'avg_start_yardline_own':'avg_start_own'})
    ordinary=score[score.season.isin([2023,2024,2025])][['season','score_bucket','return_rate','touchback_rate','avg_start_yardline_own']].copy()
    ordinary['return_rate']=ordinary.return_rate.map(pct)
    ordinary['touchback_rate']=ordinary.touchback_rate.map(pct)
    ordinary['avg_start_yardline_own']=ordinary.avg_start_yardline_own.map(lambda x:f"{x:.1f}")
    ordinary=ordinary.rename(columns={'avg_start_yardline_own':'avg_start_own'})
    md=[]
    md.append('# Kickoff is the NFL’s rules laboratory\n')
    md.append('The NFL did not merely change the kickoff. It ran a live governance experiment in public.\n')
    md.append('Kickoff is where the league’s rulemaking problem is easiest to see. It wants fewer high-speed collisions, but not a dead play. It wants more returns, but not cheap field position. It wants comeback equity, but not chaos. So it keeps turning knobs: touchbacks, fair catches, alignment zones, landing zones, onside-kick declarations, K-Balls, and out-of-bounds incentives.\n')
    md.append('The result looks less like a law book and more like a control system.\n')
    md.append('## The swing\n')
    md.append(f'In 2023, only **{pct(v(2023,"return_rate"))}** of regular-season kickoffs were returned. Touchbacks were **{pct(v(2023,"touchback_rate"))}**. By 2025, returns had jumped to **{pct(v(2025,"return_rate"))}**, while touchbacks fell to **{pct(v(2025,"touchback_rate"))}**.\n')
    md.append(f'The price was field position. Estimated average starting field position after kickoffs moved from **{own(v(2023,"avg_start_yardline_own"))}** in 2023 to **{own(v(2025,"avg_start_yardline_own"))}** in 2025. The league bought more live returns by giving offenses better starting position.\n')
    md.append('![Kickoff return and touchback rates](kickoff_return_touchback_rates.png)\n')
    md.append('## What changed\n')
    md.append('The sequence is the story.\n')
    md.append('- **2022:** a prior free-kick formation change became permanent.')
    md.append('- **2023:** the fair-catch touchback incentive reduced returns sharply.')
    md.append('- **2024:** the dynamic kickoff trial tried to restore returns without restoring the old collision geometry.')
    md.append('- **2025:** the dynamic kickoff became permanent and was tuned again.')
    md.append('- **2026:** rule changes keep tuning onside-kick and out-of-bounds incentives.\n')
    md.append('That is rulemaking as iterative mechanism design.\n')
    md.append('## The numbers\n')
    md.append(table.to_markdown(index=False))
    md.append('\nThe jump is not just late-game onside-kick noise. In ordinary states—tied, trailing by one score, or leading by one score—the 2025 return rate is still dramatically higher than 2023.\n')
    md.append(ordinary.to_markdown(index=False))
    md.append('\n![Kickoff return rate by score bucket](kickoff_adjusted_return_rate_by_score_bucket.png)\n')
    md.append('## The reusable lesson\n')
    md.append('The usual way to read a rule change is: “what changed?” That misses the point. A better schema is:\n')
    md.append('1. What metric was the league trying to move?')
    md.append('2. What mechanism did it use?')
    md.append('3. What incentive did that create?')
    md.append('4. What second-order effect appeared?')
    md.append('5. What patch came next?\n')
    md.append('Kickoff has all five. The target metrics are safety, return rate, touchback rate, field position, comeback equity, penalty burden, and watchability. The mechanisms are spatial constraints and incentive changes. The patches are already visible in 2025 and 2026.\n')
    md.append('That framing travels outside football. Enterprises change rules all the time: review thresholds, escalation policies, pricing rules, incentive schemes, approval workflows. The mistake is to treat these as static policies. They are control systems. A good rule should have a target metric, an expected behavioral response, a monitoring plan, and an explicit path for patches.\n')
    md.append('## Caveats\n')
    md.append('This is descriptive, not causal. Starting field position is estimated from the next scrimmage-like play in nflverse play-by-play. Onside success is inferred from possession after the kick. A stronger model should control for score, time, stadium, weather, postseason, and late-game comeback situations.\n')
    md.append('## Reproduce\n')
    md.append('```bash\nuv run scripts/analyze_kickoff_case_study.py --seasons 2021-2025\nuv run scripts/analyze_kickoff_adjusted.py\nuv run scripts/write_kickoff_publish_ready_post.py\n```\n')
    OUT.write_text('\n'.join(md))
    print(OUT)

if __name__=='__main__': main()

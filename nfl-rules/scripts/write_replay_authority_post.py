#!/usr/bin/env python3
# /// script
# dependencies = ["pandas", "tabulate"]
# ///
from __future__ import annotations
from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
ANALYSIS=ROOT/'data'/'analysis'
OUT=ANALYSIS/'replay_authority_post.md'

def main():
    m=pd.read_csv(ANALYSIS/'replay_authority_map.csv').fillna('')
    ev=pd.read_csv(ANALYSIS/'replay_authority_events.csv').fillna('')
    stage=m[['stage_order','stage_label','event_count','first_year','last_year','review_objects']].copy()
    examples=ev[['year','status','authority_shift','review_object','summary']].head(12).copy()
    md=[]
    md.append('# The NFL is automating judgment at the edges first\n')
    md.append('Replay changes are usually described as “more review.” That undersells what is happening. The NFL is redesigning who has authority to correct mistakes.\n')
    md.append('The direction is clear: start with coach challenges, expand booth review, add replay assist for fast objective corrections, centralize high-stakes consultation, and keep an emergency override for institutional failure.\n')
    md.append('That is not just a sports story. It is a governance pattern. When institutions add automation or AI, they rarely replace judgment all at once. They automate the edges first.\n')
    md.append('## The authority ladder\n')
    md.append(stage.to_markdown(index=False))
    md.append('\n![Replay authority map](replay_authority_map.png)\n')
    md.append('## What changed\n')
    md.append('The useful unit is not the replay rule. It is the authority shift.\n')
    md.append('- **Coach / club challenge**: teams get more ways to ask for correction.')
    md.append('- **Replay official / booth review**: the system can initiate correction without a coach spending a challenge.')
    md.append('- **Replay assist**: correction becomes lightweight and fast, especially for objective aspects of a play.')
    md.append('- **League consultation**: central authority enters high-stakes judgment calls, such as disqualification.')
    md.append('- **Emergency centralized override**: the league plans for cases where normal officiating capacity breaks.\n')
    md.append('That ladder matters because each step changes not just accuracy, but accountability. Who asks? Who decides? What evidence is enough? What remains on the field?\n')
    md.append('## Representative events\n')
    md.append(examples.to_markdown(index=False))
    md.append('\n## The reusable lesson\n')
    md.append('This is how institutions adopt automation safely: not by replacing the whole workflow, but by adding correction loops around it. First, create an appeal path. Then allow independent review. Then add assistive correction. Then centralize the rare, high-stakes cases. Finally, define emergency override.\n')
    md.append('That applies directly to AI governance. Good human-in-the-loop design is not “human or machine.” It is a map of authority: who initiates, who decides, what evidence is required, and which decisions are too consequential to leave local.\n')
    md.append('## Caveat\n')
    md.append('This analysis covers the structured rows currently captured in the NFL rules dataset. It is strongest for 2023-2026. Historical replay evolution should be added once older annual rulebook sources are located.\n')
    md.append('## Reproduce\n')
    md.append('```bash\nuv run scripts/analyze_replay_authority.py\nuv run scripts/build_replay_authority_map.py\nuv run scripts/write_replay_authority_post.py\n```\n')
    OUT.write_text('\n'.join(md))
    print(OUT)
    print(f'words={len(OUT.read_text().split())}')

if __name__=='__main__': main()

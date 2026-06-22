#!/usr/bin/env python3
# /// script
# dependencies = ["pandas", "pyarrow", "tabulate"]
# ///
from __future__ import annotations
from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
PROCESSED=ROOT/'data'/'processed'
ANALYSIS=ROOT/'data'/'analysis'

def main():
    ANALYSIS.mkdir(parents=True, exist_ok=True)
    e=pd.read_csv(PROCESSED/'rule_events.csv').fillna('')
    c=pd.read_csv(PROCESSED/'rule_changes.csv').fillna('')
    by=e.groupby(['source_quality_tier','analysis_include_default'], dropna=False).agg(
        events=('event_id','count'),
        min_score=('source_quality_score','min'),
        max_score=('source_quality_score','max'),
        sources=('source_key', lambda x:';'.join(sorted(set(map(str,x)))))
    ).reset_index().sort_values(['max_score','events'], ascending=[False,False])
    by.to_csv(ANALYSIS/'source_quality_summary.csv', index=False)
    by.to_parquet(ANALYSIS/'source_quality_summary.parquet', index=False)
    default_changes=c[c['analysis_include_default'].astype(str).isin(['True','true','1']) | (c['analysis_include_default'] == True)]
    seed_changes=c[~(c.index.isin(default_changes.index))]
    md=['# Source quality report\n']
    md.append('Rows are now tagged with a source-quality tier and default analysis inclusion flag. Use default-quality rows for public claims; use seed rows for hypothesis generation and historical framing.\n')
    md.append('## Event source quality\n')
    md.append(by.to_markdown(index=False))
    md.append('\n## Canonical changes\n')
    md.append(f'- Default-analysis canonical changes: {len(default_changes)}')
    md.append(f'- Seed / non-default canonical changes: {len(seed_changes)}\n')
    md.append('## Recommendation\n')
    md.append('For public analysis, filter `analysis_include_default == True`. For ideation, lineage discovery, and historical hypotheses, include seed rows but label them clearly.\n')
    (ANALYSIS/'source_quality_report.md').write_text('\n'.join(md))
    print(ANALYSIS/'source_quality_report.md')
    print(by.to_string(index=False))

if __name__=='__main__': main()

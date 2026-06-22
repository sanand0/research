#!/usr/bin/env python3
# /// script
# dependencies = ["pandas", "rapidfuzz", "pyarrow", "tabulate"]
# ///
from __future__ import annotations
from pathlib import Path
import pandas as pd
from rapidfuzz import fuzz

ROOT=Path(__file__).resolve().parents[1]
ANALYSIS=ROOT/'data'/'analysis'

def main():
    ANALYSIS.mkdir(parents=True, exist_ok=True)
    df=pd.read_csv(ROOT/'rules.csv').fillna('')
    online=df[df.source_key.eq('nflops_rulebook_2025_changes')].copy()
    pdf=df[df.source_key.eq('nflops_rulebook_2025_pdf')].copy()
    rows=[]
    refs=sorted(set(online.rulebook_ref)|set(pdf.rulebook_ref))
    for ref in refs:
        o=online[online.rulebook_ref.eq(ref)]
        p=pdf[pdf.rulebook_ref.eq(ref)]
        os=o.summary.iloc[0] if len(o) else ''
        ps=p.summary.iloc[0] if len(p) else ''
        rows.append({
            'rulebook_ref': ref,
            'online_present': bool(len(o)),
            'pdf_present': bool(len(p)),
            'text_similarity': round(fuzz.token_set_ratio(os, ps),1) if os and ps else None,
            'online_summary': os,
            'pdf_summary': ps,
        })
    audit=pd.DataFrame(rows).sort_values(['online_present','pdf_present','rulebook_ref'], ascending=[False,False,True])
    audit.to_csv(ANALYSIS/'rulebook_2025_online_pdf_audit.csv', index=False)
    audit.to_parquet(ANALYSIS/'rulebook_2025_online_pdf_audit.parquet', index=False)
    md=['# 2025 rulebook online-vs-PDF audit\n']
    md.append('This compares the online NFL Ops 2025 rulebook change list against the official 2025 rulebook PDF extraction. Both sources currently produce the same six rulebook references.\n')
    md.append(audit.to_markdown(index=False))
    md.append('\n## Interpretation\n')
    if audit.online_present.all() and audit.pdf_present.all():
        md.append('All rulebook references are present in both online and PDF sources. Keep both rows at event/source level for auditability; use `rule_changes.csv` for canonical-level analysis.\n')
    else:
        md.append('Some references are missing from one side. Review before treating either source as complete.\n')
    (ANALYSIS/'rulebook_2025_online_pdf_audit.md').write_text('\n'.join(md))
    print(ANALYSIS/'rulebook_2025_online_pdf_audit.md')
    print(audit[['rulebook_ref','online_present','pdf_present','text_similarity']].to_string(index=False))

if __name__=='__main__': main()

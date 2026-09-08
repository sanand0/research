#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["rdata>=1.0", "pandas>=2.2", "numpy>=2.0"]
# ///
"""Extract outcome-blind, future-independent early movement features from NestTool RDS."""
from pathlib import Path
import numpy as np
import pandas as pd
import rdata

SRC=Path('candidates/red-kite-nesttool/repo/input_data_prepared.rds')
OUT=Path('candidates/red-kite-nesttool/h005_early_predictors.csv')
obj=rdata.conversion.convert(rdata.parser.parse_file(SRC))
s=obj['summary']
keep=['year_id','bird_id','year','sex','age_cy','nest','MCP95Settle','MCP95Incu1','MCP99Settle','MCP99Incu1']
d=s[keep].copy()
# Only seasons with a field-observed nesting attempt belong to the later success estimand.
d=d[d['nest'].astype(str).eq('nest')].copy()
for c in ['MCP95Settle','MCP95Incu1','MCP99Settle','MCP99Incu1','age_cy']:
    d[c]=pd.to_numeric(d[c],errors='coerce')
# Values of 1 can be synthetic fills for a missing phase in data_prep; reject them rather than treat as real 1 m^2 areas.
for c in ['MCP95Settle','MCP95Incu1','MCP99Settle','MCP99Incu1']:
    d.loc[d[c] == 1, c]=np.nan
OUT.parent.mkdir(parents=True,exist_ok=True)
d.to_csv(OUT,index=False)
print('nest_attempt_rows',len(d),'unique_birds',d['bird_id'].nunique())
print('years',int(pd.to_numeric(d['year'],errors='coerce').min()),int(pd.to_numeric(d['year'],errors='coerce').max()))
print('sex',d['sex'].value_counts(dropna=False).to_dict())
print('complete95',int(d[['MCP95Settle','MCP95Incu1']].notna().all(axis=1).sum()))
print('complete99',int(d[['MCP99Settle','MCP99Incu1']].notna().all(axis=1).sum()))
print('success_column_persisted', 'success' in d.columns)

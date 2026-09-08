#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["rdata>=1.0", "pandas>=2.2"]
# ///
"""Outcome-seal design check: count only success availability, never values."""
import pandas as pd, rdata
obj=rdata.conversion.convert(rdata.parser.parse_file('candidates/red-kite-nesttool/repo/input_data_prepared.rds'))
s=obj['summary'][['year_id','success']]
f=pd.read_csv('analysis/red_kite_h005_features.csv')[['year_id']]
d=f.merge(s,on='year_id',how='left')
print('eligible_features',len(d),'success_label_available',int(d['success'].notna().sum()),'success_missing',int(d['success'].isna().sum()))

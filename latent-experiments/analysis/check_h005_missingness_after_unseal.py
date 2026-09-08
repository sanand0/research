#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["rdata>=1.0", "pandas>=2.2"]
# ///
"""Post-unseal H005 diagnostic: inspect outcome availability only, never yes/no values."""
import pandas as pd
import rdata

features = pd.read_csv('analysis/red_kite_h005_features.csv')
obj = rdata.conversion.convert(rdata.parser.parse_file('candidates/red-kite-nesttool/repo/input_data_prepared.rds'))
outcomes = obj['summary'][['year_id', 'success']].copy()
data = features.merge(outcomes, on='year_id', how='left', validate='one_to_one')
text = data['success'].astype('string').str.strip()
known = data['success'].notna() & text.ne('')
print('eligible', len(data), 'known', int(known.sum()), 'missing_or_blank', int((~known).sum()))
print('by_year', data.assign(known=known).groupby('year')['known'].agg(['count','sum']).to_dict('index'))
print('by_sex', data.assign(known=known).groupby('sex')['known'].agg(['count','sum']).to_dict('index'))
for col in ['contraction95','log_mcp95_incu1','contraction99','age_cy','Settle','Incu1']:
    a = pd.to_numeric(data.loc[known, col], errors='coerce')
    b = pd.to_numeric(data.loc[~known, col], errors='coerce')
    print(col, 'known_mean', round(float(a.mean()), 4), 'missing_mean', round(float(b.mean()), 4) if len(b) else None)

#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["rdata>=1.0", "pandas>=2.2", "numpy>=2.0"]
# ///
"""Build leak-free H005 early movement features; do not access success values."""
from pathlib import Path
import numpy as np
import pandas as pd
import rdata

RDS=Path('candidates/red-kite-nesttool/repo/input_data_prepared.rds')
PRED=Path('candidates/red-kite-nesttool/h005_early_predictors.csv')
OUT=Path('analysis/red_kite_h005_features.csv')
obj=rdata.conversion.convert(rdata.parser.parse_file(RDS))
m=obj['movementtrack'][['id','t_']].copy()
m['doy']=pd.to_datetime(m['t_'],unit='s',utc=True).dt.dayofyear
m['phase']=np.select([m.doy.between(70,96),m.doy.between(97,112)],['Settle','Incu1'],'other')
c=m[m.phase.isin(['Settle','Incu1'])].groupby(['id','phase'],observed=True).size().unstack(fill_value=0)
d=pd.read_csv(PRED).set_index('year_id').join(c,how='left')
d=d.dropna(subset=['MCP95Settle','MCP95Incu1','MCP99Settle','MCP99Incu1']).copy()
d=d[(d['Settle']>=100)&(d['Incu1']>=100)].copy()
d['log_mcp95_incu1']=np.log(d['MCP95Incu1'])
d['contraction95']=np.log(d['MCP95Settle'])-np.log(d['MCP95Incu1'])
d['log_mcp99_incu1']=np.log(d['MCP99Incu1'])
d['contraction99']=np.log(d['MCP99Settle'])-np.log(d['MCP99Incu1'])
d.reset_index().to_csv(OUT,index=False)
print('eligible',len(d),'birds',d['bird_id'].nunique(),'years',d['year'].nunique())
print('sex',d['sex'].value_counts().to_dict())
print('contraction95 median',round(float(d['contraction95'].median()),3),'contracting proportion',round(float((d['contraction95']>0).mean()),3))

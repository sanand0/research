#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2.0", "pandas>=2.2"]
# ///
"""Build outcome-blind H004 colony features from May/June/August 2014."""
from pathlib import Path
import numpy as np
import pandas as pd

SRC=Path('candidates/honey-bee-peirson/predictors_2014_alberta.csv')
OUT=Path('analysis/bee_h004_features.csv')
d=pd.read_csv(SRC, parse_dates=['Inspection Date'])
meta=d.drop_duplicates('Colony Number').set_index('Colony Number')[['Region','Apiary','Patties','Fumagillin','ColonyGroup']]
rows=[]
for cid,g in d.dropna(subset=['Adults']).groupby('Colony Number'):
    g=g.sort_values('Inspection Date')
    if set(g['Date']) != {'May 2014','June 2014','August 2014'}: continue
    v=g.set_index('Date')
    days=(g['Inspection Date']-g['Inspection Date'].min()).dt.days.to_numpy(float)
    y=np.log1p(g['Adults'].to_numpy(float))
    slope=float(np.polyfit(days,y,1)[0]*30)
    recent=float((np.log1p(v.at['August 2014','Adults'])-np.log1p(v.at['June 2014','Adults']))/((v.at['August 2014','Inspection Date']-v.at['June 2014','Inspection Date']).days/30))
    rows.append({'Colony Number':cid,'aug_log_adults':float(np.log1p(v.at['August 2014','Adults'])),'slope_3pt':slope,'slope_recent':recent})
f=pd.DataFrame(rows).set_index('Colony Number').join(meta).reset_index()
assert len(f)==225
f.to_csv(OUT,index=False)
print(f'features={len(f)} regions={f.Region.value_counts().to_dict()} apiaries={f.Apiary.nunique()}')

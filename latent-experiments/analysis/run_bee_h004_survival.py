#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2.0", "pandas>=2.2", "statsmodels>=0.14"]
# ///
"""Frozen H004 test: summer adult-population history vs first-winter survival."""
from __future__ import annotations
import io, json, urllib.request
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
import statsmodels.api as sm

URL='https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0288953.s002&type=supplementary'
FEATURES=Path('analysis/bee_h004_features.csv')
OUT=Path('analysis/bee_h004_survival_results.json')

f=pd.read_csv(FEATURES)
with urllib.request.urlopen(URL, timeout=30) as r:
    # Raw outcome-containing source is held in memory only and never persisted.
    raw=pd.read_csv(io.BytesIO(r.read()), usecols=['Colony Number','Date','Viable','Colony Death'])
ids=set(f['Colony Number'])
r=raw[raw['Colony Number'].isin(ids)].copy()
# Primary endpoint: viable at the April 2015 post-winter assessment.
a=r[r['Date'].eq('April 2015')][['Colony Number','Viable']].drop_duplicates('Colony Number')
a['survived_first_winter']=a['Viable'].map({'Viable':1,'Not Viable':0})
# If a colony lacks an April status, count it dead only when the source explicitly records a death by then.
order={'May 2014':0,'June 2014':1,'August 2014':2,'November 2014':3,'April 2015':4}
early=r[r['Date'].isin(order)].copy()
early['_ord']=early['Date'].map(order)
dead=set(early.loc[(early['Colony Death'].eq(1)) & (early['_ord']<=4),'Colony Number'])
known=dict(zip(a['Colony Number'],a['survived_first_winter']))
for cid in ids:
    if cid not in known and cid in dead: known[cid]=0
out=pd.DataFrame({'Colony Number':list(known),'survived_first_winter':list(known.values())}).dropna()
d=f.merge(out,on='Colony Number',how='inner')

for col in ['aug_log_adults','slope_3pt','slope_recent']:
    d[col+'_z']=(d[col]-d[col].mean())/d[col].std()

def fit(formula):
    m=smf.glm(formula,data=d,family=sm.families.Binomial()).fit()
    term=[x for x in m.params.index if x.startswith('slope_')][0]
    b=float(m.params[term]); se=float(m.bse[term])
    return {'n':int(m.nobs),'beta':b,'or':float(np.exp(b)),'ci95':[float(np.exp(b-1.96*se)),float(np.exp(b+1.96*se))],'p':float(m.pvalues[term])}

results={
 'endpoint_counts':{'n':int(len(d)),'survived':int(d.survived_first_winter.sum()),'failed':int((1-d.survived_first_winter).sum())},
 'primary':fit('survived_first_winter ~ aug_log_adults_z + slope_3pt_z + C(Region) + C(Patties) + C(Fumagillin)'),
 'recent_slope':fit('survived_first_winter ~ aug_log_adults_z + slope_recent_z + C(Region) + C(Patties) + C(Fumagillin)'),
 'apiary_fixed':fit('survived_first_winter ~ aug_log_adults_z + slope_3pt_z + C(Apiary) + C(Patties) + C(Fumagillin)'),
}
OUT.write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results,indent=2))

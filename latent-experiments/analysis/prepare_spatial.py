#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2.0", "pandas>=2.2", "statsmodels>=0.14"]
# ///
"""Build an outcome-blind off-territory propensity sensitivity covariate.

This follows LaRocque et al.'s core-feeder/day definitions, then uses the individual's
mean residual from the published fixed-effect structure as a transparent Python
approximation to their random-intercept off-territory propensity.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT=Path(__file__).resolve().parents[1]
A=ROOT/'candidates/chickadees'
OUT=ROOT/'analysis'
vis=pd.read_csv(A/'data_FeederVisits.csv')
all_dates=pd.read_csv(A/'data_AllDates.csv')
feeders=['02A','04A','09A','10A','11A','12A','14A','16A']
counts=vis.groupby(['TransponderHexCode','Feeder']).size().unstack(fill_value=0).reindex(columns=feeders,fill_value=0)
core=[]
for bird,row in counts.iterrows():
    vals=row.to_numpy()
    order=np.argsort(-vals, kind='stable')
    top=vals[order[0]]; top2=vals[order[1]] if len(vals)>1 else 0
    pct=100*top/(top+top2) if top+top2 else np.nan
    chosen='09A, 11A' if pct<60 else feeders[order[0]]
    core.append((bird,chosen,pct))
core=pd.DataFrame(core,columns=['TransponderHexCode','CoreFeeder','PercentCoreFeeder'])
v=vis.merge(core,on='TransponderHexCode',how='left')
v['onT']=[int(f in {x.strip() for x in str(c).split(',')}) for f,c in zip(v.Feeder,v.CoreFeeder)]
v['offT']=1-v['onT']
daily=v.groupby(['VisitDate','TransponderHexCode'],as_index=False).agg(offT=('offT','max'))
d=all_dates[all_dates.UniqueFeederCount>=1].merge(daily,on=['VisitDate','TransponderHexCode'],how='left')
d=d[(d.VisitDate>='2023-01-09')&(d.VisitDate<='2023-02-14')].copy()
d['TempL0']=d.Temp_stnd+1.2082479
# Published fixed-effect structure for offT: age-sex-specific intercepts and temperature slopes.
m=smf.glm('offT ~ 0 + C(Age_Sex) + C(Age_Sex):TempL0',data=d,family=__import__('statsmodels.api').api.families.Binomial()).fit()
d['fixed_p']=m.predict(d)
d['offT_resid']=d.offT-d.fixed_p
p=d.groupby('TransponderHexCode',as_index=False).agg(
    offT_rate=('offT','mean'), offT_resid_mean=('offT_resid','mean'), offT_days=('offT','size'), Age_Sex=('Age_Sex','first'))
p.to_csv(OUT/'spatial_propensity.csv',index=False)
summary={'bird_days':len(d),'birds':d.TransponderHexCode.nunique(),'two_core_birds':core.loc[core.PercentCoreFeeder<60,'TransponderHexCode'].tolist(),
         'fixed_effects':{k:float(v) for k,v in m.params.items()},'note':'No survival file read.'}
(OUT/'spatial_preoutcome_summary.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))

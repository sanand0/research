#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2.0", "pandas>=2.2", "statsmodels>=0.14"]
# ///
"""Post-outcome sanity check: can a Python GLMM approximation recover LaRocque's published off-territory survival signal?"""
from pathlib import Path
import json, re
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.genmod.bayes_mixed_glm import BinomialBayesMixedGLM

ROOT=Path(__file__).resolve().parents[1]
A=ROOT/'candidates/chickadees'
vis=pd.read_csv(A/'data_FeederVisits.csv')
all_dates=pd.read_csv(A/'data_AllDates.csv')
surv=pd.read_csv(A/'THC_Survival.csv')
feeders=['02A','04A','09A','10A','11A','12A','14A','16A']
counts=vis.groupby(['TransponderHexCode','Feeder']).size().unstack(fill_value=0).reindex(columns=feeders,fill_value=0)
core=[]
for bird,row in counts.iterrows():
    vals=row.to_numpy(); order=np.argsort(-vals,kind='stable'); top,top2=vals[order[0]],vals[order[1]]
    pct=100*top/(top+top2) if top+top2 else np.nan
    core.append((bird,'09A, 11A' if pct<60 else feeders[order[0]]))
core=pd.DataFrame(core,columns=['TransponderHexCode','CoreFeeder'])
v=vis.merge(core,on='TransponderHexCode')
v['onT']=[int(f in {x.strip() for x in str(c).split(',')}) for f,c in zip(v.Feeder,v.CoreFeeder)]
v['offT']=1-v.onT
daily=v.groupby(['VisitDate','TransponderHexCode','CoreFeeder'],as_index=False).agg(offT=('offT','max'))
d=all_dates[all_dates.UniqueFeederCount>=1].merge(daily,on=['VisitDate','TransponderHexCode'])
d=d[(d.VisitDate>='2023-01-09')&(d.VisitDate<='2023-02-14')].copy()
d['TempL0']=d.Temp_stnd+1.2082479
formula='offT ~ 0 + C(Age_Sex) + C(Age_Sex):TempL0'
vc={'bird':'0 + C(TransponderHexCode)','core':'0 + C(CoreFeeder)'}
model=BinomialBayesMixedGLM.from_formula(formula,vc,d)
fit=model.fit_vb(rng=20260908)
re=fit.random_effects()
bird=re.loc[re.index.str.startswith('C(TransponderHexCode)')].copy()
bird['TransponderHexCode']=bird.index.str.extract(r'\[(.*?)\]',expand=False)
bird[['TransponderHexCode','Mean','SD']].rename(columns={'Mean':'offT_re','SD':'offT_re_sd'}).to_csv(ROOT/'analysis/sourceA_offT_random_effects.csv',index=False)
x=bird[['TransponderHexCode','Mean']].rename(columns={'Mean':'offT_re'}).merge(surv,on='TransponderHexCode')
x['offT_z']=(x.offT_re-x.offT_re.mean())/x.offT_re.std(ddof=1)
g=smf.glm('Survived ~ offT_z',x,family=sm.families.Binomial()).fit()
term='offT_z'; lo,hi=g.conf_int().loc[term]
out={'n_birddays':len(d),'n_birds':d.TransponderHexCode.nunique(),'n_survival_join':len(x),
     'vb_variance_log_sd':{str(k):float(v) for k,v in zip(model.vcp_names,fit.vcp_mean)},
     'survival_beta':float(g.params[term]),'se':float(g.bse[term]),'p':float(g.pvalues[term]),
     'or':float(np.exp(g.params[term])),'or_ci95':[float(np.exp(lo)),float(np.exp(hi))],
     'published_reference':'LaRocque author code posterior-mode coefficient ~ -0.245, CrI -0.503 to -0.050'}
(ROOT/'analysis/sourceA_validation.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))

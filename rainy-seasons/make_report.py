import pandas as pd
from pathlib import Path
OUT=Path('data/out')
MIN_BASE=0.05
MAX_BASE=0.40
scores=pd.read_csv(OUT/'city_season_scores.csv')
nontriv=scores[(scores.base_wet_hour_rate>=MIN_BASE)&(scores.base_wet_hour_rate<=MAX_BASE)].copy()
cols=['city','country','population','season','base_wet_hour_rate','best_window','window_hours','inside_wet_hour_rate','outside_wet_hour_rate','risk_difference','risk_lift','wet_hour_coverage_in_window','umbrella_reliability_score','hourly_rain_entropy_0_1','season_wet_hours','season_hours']
top=nontriv.sort_values(['umbrella_reliability_score','risk_difference','wet_hour_coverage_in_window'],ascending=False).head(50)[cols]
bottom=nontriv.sort_values(['umbrella_reliability_score','risk_difference'],ascending=True).head(50)[cols+['hard_to_predict_score']]
hard=nontriv.sort_values(['hard_to_predict_score','hourly_rain_entropy_0_1'],ascending=False).head(50)[cols+['hard_to_predict_score']]
top.to_csv(OUT/'top_city_seasons_nontrivial_5pct.csv',index=False)
bottom.to_csv(OUT/'bottom_by_reliability_city_seasons_nontrivial_5pct.csv',index=False)
hard.to_csv(OUT/'hardest_city_seasons_nontrivial_5pct.csv',index=False)
city=nontriv.groupby(['city','country','country_code','population']).agg(
    seasons_analyzed=('season','count'),
    best_score=('umbrella_reliability_score','max'),
    median_score=('umbrella_reliability_score','median'),
    median_risk_difference=('risk_difference','median'),
    median_entropy=('hourly_rain_entropy_0_1','median'),
    median_base_rate=('base_wet_hour_rate','median'),
    useful_season_share=('risk_difference', lambda s: float((s>=0.05).mean())),
).reset_index()
best_idx=nontriv.groupby(['city','country','country_code','population'])['umbrella_reliability_score'].idxmax()
best_rows=nontriv.loc[best_idx,['city','country','country_code','population','season','best_window','window_hours','base_wet_hour_rate','inside_wet_hour_rate','outside_wet_hour_rate','risk_difference','risk_lift','wet_hour_coverage_in_window','umbrella_reliability_score']]
city=city.merge(best_rows,on=['city','country','country_code','population']).sort_values('best_score',ascending=False)
city.to_csv(OUT/'city_reliability_nontrivial_5pct.csv',index=False)

def fmt(df, n=10):
    show=df.head(n).copy()
    rename={
      'base_wet_hour_rate':'base', 'inside_wet_hour_rate':'inside', 'outside_wet_hour_rate':'outside',
      'risk_difference':'diff','risk_lift':'lift','wet_hour_coverage_in_window':'coverage',
      'umbrella_reliability_score':'score','hourly_rain_entropy_0_1':'entropy','hard_to_predict_score':'hard'
    }
    show=show.rename(columns=rename)
    for c in ['base','inside','outside','diff','coverage','useful_season_share','median_base_rate','median_risk_difference']:
        if c in show: show[c]=show[c].map(lambda x:f'{100*x:.1f}%')
    for c in ['score','best_score','median_score','entropy','hard']:
        if c in show: show[c]=show[c].map(lambda x:f'{x:.3f}')
    if 'lift' in show: show['lift']=show['lift'].map(lambda x:f'{x:.1f}x' if x<100 else '>100x')
    if 'population' in show: show['population']=show['population'].map(lambda x:f'{int(x):,}')
    return show.to_markdown(index=False)

report=[]
report.append('# Rainy seasons umbrella-window analysis')
report.append('')
report.append('Scope: 150 most-populated GeoNames populated places; hourly Open-Meteo historical precipitation; 2015-01-01 to 2024-12-31; wet hour = precipitation >= 0.2 mm/hour.')
report.append('')
report.append('Main score: best 1-6 hour local-time window for each city-season, scored as `(inside wet-hour risk - outside wet-hour risk) * sqrt(share of wet hours inside the window)`. Non-trivial seasons are base wet-hour rate 5%-40%.')
report.append('')
report.append('## Top 10 city-seasons')
report.append(fmt(top[['city','country','season','best_window','base_wet_hour_rate','inside_wet_hour_rate','outside_wet_hour_rate','risk_difference','risk_lift','wet_hour_coverage_in_window','umbrella_reliability_score']],10))
report.append('')
report.append('## Bottom 10 city-seasons by rule reliability')
report.append(fmt(bottom[['city','country','season','best_window','base_wet_hour_rate','inside_wet_hour_rate','outside_wet_hour_rate','risk_difference','risk_lift','wet_hour_coverage_in_window','umbrella_reliability_score','hard_to_predict_score']],10))
report.append('')
report.append('## Hardest 10 city-seasons: high hourly entropy + low best-rule separation')
report.append(fmt(hard[['city','country','season','best_window','base_wet_hour_rate','inside_wet_hour_rate','outside_wet_hour_rate','risk_difference','risk_lift','wet_hour_coverage_in_window','hourly_rain_entropy_0_1','hard_to_predict_score']],10))
report.append('')
report.append('## City-wise metric: top 30 cities by best non-trivial seasonal rule')
report.append(fmt(city[['city','country','population','season','best_window','base_wet_hour_rate','inside_wet_hour_rate','outside_wet_hour_rate','risk_difference','risk_lift','wet_hour_coverage_in_window','best_score','median_score','useful_season_share']].rename(columns={'best_score':'score'}),30))
(OUT/'report_nontrivial_5pct.md').write_text('\n'.join(report))
print((OUT/'report_nontrivial_5pct.md').read_text())

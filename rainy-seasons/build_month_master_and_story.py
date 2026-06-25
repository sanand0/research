import json, math, csv, shutil, textwrap, os
from pathlib import Path
import pandas as pd
import numpy as np

RAIN_BASE = Path('/home/vscode/code/research/rainy-seasons')
RAW = RAIN_BASE / 'data/raw'
OUT = RAIN_BASE / 'data/out'
STORY_RESEARCH = Path('/home/vscode/code/research/rainy-seasons/datastories/rainy-seasons')
STORY_SITE = Path('/home/vscode/code/datastories/rainy-seasons')
STORY_RESEARCH.mkdir(parents=True, exist_ok=True)
STORY_SITE.mkdir(parents=True, exist_ok=True)

START_DATE='2015-01-01'
END_DATE='2024-12-31'
WET_THRESHOLD=0.2

cities = pd.read_csv(OUT/'cities.csv')
# Keep a stable readable order: by best non-trivial seasonal score if available, else population.
city_rank_path = OUT/'city_reliability_nontrivial_5pct.csv'
if city_rank_path.exists():
    ranks = pd.read_csv(city_rank_path)[['city','country','best_score']]
    cities = cities.merge(ranks, on=['city','country'], how='left')
else:
    cities['best_score'] = np.nan
cities = cities.sort_values(['best_score','population'], ascending=[False, False]).reset_index(drop=True)

hour_defs=[]
for start_h in range(24):
    for length in range(1,7):
        hours=[(start_h+i)%24 for i in range(length)]
        end=(start_h+length)%24
        hour_defs.append((start_h,length,hours,f'{start_h:02d}:00-{end:02d}:00'))

records=[]
for idx, row in cities.iterrows():
    gid=str(row.geonameid)
    cache=RAW/f'openmeteo_{gid}_{START_DATE}_{END_DATE}.json'
    if not cache.exists():
        print('missing', row.city, cache)
        continue
    j=json.loads(cache.read_text())
    times=pd.to_datetime(j['hourly']['time'])
    precip=np.array(j['hourly']['precipitation'], dtype=float)
    precip=np.where(np.isnan(precip), 0, precip)
    wet=precip>=WET_THRESHOLD
    months=times.month.to_numpy()
    hours=times.hour.to_numpy()
    wet_counts=np.zeros((12,24), dtype=np.int64)
    total_counts=np.zeros((12,24), dtype=np.int64)
    precip_sum=np.zeros((12,24), dtype=float)
    for m in range(1,13):
        mm=months==m
        for h in range(24):
            mask=mm & (hours==h)
            total_counts[m-1,h]=int(mask.sum())
            wet_counts[m-1,h]=int(wet[mask].sum())
            precip_sum[m-1,h]=float(precip[mask].sum())
    for m in range(1,13):
        total_by_h=total_counts[m-1]
        wet_by_h=wet_counts[m-1]
        precip_by_h=precip_sum[m-1]
        total=int(total_by_h.sum())
        wet_total=int(wet_by_h.sum())
        base=wet_total/total if total else 0
        precip_total=float(precip_by_h.sum())
        best=None
        for start_h, hlen, hh, label in hour_defs:
            in_total=int(total_by_h[hh].sum())
            in_wet=int(wet_by_h[hh].sum())
            out_total=total-in_total
            out_wet=wet_total-in_wet
            if not in_total or not out_total:
                continue
            inside=in_wet/in_total
            outside=out_wet/out_total
            diff=inside-outside
            lift=inside/outside if outside>0 else (999 if inside>0 else 1)
            coverage=in_wet/wet_total if wet_total else 0
            score=diff*math.sqrt(max(coverage,0))
            rec=(score,diff,lift,coverage,inside,outside,start_h,hlen,label,in_wet,in_total,out_wet,out_total)
            if best is None or rec>best:
                best=rec
        score,diff,lift,coverage,inside,outside,start_h,hlen,label,in_wet,in_total,out_wet,out_total=best
        hourly_rates=np.divide(wet_by_h,total_by_h,out=np.zeros(24,dtype=float),where=total_by_h>0)
        hourly_precip=np.divide(precip_by_h,total_by_h,out=np.zeros(24,dtype=float),where=total_by_h>0)
        wet_dist=(wet_by_h/wet_total).tolist() if wet_total else [0]*24
        rec={
            'geonameid': gid,
            'city': row.city,
            'country': row.country,
            'country_code': row.country_code,
            'city_country': f'{row.city}, {row.country}',
            'population': int(row.population),
            'city_rank': idx+1,
            'lat': float(row.lat),
            'lon': float(row.lon),
            'month_num': m,
            'month': pd.Timestamp(2020,m,1).strftime('%b'),
            'month_name': pd.Timestamp(2020,m,1).strftime('%B'),
            'wet_threshold_mm_per_hour': WET_THRESHOLD,
            'total_hours': total,
            'wet_hours': wet_total,
            'rain_pct': base,
            'total_precip_mm': precip_total,
            'mean_precip_mm_per_hour': precip_total/total if total else 0,
            'best_window': label,
            'window_start_hour': start_h,
            'window_hours': hlen,
            'window_end_hour': (start_h+hlen)%24,
            'inside_wet_hour_rate': inside,
            'outside_wet_hour_rate': outside,
            'risk_difference': diff,
            'risk_lift': lift,
            'wet_hour_coverage_in_window': coverage,
            'umbrella_score': score,
            'window_wet_hours': in_wet,
            'window_total_hours': in_total,
            'outside_wet_hours': out_wet,
            'outside_total_hours': out_total,
            'hourly_rain_rates_json': json.dumps([round(float(x),4) for x in hourly_rates.tolist()], separators=(',',':')),
            'hourly_wet_distribution_json': json.dumps([round(float(x),4) for x in wet_dist], separators=(',',':')),
            'hourly_mean_precip_json': json.dumps([round(float(x),4) for x in hourly_precip.tolist()], separators=(',',':')),
        }
        for h in range(24):
            rec[f'h{h:02d}_rain_rate']=float(hourly_rates[h])
        records.append(rec)

master=pd.DataFrame(records)
master_path=OUT/'city_month_master.csv'
master.to_csv(master_path,index=False)
for folder in [STORY_RESEARCH, STORY_SITE]:
    master.to_csv(folder/'city_month_master.csv',index=False)
print('Wrote master rows', len(master), master_path)

# Prepare compact data for embedding: keep all 150x12 cells; round for size.
embed_cols=['geonameid','city','country','city_country','population','city_rank','month_num','month','rain_pct','umbrella_score','best_window','window_start_hour','window_hours','inside_wet_hour_rate','outside_wet_hour_rate','risk_difference','risk_lift','wet_hour_coverage_in_window','hourly_rain_rates_json']
small=master[embed_cols].copy()
for c in ['rain_pct','umbrella_score','inside_wet_hour_rate','outside_wet_hour_rate','risk_difference','risk_lift','wet_hour_coverage_in_window']:
    small[c]=small[c].astype(float).round(4)
# Convert JSON string to list.
data=[]
for r in small.to_dict(orient='records'):
    r['hours']=json.loads(r.pop('hourly_rain_rates_json'))
    data.append(r)
meta={
    'start_date': START_DATE,
    'end_date': END_DATE,
    'wet_threshold': WET_THRESHOLD,
    'city_count': int(master.geonameid.nunique()),
    'row_count': int(len(master)),
    'max_score': float(master.umbrella_score.max()),
    'max_rain_pct': float(master.rain_pct.max()),
    'generated': pd.Timestamp.now(tz='Asia/Singapore').strftime('%Y-%m-%d %H:%M %Z'),
}

story_title='When does the rain keep an appointment?'
story_description='A city-month atlas of whether umbrella weather follows a daily rhythm — or refuses to be put on a clock.'

html_template = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>When does the rain keep an appointment?</title>
<meta name="description" content="A city-month atlas of whether umbrella weather follows a daily rhythm.">
<style>
  :root {
    --ink: #171717;
    --muted: #666;
    --hair: #e7e1d8;
    --paper: #fbfaf7;
    --panel: #ffffff;
    --score-hi: #08306b;
    --score-lo: #f7fbff;
    --window: #ffbf47;
    --window-dark: #ad6500;
    --rain: #61758a;
    --shadow: 0 12px 40px rgba(30, 24, 18, .10);
  }
  * { box-sizing: border-box; }
  html { scroll-behavior: smooth; }
  body {
    margin: 0;
    background: var(--paper);
    color: var(--ink);
    font-family: ui-serif, Georgia, Cambria, "Times New Roman", Times, serif;
  }
  .hero {
    min-height: 76vh;
    display: grid;
    align-items: end;
    padding: clamp(2rem, 6vw, 6rem) clamp(1rem, 5vw, 5rem);
    background:
      radial-gradient(circle at 80% 10%, rgba(255,191,71,.22), transparent 28rem),
      linear-gradient(180deg, #fffaf0 0%, #fbfaf7 78%);
    border-bottom: 1px solid var(--hair);
  }
  .kicker { font: 700 .78rem/1.2 ui-sans-serif, system-ui, sans-serif; letter-spacing: .16em; text-transform: uppercase; color: #8a4b00; }
  h1 { max-width: 12ch; font-size: clamp(3.4rem, 9vw, 9.8rem); line-height: .88; letter-spacing: -.07em; margin: .5rem 0 1.3rem; }
  .dek { max-width: 52rem; font-size: clamp(1.25rem, 2.2vw, 2.25rem); line-height: 1.18; color: #2a2a2a; margin: 0; }
  .byline { margin-top: 2rem; color: var(--muted); font: 500 .95rem/1.5 ui-sans-serif, system-ui, sans-serif; }
  main { width: min(118rem, 100%); margin: 0 auto; }
  section { padding: clamp(2.2rem, 5vw, 5rem) clamp(1rem, 4vw, 4rem); }
  .narrative { width: min(48rem, 100%); margin: 0 auto; font-size: clamp(1.2rem, 1.65vw, 1.55rem); line-height: 1.52; }
  .narrative p { margin: 0 0 1.25em; }
  .narrative .drop:first-letter { float: left; font-size: 4.2em; line-height: .82; padding-right: .08em; font-weight: 700; color: #0b3b76; }
  .stat-row { display: grid; grid-template-columns: repeat(4, minmax(0,1fr)); gap: 1rem; margin: 2.5rem auto; width: min(70rem, 100%); }
  .stat { background: #fff; border: 1px solid var(--hair); box-shadow: var(--shadow); padding: 1.2rem; border-radius: 1.1rem; }
  .stat b { display: block; font: 800 clamp(1.8rem,4vw,3rem)/1 ui-sans-serif,system-ui,sans-serif; letter-spacing: -.04em; color: #0b3b76; }
  .stat span { display:block; margin-top:.45rem; color:var(--muted); font: 600 .85rem/1.35 ui-sans-serif,system-ui,sans-serif; }
  .grid-section { padding-left: clamp(.5rem, 2vw, 2rem); padding-right: clamp(.5rem, 2vw, 2rem); }
  .grid-intro { width: min(68rem, 100%); margin: 0 auto 1.2rem; display: grid; grid-template-columns: 1.5fr 1fr; gap: 1.5rem; align-items: end; }
  .grid-intro h2 { font-size: clamp(2rem, 4vw, 4.2rem); line-height: .95; letter-spacing: -.05em; margin: 0; }
  .grid-intro p { margin: 0; color: #4e4e4e; font-size: 1.05rem; line-height: 1.45; }
  .controls { width: min(118rem, 100%); margin: 0 auto .75rem; display:flex; gap:.75rem; flex-wrap:wrap; align-items:center; justify-content:space-between; font: 600 .85rem/1.2 ui-sans-serif,system-ui,sans-serif; }
  .controls label { color:#555; display:flex; align-items:center; gap:.45rem; }
  input, select { border:1px solid #d6cec3; border-radius:.8rem; padding:.6rem .75rem; background:#fff; font: inherit; color:#222; }
  input { min-width: min(18rem, 70vw); }
  .legend { display:flex; gap:.9rem; align-items:center; flex-wrap:wrap; color:#555; }
  .ramp { width: 11rem; height: .75rem; border-radius: 99px; background: linear-gradient(90deg,#f7fbff,#c9ddf0,#6baed6,#2171b5,#08306b); border:1px solid #d6dbe1; }
  .window-dot { width:1.2rem; height:.55rem; background:var(--window); display:inline-block; border-radius:99px; box-shadow: inset 0 0 0 1px rgba(0,0,0,.18); }
  .matrix-wrap { width: 100%; overflow: auto; border: 1px solid #d7d0c8; border-radius: 1rem; background: #fff; box-shadow: var(--shadow); max-height: 82vh; }
  .matrix { min-width: 1120px; display: grid; grid-template-columns: 210px repeat(12, minmax(74px, 1fr)); align-items: stretch; }
  .head, .row-label, .cell { border-bottom: 1px solid rgba(0,0,0,.10); border-right: 1px solid rgba(0,0,0,.08); }
  .head { position: sticky; top: 0; z-index: 4; background: #f5efe7; color:#38322c; min-height: 2.4rem; display:flex; align-items:center; justify-content:center; font: 800 .78rem/1 ui-sans-serif,system-ui,sans-serif; letter-spacing:.03em; text-transform:uppercase; }
  .corner { left: 0; z-index: 6; justify-content:flex-start; padding-left: .8rem; }
  .row-label { position: sticky; left: 0; z-index: 3; background: rgba(255,255,255,.94); min-height: 5.2rem; padding: .72rem .8rem; display:flex; flex-direction:column; justify-content:center; }
  .row-label strong { font: 800 .94rem/1.15 ui-sans-serif,system-ui,sans-serif; letter-spacing:-.01em; }
  .row-label span { color:#777; font: 600 .75rem/1.2 ui-sans-serif,system-ui,sans-serif; margin-top:.22rem; }
  .cell { min-height: 5.2rem; padding: .35rem .38rem .3rem; display:flex; flex-direction:column; justify-content:space-between; position:relative; overflow:hidden; isolation:isolate; }
  .cell::before { content:""; position:absolute; inset:0; background: var(--bg); z-index:-2; }
  .cell::after { content:""; position:absolute; inset:0; background: linear-gradient(180deg, rgba(255,255,255,.14), transparent 45%, rgba(0,0,0,.06)); z-index:-1; pointer-events:none; }
  .cell.low::after { background: linear-gradient(180deg, rgba(255,255,255,.25), transparent 60%); }
  .numbers { display:flex; align-items:flex-start; justify-content:space-between; gap:.2rem; color: var(--fg); text-shadow: var(--shadow-text); }
  .score { font: 900 .95rem/.95 ui-sans-serif,system-ui,sans-serif; letter-spacing:-.04em; }
  .rainpct { font: 800 .72rem/1 ui-sans-serif,system-ui,sans-serif; opacity:.9; }
  .sub { margin-top:.15rem; color: var(--fg); opacity:.82; font: 700 .56rem/1 ui-sans-serif,system-ui,sans-serif; letter-spacing:.01em; text-shadow: var(--shadow-text); white-space:nowrap; }
  .bars { height: 1.75rem; display:grid; grid-template-columns: repeat(24, 1fr); gap:1px; align-items:end; padding-top:.2rem; }
  .bar { min-width: 1px; border-radius:2px 2px 0 0; height: calc(var(--h) * 100%); background: var(--bar); opacity: var(--bar-opacity); box-shadow: 0 0 0 .2px rgba(0,0,0,.22); }
  .bar.in { background: var(--window); opacity: .96; box-shadow: 0 0 0 .25px rgba(70,38,0,.4); }
  .callout-grid { display:grid; grid-template-columns: repeat(3, minmax(0,1fr)); gap:1rem; margin:2rem auto 0; width:min(88rem,100%); }
  .callout { background:#fff; border:1px solid var(--hair); border-radius:1.2rem; box-shadow:var(--shadow); padding:1.25rem; }
  .callout h3 { margin:.1rem 0 .8rem; font: 900 1rem/1.1 ui-sans-serif,system-ui,sans-serif; letter-spacing:-.02em; }
  .callout p { margin:.5rem 0; color:#4a4a4a; font: 500 .95rem/1.4 ui-sans-serif,system-ui,sans-serif; }
  .callout b { color:#111; }
  .method { background:#111; color:#f4efe7; }
  .method .narrative { font-size:1.05rem; font-family: ui-sans-serif, system-ui, sans-serif; color:#ddd; }
  .method h2 { font: 900 clamp(1.8rem,4vw,3.5rem)/1 ui-sans-serif,system-ui,sans-serif; letter-spacing:-.05em; color:#fff; margin:0 0 1rem; }
  code { background: rgba(255,255,255,.1); padding:.1rem .25rem; border-radius:.25rem; }
  footer { padding: 2rem; color:#777; text-align:center; font: 600 .8rem/1.4 ui-sans-serif,system-ui,sans-serif; }
  @media (max-width: 820px) {
    .hero { min-height: 62vh; }
    .stat-row, .grid-intro, .callout-grid { grid-template-columns: 1fr; }
    .matrix { min-width: 1030px; grid-template-columns: 165px repeat(12, 72px); }
    .row-label { padding:.55rem; }
    .cell { min-height:4.8rem; }
    section { padding-left: 1rem; padding-right: 1rem; }
  }
</style>
</head>
<body>
<header class="hero">
  <div>
    <div class="kicker">A rain clock, if one exists</div>
    <h1>When does the rain keep an appointment?</h1>
    <p class="dek">We ask a deliberately human question of ten years of hourly weather: not “how much rain falls,” but whether a city has a reliable hour when an umbrella suddenly becomes a good idea.</p>
    <div class="byline">150 large cities · 12 months · 24 hours · umbrella rain = at least 0.2 mm in an hour</div>
  </div>
</header>
<main>
<section>
  <div class="narrative">
    <p class="drop">Rain is often described as a season. But the useful question is smaller. If you are leaving the house at noon, you do not ask whether July is wet. You ask whether the sky has a habit.</p>
    <p>So each city-month below is treated like a tiny detective story. We try every local-time window from one to six hours. The best window wins only if rain is much more likely inside it than outside it, and if that window captures a meaningful share of the month’s rainy hours.</p>
  </div>
  <div class="stat-row">
    <div class="stat"><b id="stat-cities">150</b><span>large cities analyzed</span></div>
    <div class="stat"><b id="stat-cells">1,800</b><span>city-month cells</span></div>
    <div class="stat"><b id="stat-years">10</b><span>years of hourly data</span></div>
    <div class="stat"><b id="stat-top">0.45</b><span>top umbrella-window score</span></div>
  </div>
</section>
<section class="grid-section" id="atlas">
  <div class="grid-intro">
    <h2>The atlas of punctual rain</h2>
    <p>Darker cells mean a stronger umbrella rule. The small number is the monthly wet-hour rate. The 24 tiny bars show rain risk by hour; amber bars mark the best umbrella window.</p>
  </div>
  <div class="controls">
    <div style="display:flex;gap:.75rem;flex-wrap:wrap;align-items:center">
      <label>Find city <input id="search" placeholder="Singapore, Tokyo, Lagos…"></label>
      <label>Sort <select id="sort"><option value="best">Best umbrella rule</option><option value="rain">Wettest month</option><option value="hard">Hardest to time</option><option value="name">City name</option></select></label>
    </div>
    <div class="legend"><span>Score</span><span class="ramp"></span><span><span class="window-dot"></span> best window</span><span>number = wet-hour %</span></div>
  </div>
  <div class="matrix-wrap" id="matrixWrap"><div class="matrix" id="matrix"></div></div>
  <div class="callout-grid" id="callouts"></div>
</section>
<section>
  <div class="narrative">
    <p>The most regular rains are not merely wet. They are <em>scheduled</em>. Caracas in August is almost theatrical: between noon and 6 p.m., more than half the hours are wet; outside that window, barely one in twenty is.</p>
    <p>The hardest places tell a different story. Tokyo outside summer, Incheon in the cool months, and parts of northern China do get umbrella weather. But the clock is little help. Rain does not gather into a daily appointment; it is spread thinly across the day.</p>
    <p>That is the point of the grid. The weather question people ask is local, seasonal, and behavioral. Averages answer the climate question. This table tries to answer the leaving-the-house question.</p>
  </div>
</section>
<section class="method">
  <div class="narrative">
    <h2>How the score works</h2>
    <p>For each city and month, I marked an hour as wet if precipitation was at least <code>0.2 mm/hour</code>. Then I tested every 1–6 hour local-time window. The score is:</p>
    <p><code>(wet-hour risk inside the window − wet-hour risk outside the window) × sqrt(share of wet hours inside the window)</code></p>
    <p>This penalizes two misleading cases: a window that is only slightly wetter than the rest of the day, and a window that looks intense but captures very little of the month’s rain.</p>
    <p>Data: Open-Meteo historical hourly precipitation, 2015–2024, using GeoNames city coordinates. The master CSV for this visualization is <code>city_month_master.csv</code>.</p>
  </div>
</section>
</main>
<footer>Built as a single-page data story. Cells use local city time.</footer>
<script id="rain-data" type="application/json">__DATA__</script>
<script>
const payload = JSON.parse(document.getElementById('rain-data').textContent);
const data = payload.data;
const meta = payload.meta;
const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
const maxScore = Math.max(...data.map(d => d.umbrella_score));
const maxRain = Math.max(...data.map(d => d.rain_pct));
const byCity = new Map();
for (const d of data) {
  if (!byCity.has(d.geonameid)) byCity.set(d.geonameid, {id:d.geonameid, city:d.city, country:d.country, population:d.population, rank:d.city_rank, cells:[], best:0, rain:0, hard:1});
  const c = byCity.get(d.geonameid);
  c.cells.push(d);
  c.best = Math.max(c.best, d.umbrella_score);
  c.rain = Math.max(c.rain, d.rain_pct);
}
for (const c of byCity.values()) {
  c.cells.sort((a,b)=>a.month_num-b.month_num);
  c.hard = c.best;
}
let cities = Array.from(byCity.values());
function lerp(a,b,t){ return Math.round(a+(b-a)*t); }
function color(score){
  const t = Math.pow(Math.max(0, Math.min(1, score / maxScore)), 0.55);
  const stops = [
    [247,251,255], [198,219,239], [107,174,214], [33,113,181], [8,48,107]
  ];
  const p = t * (stops.length - 1);
  const i = Math.min(stops.length - 2, Math.floor(p));
  const f = p - i;
  const c0 = stops[i], c1 = stops[i+1];
  return [lerp(c0[0],c1[0],f), lerp(c0[1],c1[1],f), lerp(c0[2],c1[2],f)];
}
function luminance(rgb){
  const [r,g,b] = rgb.map(v => { v/=255; return v<=.03928 ? v/12.92 : Math.pow((v+.055)/1.055,2.4); });
  return .2126*r + .7152*g + .0722*b;
}
function pct(x, digits=0){ return (x*100).toFixed(digits) + '%'; }
function inWindow(h, start, len){ return ((h - start + 24) % 24) < len; }
function render(){
  const q = document.getElementById('search').value.trim().toLowerCase();
  const sort = document.getElementById('sort').value;
  let rows = cities.filter(c => !q || (c.city + ' ' + c.country).toLowerCase().includes(q));
  rows.sort((a,b) => {
    if (sort === 'name') return (a.city + a.country).localeCompare(b.city + b.country);
    if (sort === 'rain') return b.rain - a.rain;
    if (sort === 'hard') return a.best - b.best;
    return b.best - a.best;
  });
  const matrix = document.getElementById('matrix');
  matrix.innerHTML = '';
  const corner = document.createElement('div'); corner.className='head corner'; corner.textContent='City'; matrix.appendChild(corner);
  for (const m of months) { const h=document.createElement('div'); h.className='head'; h.textContent=m; matrix.appendChild(h); }
  for (const city of rows) {
    const label = document.createElement('div');
    label.className='row-label';
    label.innerHTML = `<strong>${city.city}</strong><span>${city.country}</span>`;
    matrix.appendChild(label);
    for (const cell of city.cells) matrix.appendChild(cellNode(cell));
  }
}
function cellNode(d){
  const rgb = color(d.umbrella_score);
  const lum = luminance(rgb);
  const fg = lum < .38 ? '#fff' : '#17202a';
  const bar = lum < .38 ? 'rgba(255,255,255,.58)' : 'rgba(55,70,86,.36)';
  const div = document.createElement('div');
  div.className = 'cell' + (lum>.72 ? ' low' : '');
  div.style.setProperty('--bg', `rgb(${rgb[0]},${rgb[1]},${rgb[2]})`);
  div.style.setProperty('--fg', fg);
  div.style.setProperty('--bar', bar);
  div.style.setProperty('--bar-opacity', lum < .38 ? '.74' : '.82');
  div.style.setProperty('--shadow-text', lum < .38 ? '0 1px 1px rgba(0,0,0,.35)' : 'none');
  const maxH = Math.max(.001, ...d.hours);
  const bars = d.hours.map((v,h)=>`<span class="bar ${inWindow(h,d.window_start_hour,d.window_hours)?'in':''}" style="--h:${Math.max(.04, v/maxH).toFixed(3)}" title="${String(h).padStart(2,'0')}:00 ${pct(v,1)}"></span>`).join('');
  div.title = `${d.city}, ${d.country} · ${d.month}\nBest window: ${d.best_window}\nMonthly wet-hour rate: ${pct(d.rain_pct,1)}\nInside: ${pct(d.inside_wet_hour_rate,1)} · outside: ${pct(d.outside_wet_hour_rate,1)}\nScore: ${d.umbrella_score.toFixed(3)}`;
  div.innerHTML = `<div><div class="numbers"><span class="score">${d.umbrella_score.toFixed(2)}</span><span class="rainpct">${pct(d.rain_pct)}</span></div><div class="sub">${d.best_window}</div></div><div class="bars">${bars}</div>`;
  return div;
}
function renderCallouts(){
  const sorted=[...data].sort((a,b)=>b.umbrella_score-a.umbrella_score);
  const unique=[]; const seen=new Set();
  for (const d of sorted) { if (!seen.has(d.geonameid)) { unique.push(d); seen.add(d.geonameid); } if (unique.length>=3) break; }
  const hardest=[...cities].sort((a,b)=>a.best-b.best).slice(0,3);
  const box=document.getElementById('callouts');
  box.innerHTML = `
    <div class="callout"><h3>The clearest clock</h3><p><b>${unique[0].city}</b> in <b>${unique[0].month}</b>: ${pct(unique[0].inside_wet_hour_rate,1)} wet inside ${unique[0].best_window}, versus ${pct(unique[0].outside_wet_hour_rate,1)} outside.</p></div>
    <div class="callout"><h3>The familiar tropical signature</h3><p>The strongest rules cluster around late morning and afternoon. Convective rain often behaves like a recurring appointment, not just a season.</p></div>
    <div class="callout"><h3>The least clock-like cities</h3><p><b>${hardest.map(c=>c.city).join(', ')}</b> have weak best rules even in their wettest usable months. The umbrella question needs a forecast, not a clock.</p></div>`;
}
document.getElementById('search').addEventListener('input', render);
document.getElementById('sort').addEventListener('change', render);
document.getElementById('stat-cities').textContent = meta.city_count.toLocaleString();
document.getElementById('stat-cells').textContent = meta.row_count.toLocaleString();
document.getElementById('stat-top').textContent = meta.max_score.toFixed(2);
renderCallouts();
render();
</script>
</body>
</html>'''

payload={'meta':meta, 'data':data}
html=html_template.replace('__DATA__', json.dumps(payload, separators=(',',':')).replace('</','<\\/'))
for folder in [STORY_RESEARCH, STORY_SITE]:
    (folder/'index.html').write_text(html, encoding='utf-8')
    (folder/'README.md').write_text(textwrap.dedent(f'''\
    # {story_title}

    {story_description}

    Data: Open-Meteo hourly historical precipitation, {START_DATE} to {END_DATE}. City list: top {meta['city_count']} populated GeoNames places. A wet hour is precipitation >= {WET_THRESHOLD} mm/hour.

    Files:

    - `index.html` — single-page data story
    - `city_month_master.csv` — one row per city-month, with best umbrella window and 24 hourly rain-risk values
    '''), encoding='utf-8')
print('Wrote story to', STORY_RESEARCH, 'and', STORY_SITE)

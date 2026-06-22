#!/usr/bin/env python3
# /// script
# dependencies = ["pandas"]
# ///
from __future__ import annotations
from pathlib import Path
import json
import shutil
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
ANALYSIS=ROOT/'data'/'analysis'
PROCESSED=ROOT/'data'/'processed'
OUT=ANALYSIS/'rules_explorer.html'

def slim(df, cols, n=None):
    cols=[c for c in cols if c in df.columns]
    x=df[cols].fillna('').copy()
    if n: x=x.head(n)
    return x.to_dict(orient='records')

def main():
    changes=pd.read_csv(PROCESSED/'rule_changes.csv').fillna('')
    events=pd.read_csv(PROCESSED/'rule_events.csv').fillna('')
    pressure=pd.read_csv(ANALYSIS/'pressure_signals_ranked.csv').fillna('') if (ANALYSIS/'pressure_signals_ranked.csv').exists() else pd.DataFrame()
    kickoff=pd.read_csv(ANALYSIS/'kickoff_pbp_summary_by_season_type.csv').fillna('') if (ANALYSIS/'kickoff_pbp_summary_by_season_type.csv').exists() else pd.DataFrame()
    replay=pd.read_csv(ANALYSIS/'replay_authority_map.csv').fillna('') if (ANALYSIS/'replay_authority_map.csv').exists() else pd.DataFrame()
    funnel=pd.read_csv(ANALYSIS/'rule_funnel_summary.csv').fillna('') if (ANALYSIS/'rule_funnel_summary.csv').exists() else pd.DataFrame()
    # Copy selected assets next to HTML for portability.
    for asset in ['kickoff_return_touchback_rates.png','kickoff_adjusted_return_rate_by_score_bucket.png','replay_authority_map.png']:
        p=ANALYSIS/asset
        if p.exists() and p.resolve() != (ANALYSIS/asset).resolve(): shutil.copy2(p, ANALYSIS/asset)
    data={
        'changes': slim(changes, ['canonical_change_id','title','lineage','sublineage','first_year','last_year','status_lifecycle','target_metrics','event_count','approved_event_count','proposed_event_count','historical_event_count','best_source_quality_score','source_quality_tiers','analysis_include_default','source_keys','representative_summary']),
        'events': slim(events, ['year','status','item_type','proposal_number','proposer','canonical_change_id','auto_lineage','auto_sublineage','source_quality_tier','source_quality_score','analysis_include_default','summary','source_key','source_url'], 800),
        'pressure': slim(pressure, ['canonical_change_id','lineage','sublineage','first_year','signal_score','signal_reasons','recommended_tracking_metric','title_or_summary','event_summaries']),
        'kickoff': slim(kickoff, ['season','season_type','kickoffs','return_rate','touchback_rate','fair_catch_rate','onside_attempt_rate','avg_start_yardline_own','penalty_rate']),
        'replay': slim(replay, ['stage_order','stage_label','event_count','first_year','last_year','who_initiates','who_decides','review_objects']),
        'funnel': slim(funnel, list(funnel.columns)),
    }
    js=json.dumps(data, ensure_ascii=False).replace('</','<\\/')
    html_doc=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>NFL Rules Explorer</title>
<style>
:root{{--bg:#0b1020;--panel:#121a2f;--muted:#98a2b3;--text:#e7edf7;--accent:#8fb7ff;--line:#24304d;--good:#84e1bc;--warn:#ffd37a}}
body{{margin:0;font:14px/1.45 system-ui,-apple-system,Segoe UI,sans-serif;background:var(--bg);color:var(--text)}}header{{padding:28px 34px 14px;border-bottom:1px solid var(--line);background:linear-gradient(180deg,#101832,#0b1020)}}h1{{margin:0 0 8px;font-size:28px}}h2{{margin:0 0 12px}}.subtitle{{color:var(--muted);max-width:980px}}main{{padding:22px 34px 50px;display:grid;gap:20px}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:14px}}.card{{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:16px;box-shadow:0 10px 30px rgba(0,0,0,.18)}}.metric{{font-size:28px;font-weight:700}}.label{{color:var(--muted);font-size:12px;text-transform:uppercase;letter-spacing:.08em}}.controls{{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin-bottom:10px}}select,input,button{{background:#0d1428;color:var(--text);border:1px solid var(--line);border-radius:8px;padding:8px 10px}}button{{cursor:pointer}}table{{width:100%;border-collapse:collapse;font-size:13px}}th,td{{border-bottom:1px solid var(--line);padding:8px;text-align:left;vertical-align:top}}th{{color:#b8c7e6;position:sticky;top:0;background:var(--panel)}}.small{{color:var(--muted);font-size:12px}}a{{color:var(--accent)}}.badge{{display:inline-block;padding:2px 7px;border:1px solid var(--line);border-radius:999px;color:#c8d7f5;margin:1px}}.quality{{color:var(--good)}}.seed{{color:var(--warn)}}img{{max-width:100%;border:1px solid var(--line);border-radius:10px;background:#fff}}.timeline{{display:grid;grid-template-columns:70px 1fr;gap:7px;align-items:center}}.bar{{height:10px;background:#273451;border-radius:999px;overflow:hidden}}.bar span{{display:block;height:100%;background:var(--accent)}}
</style></head><body><header><h1>NFL Rules Explorer</h1><div class="subtitle">Static explorer generated from extracted NFL rule-change events, canonical changes, source quality, pressure signals, kickoff metrics, and replay authority maps. No backend; data is embedded in this HTML.</div></header><main>
<section class="grid" id="metrics"></section>
<section class="card"><h2>Timeline by year</h2><div id="timeline"></div></section>
<section class="card"><h2>Canonical rule changes</h2><div class="controls"><label>Lineage <select id="lineage"></select></label><label>Quality <select id="quality"><option value="all">All</option><option value="default">Default analysis only</option><option value="seed">Seed / historical only</option></select></label><label>Search <input id="search" placeholder="kickoff, replay, overtime…"></label><button id="exportChanges">Export filtered CSV</button></div><div class="small" id="changeCount"></div><div style="overflow:auto;max-height:620px"><table id="changes"></table></div></section>
<section class="grid"><div class="card"><h2>Pressure signals</h2><div id="pressure"></div></div><div class="card"><h2>Kickoff metrics</h2><div id="kickoff"></div><img src="kickoff_return_touchback_rates.png" alt="Kickoff return and touchback rates"></div></section>
<section class="grid"><div class="card"><h2>Replay authority map</h2><div id="replay"></div></div><div class="card"><h2>Replay map image</h2><img src="replay_authority_map.png" alt="Replay authority map"></div></section>
<section class="card"><h2>Recent source events</h2><div style="overflow:auto;max-height:520px"><table id="events"></table></div></section>
</main><script>const DATA={js};
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[c]));
let filteredChanges=[];function table(el,rows,cols,linkSource=false){{if(!rows.length){{el.innerHTML='<p class="small">No rows.</p>';return;}}el.innerHTML='<thead><tr>'+cols.map(c=>`<th>${{esc(c)}}</th>`).join('')+'</tr></thead><tbody>'+rows.map(r=>'<tr>'+cols.map(c=>{{let v=r[c];if(linkSource&&c==='source_url'&&v)return `<td><a href="${{esc(v)}}">source</a></td>`;return `<td>${{esc(v)}}</td>`}}).join('')+'</tr>').join('')+'</tbody>';}}
function pct(x){{const n=Number(x);return Number.isFinite(n)?(n*100).toFixed(1)+'%':esc(x)}}function csv(rows){{if(!rows.length)return '';const cols=Object.keys(rows[0]);return cols.join(',')+'\n'+rows.map(r=>cols.map(c=>'"'+String(r[c]??'').replaceAll('"','""')+'"').join(',')).join('\n')}}
function initMetrics(){{const f=DATA.funnel[0]||{{}};const defaultEvents=DATA.events.filter(d=>String(d.analysis_include_default)==='True'||d.analysis_include_default===true).length;const m=[['Events',DATA.events.length],['Default-quality events',defaultEvents],['Canonical changes',DATA.changes.length],['Pressure signals',DATA.pressure.length],['Proposed→approved',`${{f.proposed_and_approved||''}} / ${{f.proposed_canonical_changes||''}}`]];document.getElementById('metrics').innerHTML=m.map(([k,v])=>`<div class="card"><div class="label">${{esc(k)}}</div><div class="metric">${{esc(v)}}</div></div>`).join('')}}
function initTimeline(){{const by={{}};DATA.events.forEach(r=>{{const y=r.year||'unknown';by[y]=(by[y]||0)+1}});const max=Math.max(...Object.values(by));document.getElementById('timeline').innerHTML='<div class="timeline">'+Object.entries(by).sort((a,b)=>Number(a[0])-Number(b[0])).map(([y,n])=>`<div>${{esc(y)}}</div><div><div class="bar"><span style="width:${{100*n/max}}%"></span></div><span class="small">${{n}}</span></div>`).join('')+'</div>'}}
function initChanges(){{const lineages=['All',...Array.from(new Set(DATA.changes.map(d=>d.lineage))).sort()];const sel=document.getElementById('lineage');sel.innerHTML=lineages.map(x=>`<option>${{esc(x)}}</option>`).join('');const search=document.getElementById('search'), quality=document.getElementById('quality');function render(){{const q=search.value.toLowerCase(),lin=sel.value,qual=quality.value;filteredChanges=DATA.changes.filter(r=>{{const include=String(r.analysis_include_default)==='True'||r.analysis_include_default===true;const seed=String(r.source_quality_tiers||'').includes('seed');return (lin==='All'||r.lineage===lin)&&(qual==='all'||(qual==='default'&&include)||(qual==='seed'&&seed))&&JSON.stringify(r).toLowerCase().includes(q)}});document.getElementById('changeCount').textContent=`${{filteredChanges.length}} changes`;table(document.getElementById('changes'),filteredChanges,['first_year','last_year','lineage','sublineage','best_source_quality_score','status_lifecycle','event_count','title','representative_summary'])}}sel.onchange=render;search.oninput=render;quality.onchange=render;render();document.getElementById('exportChanges').onclick=()=>{{const blob=new Blob([csv(filteredChanges)],{{type:'text/csv'}});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='filtered_rule_changes.csv';a.click();}}}}
function initPressure(){{document.getElementById('pressure').innerHTML=DATA.pressure.map(r=>`<p><b>${{esc(r.signal_score)}}</b> <span class="badge">${{esc(r.lineage)}}</span> ${{esc(r.title_or_summary||r.canonical_change_id)}}<br><span class="small">${{esc(r.recommended_tracking_metric)}}<br>${{esc(r.signal_reasons)}}</span></p>`).join('')}}
function initKickoff(){{const rows=DATA.kickoff.filter(r=>String(r.season_type)==='REG');document.getElementById('kickoff').innerHTML='<table><thead><tr><th>Season</th><th>Return</th><th>Touchback</th><th>Start</th><th>Penalty</th></tr></thead><tbody>'+rows.map(r=>`<tr><td>${{r.season}}</td><td>${{pct(r.return_rate)}}</td><td>${{pct(r.touchback_rate)}}</td><td>${{esc(r.avg_start_yardline_own)}}</td><td>${{pct(r.penalty_rate)}}</td></tr>`).join('')+'</tbody></table>'}}
function initReplay(){{document.getElementById('replay').innerHTML=DATA.replay.map(r=>`<p><span class="badge">${{esc(r.stage_order)}}</span> <b>${{esc(r.stage_label)}}</b> — ${{esc(r.event_count)}} events, ${{esc(r.first_year)}}–${{esc(r.last_year)}}<br><span class="small">Initiates: ${{esc(r.who_initiates)}}<br>Decides: ${{esc(r.who_decides)}}<br>Objects: ${{esc(r.review_objects)}}</span></p>`).join('')}}
function initEvents(){{const rows=DATA.events.filter(r=>Number(r.year)>=2023).slice(0,220);table(document.getElementById('events'),rows,['year','status','item_type','proposal_number','proposer','auto_lineage','auto_sublineage','source_quality_tier','source_quality_score','summary','source_url'],true)}}
initMetrics();initTimeline();initChanges();initPressure();initKickoff();initReplay();initEvents();
</script></body></html>'''
    OUT.write_text(html_doc)
    print(OUT)

if __name__=='__main__': main()

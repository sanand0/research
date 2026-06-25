#!/usr/bin/env python3
import csv, io, json, math, os, sys, time, zipfile, textwrap
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.parse import urlencode
from urllib.error import HTTPError, URLError
from collections import defaultdict

import duckdb
import pandas as pd
import numpy as np
import requests
from tqdm import tqdm

BASE = Path('.').resolve()
DATA = BASE / 'data'
RAW = DATA / 'raw'
OUT = DATA / 'out'
RAW.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)

START_DATE = '2015-01-01'
END_DATE = '2024-12-31'
WET_THRESHOLD_MM = 0.2
TOP_N_CITIES = int(os.environ.get('TOP_N_CITIES', '150'))
MIN_BASE_RATE = float(os.environ.get('MIN_BASE_RATE', '0.02'))
MAX_BASE_RATE = float(os.environ.get('MAX_BASE_RATE', '0.40'))

# City list from GeoNames.
def download(url, path):
    if path.exists() and path.stat().st_size > 0:
        return
    print(f'Downloading {url} -> {path}', flush=True)
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    path.write_bytes(r.content)

cities_zip = RAW / 'cities15000.zip'
country_txt = RAW / 'countryInfo.txt'
download('https://download.geonames.org/export/dump/cities15000.zip', cities_zip)
download('https://download.geonames.org/export/dump/countryInfo.txt', country_txt)

country = {}
with country_txt.open(encoding='utf-8') as f:
    for line in f:
        if not line.strip() or line.startswith('#'):
            continue
        row = line.rstrip('\n').split('\t')
        if len(row) >= 5:
            country[row[0]] = row[4]

cols = ['geonameid','name','asciiname','alternatenames','latitude','longitude','feature_class','feature_code','country_code','cc2','admin1','admin2','admin3','admin4','population','elevation','dem','timezone','modification_date']
rows = []
with zipfile.ZipFile(cities_zip) as z:
    with z.open('cities15000.txt') as f:
        text = io.TextIOWrapper(f, encoding='utf-8')
        reader = csv.reader(text, delimiter='\t')
        for r in reader:
            d = dict(zip(cols, r))
            try:
                pop = int(d['population'] or 0)
                lat = float(d['latitude']); lon = float(d['longitude'])
            except Exception:
                continue
            # Keep populated places. Do not require PPL exactly because PPLA/PPLC are useful.
            if d['feature_class'] != 'P' or pop <= 0:
                continue
            rows.append({
                'geonameid': d['geonameid'],
                'city': d['asciiname'] or d['name'],
                'country_code': d['country_code'],
                'country': country.get(d['country_code'], d['country_code']),
                'lat': lat,
                'lon': lon,
                'population': pop,
                'timezone': d['timezone'],
                'feature_code': d['feature_code'],
            })

cities = pd.DataFrame(rows).sort_values('population', ascending=False).drop_duplicates(['city','country_code']).head(TOP_N_CITIES).reset_index(drop=True)
cities.to_csv(OUT / 'cities.csv', index=False)
print(f'Using {len(cities)} cities. Population range {cities.population.min():,} - {cities.population.max():,}', flush=True)

# Precompute season masks and hour interval masks.
season_defs = []
for start_m in range(1, 13):
    for length in range(1, 12):
        months = [((start_m - 1 + i) % 12) + 1 for i in range(length)]
        # Canonical label
        if length == 1:
            label = pd.Timestamp(2020, start_m, 1).strftime('%b')
        elif length == 11:
            missing = sorted(set(range(1,13)) - set(months))[0]
            label = f'All except {pd.Timestamp(2020, missing, 1).strftime("%b")}'
        else:
            end_m = months[-1]
            label = f'{pd.Timestamp(2020, start_m, 1).strftime("%b")}-{pd.Timestamp(2020, end_m, 1).strftime("%b")}'
        season_defs.append((start_m, length, months, label))

hour_defs = []
for start_h in range(24):
    for length in range(1, 7):
        hours = [((start_h + i) % 24) for i in range(length)]
        end_h = (start_h + length) % 24
        label = f'{start_h:02d}:00-{end_h:02d}:00'
        hour_defs.append((start_h, length, hours, label))

# Helper score. Best window score favors useful separation, not merely accuracy on imbalanced data.
def compute_for_city(cityrow, session):
    city_id = str(cityrow.geonameid)
    cache = RAW / f'openmeteo_{city_id}_{START_DATE}_{END_DATE}.json'
    if not cache.exists() or cache.stat().st_size < 1000:
        params = {
            'latitude': f'{cityrow.lat:.5f}',
            'longitude': f'{cityrow.lon:.5f}',
            'start_date': START_DATE,
            'end_date': END_DATE,
            'hourly': 'precipitation',
            'timezone': 'auto',
        }
        url = 'https://archive-api.open-meteo.com/v1/archive?' + urlencode(params)
        for attempt in range(5):
            try:
                r = session.get(url, timeout=90)
                if r.status_code == 429 or r.status_code >= 500:
                    time.sleep(2 + attempt * 3)
                    continue
                r.raise_for_status()
                cache.write_bytes(r.content)
                time.sleep(0.15)
                break
            except Exception as e:
                if attempt == 4:
                    raise
                time.sleep(2 + attempt * 3)
    j = json.loads(cache.read_text())
    times = pd.to_datetime(j['hourly']['time'])
    precip = np.array(j['hourly']['precipitation'], dtype=float)
    wet = np.where(np.isnan(precip), False, precip >= WET_THRESHOLD_MM)
    months = times.month.to_numpy()
    hours = times.hour.to_numpy()
    total_n = len(wet)
    if total_n < 80000:
        print(f'Warning: short data for {cityrow.city}: {total_n}', file=sys.stderr)
    out = []
    # Hour counts by month: 12 x 24, wet counts and total counts.
    wet_counts = np.zeros((12,24), dtype=np.int64)
    total_counts = np.zeros((12,24), dtype=np.int64)
    for m in range(1, 13):
        m_mask = months == m
        if not m_mask.any(): continue
        for h in range(24):
            mask = m_mask & (hours == h)
            total_counts[m-1,h] = mask.sum()
            wet_counts[m-1,h] = wet[mask].sum()
    for start_m, slen, smonths, slabel in season_defs:
        idx = np.array([m-1 for m in smonths])
        s_total_by_hour = total_counts[idx,:].sum(axis=0)
        s_wet_by_hour = wet_counts[idx,:].sum(axis=0)
        season_total = int(s_total_by_hour.sum())
        season_wet = int(s_wet_by_hour.sum())
        if season_total == 0: continue
        base = season_wet / season_total
        # We retain all records, but rank useful windows separately with base-rate filters.
        # Hard-to-predict should include non-trivial seasons; trivial seasons are easy for a different reason.
        best = None
        for start_h, hlen, hh, hlabel in hour_defs:
            in_total = int(s_total_by_hour[hh].sum())
            in_wet = int(s_wet_by_hour[hh].sum())
            out_total = season_total - in_total
            out_wet = season_wet - in_wet
            if in_total <= 0 or out_total <= 0: continue
            inside = in_wet / in_total
            outside = out_wet / out_total
            diff = inside - outside
            lift = inside / outside if outside > 0 else (999 if inside > 0 else 1)
            coverage = in_wet / season_wet if season_wet > 0 else 0
            # Balanced usefulness: separation weighted by event coverage and not too-wide windows.
            # Since hlen <= 6, width penalty mild; 6h is allowed when genuinely better.
            score = diff * math.sqrt(max(coverage, 0))
            # Mutual information between wet/no-wet and inside/outside in nats.
            p_in = in_total / season_total
            p_w = base
            cells = [
                (in_wet, in_total, p_in, p_w),
                (in_total-in_wet, in_total, p_in, 1-p_w),
                (out_wet, out_total, 1-p_in, p_w),
                (out_total-out_wet, out_total, 1-p_in, 1-p_w),
            ]
            mi = 0.0
            for count, denom_side, p_side, p_evt in cells:
                if count <= 0: continue
                pxy = count / season_total
                mi += pxy * math.log(pxy / (p_side * p_evt))
            rec = (score, diff, lift, coverage, inside, outside, start_h, hlen, hlabel, mi, in_wet, in_total, out_wet, out_total)
            if best is None or rec > best:
                best = rec
        # Flatness: std of hourly wet rates, weighted not necessary; lower = harder by time of day
        hourly_rate = np.divide(s_wet_by_hour, s_total_by_hour, out=np.zeros_like(s_wet_by_hour, dtype=float), where=s_total_by_hour>0)
        entropy = 0.0
        if season_wet > 0:
            p_hour_given_wet = s_wet_by_hour / season_wet
            entropy = -float(np.sum([p*math.log(p) for p in p_hour_given_wet if p > 0])) / math.log(24)
        if best:
            score, diff, lift, coverage, inside, outside, start_h, hlen, hlabel, mi, in_wet, in_total, out_wet, out_total = best
            # hard score: low useful separation in non-trivial seasons, plus high entropy. Higher means harder.
            hard_score = (1 - min(max(diff / 0.20, 0), 1)) * 0.65 + entropy * 0.35
            out.append({
                'geonameid': cityrow.geonameid,
                'city': cityrow.city,
                'country': cityrow.country,
                'country_code': cityrow.country_code,
                'population': int(cityrow.population),
                'lat': cityrow.lat, 'lon': cityrow.lon,
                'season': slabel,
                'season_start_month': start_m,
                'season_months': slen,
                'wet_threshold_mm_per_hour': WET_THRESHOLD_MM,
                'base_wet_hour_rate': base,
                'best_window': hlabel,
                'window_start_hour': start_h,
                'window_hours': hlen,
                'inside_wet_hour_rate': inside,
                'outside_wet_hour_rate': outside,
                'risk_difference': diff,
                'risk_lift': lift,
                'wet_hour_coverage_in_window': coverage,
                'mutual_information_nats': mi,
                'umbrella_reliability_score': score,
                'hourly_rain_entropy_0_1': entropy,
                'hard_to_predict_score': hard_score,
                'season_hours': season_total,
                'season_wet_hours': season_wet,
                'window_wet_hours': in_wet,
            })
    return out

all_records = []
errors = []
session = requests.Session()
session.headers.update({'User-Agent': 'rain-window-research/0.1 (personal analysis)'})
for _, row in tqdm(cities.iterrows(), total=len(cities), desc='cities'):
    try:
        recs = compute_for_city(row, session)
        all_records.extend(recs)
        if len(all_records) % (132*25) == 0:
            pd.DataFrame(all_records).to_parquet(OUT / 'city_season_scores.partial.parquet', index=False)
    except Exception as e:
        errors.append({'city': row.city, 'country': row.country, 'error': repr(e)})
        print('ERROR', row.city, row.country, repr(e), file=sys.stderr, flush=True)

scores = pd.DataFrame(all_records)
scores.to_parquet(OUT / 'city_season_scores.parquet', index=False)
scores.to_csv(OUT / 'city_season_scores.csv', index=False)
pd.DataFrame(errors).to_csv(OUT / 'errors.csv', index=False)

# Non-trivial seasons filter for main top/bottom.
nontriv = scores[(scores.base_wet_hour_rate >= MIN_BASE_RATE) & (scores.base_wet_hour_rate <= MAX_BASE_RATE)].copy()
# Top city-seasons: useful window
cols = ['city','country','population','season','base_wet_hour_rate','best_window','window_hours','inside_wet_hour_rate','outside_wet_hour_rate','risk_difference','risk_lift','wet_hour_coverage_in_window','umbrella_reliability_score','hourly_rain_entropy_0_1','season_wet_hours','season_hours']
top = nontriv.sort_values(['umbrella_reliability_score','risk_difference','wet_hour_coverage_in_window'], ascending=False).head(50)[cols]
bottom = nontriv.sort_values(['umbrella_reliability_score','risk_difference'], ascending=True).head(50)[cols + ['hard_to_predict_score']]
# More meaningful hard: avoid low-base near 2%? also rank hard score desc with entropy high and diff low, but nontrivial.
hard = nontriv.sort_values(['hard_to_predict_score','hourly_rain_entropy_0_1'], ascending=False).head(50)[cols + ['hard_to_predict_score']]

top.to_csv(OUT / 'top_city_seasons.csv', index=False)
bottom.to_csv(OUT / 'bottom_by_reliability_city_seasons.csv', index=False)
hard.to_csv(OUT / 'hardest_city_seasons.csv', index=False)

# City-level: best nontrivial season, median predictability, and share of useful seasons.
city = nontriv.groupby(['city','country','country_code','population']).agg(
    seasons_analyzed=('season','count'),
    best_score=('umbrella_reliability_score','max'),
    median_score=('umbrella_reliability_score','median'),
    median_risk_difference=('risk_difference','median'),
    median_entropy=('hourly_rain_entropy_0_1','median'),
    median_base_rate=('base_wet_hour_rate','median'),
    useful_season_share=('risk_difference', lambda s: float((s >= 0.05).mean())),
).reset_index()
best_idx = nontriv.groupby(['city','country','country_code','population'])['umbrella_reliability_score'].idxmax()
best_rows = nontriv.loc[best_idx, ['city','country','country_code','population','season','best_window','window_hours','base_wet_hour_rate','inside_wet_hour_rate','outside_wet_hour_rate','risk_difference','risk_lift','wet_hour_coverage_in_window','umbrella_reliability_score']]
city = city.merge(best_rows, on=['city','country','country_code','population'], suffixes=('', '_best'))
city = city.sort_values('best_score', ascending=False)
city.to_csv(OUT / 'city_reliability.csv', index=False)

# Save a concise markdown report tables.
def pct(x): return f'{x*100:.1f}%'
def fmt_table(df, n=10):
    show = df.head(n).copy()
    for c in ['base_wet_hour_rate','inside_wet_hour_rate','outside_wet_hour_rate','risk_difference','wet_hour_coverage_in_window','umbrella_reliability_score','hourly_rain_entropy_0_1','hard_to_predict_score']:
        if c in show:
            if c in ['umbrella_reliability_score','hourly_rain_entropy_0_1','hard_to_predict_score']:
                show[c] = show[c].map(lambda x: f'{x:.3f}')
            else:
                show[c] = show[c].map(pct)
    if 'risk_lift' in show:
        show['risk_lift'] = show['risk_lift'].map(lambda x: f'{x:.1f}x' if x < 100 else '>100x')
    if 'population' in show:
        show['population'] = show['population'].map(lambda x: f'{int(x):,}')
    return show.to_markdown(index=False)

report = []
report.append(f'# Rainy seasons umbrella-window analysis\n')
report.append(f'- Data: Open-Meteo Historical Weather API hourly precipitation, {START_DATE} to {END_DATE}.')
report.append(f'- Cities: top {len(cities)} populated GeoNames `cities15000` populated places.')
report.append(f'- Wet hour threshold: precipitation >= {WET_THRESHOLD_MM} mm/hour.')
report.append(f'- Seasons: all contiguous local calendar month windows from 1 to 11 months, wrapping around year-end.')
report.append(f'- Candidate umbrella windows: every local-time interval of 1 to 6 hours, wrapping around midnight.')
report.append(f'- Non-trivial city-seasons: base wet-hour rate between {MIN_BASE_RATE:.0%} and {MAX_BASE_RATE:.0%}.')
report.append('\n## Top 10 city-seasons by umbrella-window reliability\n')
report.append(fmt_table(top[['city','country','season','best_window','base_wet_hour_rate','inside_wet_hour_rate','outside_wet_hour_rate','risk_difference','risk_lift','wet_hour_coverage_in_window','umbrella_reliability_score']], 10))
report.append('\n## Bottom 10 city-seasons by umbrella-window reliability\n')
report.append(fmt_table(bottom[['city','country','season','best_window','base_wet_hour_rate','inside_wet_hour_rate','outside_wet_hour_rate','risk_difference','risk_lift','wet_hour_coverage_in_window','umbrella_reliability_score','hard_to_predict_score']], 10))
report.append('\n## Hardest 10 non-trivial city-seasons by high entropy + low separation\n')
report.append(fmt_table(hard[['city','country','season','best_window','base_wet_hour_rate','inside_wet_hour_rate','outside_wet_hour_rate','risk_difference','risk_lift','wet_hour_coverage_in_window','hourly_rain_entropy_0_1','hard_to_predict_score']], 10))
report.append('\n## Top 25 cities by best seasonal umbrella rule\n')
report.append(fmt_table(city[['city','country','population','season','best_window','base_wet_hour_rate','inside_wet_hour_rate','outside_wet_hour_rate','risk_difference','risk_lift','wet_hour_coverage_in_window','best_score','median_score','useful_season_share']].rename(columns={'best_score':'umbrella_reliability_score'}), 25))

(OUT / 'report.md').write_text('\n'.join(report), encoding='utf-8')
print('\n'.join(report[:14]))
print('\nWrote outputs to', OUT, flush=True)

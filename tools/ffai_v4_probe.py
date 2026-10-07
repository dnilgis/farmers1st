#!/usr/bin/env python3
"""
FFAI v4 data probe. Finds out what national data exists before v4 is built.
Publishes nothing. Run by the "probe" mode of .github/workflows/ffai-update.yml.

1. USDA NASS Quick Stats (needs secret NASS_API_KEY):
   every NATIONAL "INDEX FOR PRICE RECEIVED" / "INDEX FOR PRICE PAID" series,
   with frequency, first and last period, and the full data saved to CSV.
2. FRED (needs FRED_API_KEY): searches for national farm income, farm
   bankruptcy, farmland value and farm debt series; lists id, title,
   frequency, start, end.

Output: engine/v4probe/ (artifact) and the run summary.
"""
import json, os, sys, time, urllib.parse, urllib.request
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'engine', 'v4probe')
NASS = 'https://quickstats.nass.usda.gov/api/'
MONTHS = {m: i + 1 for i, m in enumerate(['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'])}
FRED_SEARCHES = ['net farm income', 'farm income United States', 'farm sector income', 'farm bankruptcy',
                 'chapter 12 bankruptcy', 'farm real estate value', 'farm sector debt', 'agricultural loans delinquency',
                 'prices received by farmers', 'prices paid by farmers']


def http_json(url, timeout=90, tries=3):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'farmers1st.com FFAI research'})
            return json.loads(urllib.request.urlopen(req, timeout=timeout).read().decode('utf-8'))
        except Exception as e:
            last = e
            time.sleep(3 * (i + 1))
    raise last


def nass(endpoint, key, **params):
    q = urllib.parse.urlencode({'key': key, 'format': 'JSON', **params})
    return http_json(f'{NASS}{endpoint}/?{q}')


def probe_nass(key, md, log):
    md += ['', '### USDA NASS national price indexes', '']
    if not key:
        md.append('NASS_API_KEY is not set. Add it as a repository secret and run probe again.')
        return
    found = []
    for group in ('PRICES RECEIVED', 'PRICES PAID'):
        try:
            vals = nass('get_param_values', key, param='short_desc', group_desc=group, agg_level_desc='NATIONAL')
            names = [s for s in vals.get('short_desc', []) if 'INDEX' in s.upper()]
            log.append(f'NASS {group}: {len(vals.get("short_desc", []))} national series, {len(names)} are indexes')
            found += [(group, n) for n in names]
        except Exception as e:
            log.append(f'NASS {group}: list failed: {e}')
    rows, frames = [], []
    for group, name in found[:150]:
        try:
            data = nass('api_GET', key, short_desc=name, agg_level_desc='NATIONAL').get('data', [])
        except Exception as e:
            rows.append((group, name, 'ERROR', '', '', 0, str(e)[:60])); continue
        recs = []
        for d in data:
            per = (d.get('reference_period_desc') or '').upper()
            freq = (d.get('freq_desc') or '').upper()
            try:
                v = float(str(d.get('Value', '')).replace(',', ''))
                y = int(d.get('year'))
            except ValueError:
                continue
            m = MONTHS.get(per[:3]) if freq == 'MONTHLY' else (1 if freq == 'ANNUAL' else None)
            if m is None:
                continue
            recs.append({'series': name, 'group': group, 'freq': freq, 'date': f'{y}-{m:02d}-01', 'value': v})
        if not recs:
            rows.append((group, name, '-', '', '', 0, 'no monthly/annual numeric values')); continue
        df = pd.DataFrame(recs).drop_duplicates(['series', 'freq', 'date']).sort_values('date')
        frames.append(df)
        for fq, g in df.groupby('freq'):
            rows.append((group, name, fq, g.date.iloc[0][:7], g.date.iloc[-1][:7], len(g), f'{g.value.iloc[-1]:g}'))
    if frames:
        os.makedirs(OUT, exist_ok=True)
        pd.concat(frames).to_csv(os.path.join(OUT, 'nass_national_indexes.csv'), index=False)
    md += ['| Group | Series | Freq | First | Last | N | Latest |', '|---|---|---|---|---|---|---|']
    for r in rows:
        md.append('| ' + ' | '.join(str(x) for x in r) + ' |')


def probe_fred(key, md, log):
    md += ['', '### FRED national candidates', '']
    if not key:
        md.append('FRED_API_KEY is not set.'); return
    seen = {}
    for term in FRED_SEARCHES:
        q = urllib.parse.urlencode({'search_text': term, 'api_key': key, 'file_type': 'json', 'limit': 12,
                                    'order_by': 'popularity', 'sort_order': 'desc'})
        try:
            res = http_json(f'https://api.stlouisfed.org/fred/series/search?{q}')
        except Exception as e:
            log.append(f'FRED search {term!r} failed: {e}'); continue
        for s in res.get('seriess', []):
            if s['id'] not in seen:
                seen[s['id']] = (term, s['id'], s['title'][:90], s['frequency_short'], s['observation_start'][:7],
                                 s['observation_end'][:7], s.get('seasonal_adjustment_short', ''))
    md += ['| Search | ID | Title | Freq | Start | End | SA |', '|---|---|---|---|---|---|---|']
    for r in seen.values():
        md.append('| ' + ' | '.join(str(x).replace('|', '/') for x in r) + ' |')
    os.makedirs(OUT, exist_ok=True)
    pd.DataFrame(list(seen.values()), columns=['search', 'id', 'title', 'freq', 'start', 'end', 'sa']).to_csv(
        os.path.join(OUT, 'fred_candidates.csv'), index=False)


def main():
    md, log = ['## FFAI v4 data probe (nothing published)'], []
    probe_nass(os.environ.get('NASS_API_KEY', '').strip(), md, log)
    probe_fred(os.environ.get('FRED_API_KEY', '').strip(), md, log)
    md[1:1] = [''] + [f'- {l}' for l in log]
    text = '\n'.join(md) + '\n'
    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, 'probe_report.md'), 'w', encoding='utf-8').write(text)
    print(text)
    p = os.environ.get('GITHUB_STEP_SUMMARY')
    if p:
        open(p, 'a', encoding='utf-8').write(text)


if __name__ == '__main__':
    main()

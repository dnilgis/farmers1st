#!/usr/bin/env python3
"""
FFAI v4 - Farmers First Ag Index, national terms-of-trade build.

WHAT IT MEASURES
  What U.S. farms are paid for what they sell, against what they pay for what
  they buy. Both sides are USDA NASS national price indexes (2011 = 100):
    All farms   COMMODITY TOTALS (received)  / PPITW, all commodities, services,
                interest, taxes & wage rates (paid). This is USDA's own
                published "ratio of prices received to prices paid".
    Crops       CROP TOTALS (received)       / CROP SECTOR (paid)
    Livestock   LIVESTOCK TOTALS (received)  / ANIMAL SECTOR (paid)
    Dairy       DAIRY PRODUCT TOTALS (received) / ANIMAL SECTOR (paid)
  Quarter = average of its 3 months; a quarter is used only when all 3 months
  of both sides are published. Full monthly history starts Q1 1995 (USDA
  reported costs only 4 months a year in 1990-94).

TWO CANDIDATE SCORES (both 0-100, both use only data up to that quarter or a
fixed base, so published values never move because of the method):
  A  "level"   - the ratio's percentile within the fixed base period 1995-2019.
  B  "decade"  - the ratio divided by its average over the previous 40
                 quarters (real time), as a percentile within 2005-2019.
                 Allows for the slow long-run decline in the ratio (yields
                 rise, so farms live with lower price ratios over decades).

PRE-REGISTERED VALIDATION (written Oct 7, 2026, before any of these tests
were run; committed to git before the first v4 run so the timing is checkable)
  Target: USDA net farm income (FRED B1448C1A027NBEA), deflated by CPI
  (CPIAUCSL annual average). Second target: the same minus federal
  agricultural subsidies (FRED L312041A027NBEA), i.e. market income.
  Annual, year-over-year changes, so trends shared by both series cannot
  produce a fake correlation.
    T1  corr(change in the candidate's annual average log measure,
             change in log real net farm income) > 0 with one-sided p < 0.05,
        p computed with an effective sample size corrected for
        autocorrelation of both changed series.
    T2  same as T1 against market income (net farm income minus subsidies).
    T3  out of sample: predicting this year's change in log real net farm
        income from this year's change in the measure (expanding regression,
        first 10 years used only for fitting) has lower RMSE than BOTH
        "no change" and "same change as last year".
  Decision: the headline uses the candidate that passes more of T1-T3.
  Tie -> A (simpler, and it is USDA's own ratio). If neither passes T1,
  v4 ships as a descriptive terms-of-trade index and the site says it is
  not validated against farm income.
  National farm loan delinquency is reported for reference only; no claim.
"""
import json, math, os, sys, time, urllib.parse, urllib.request
import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'v4')
NASS = 'https://quickstats.nass.usda.gov/api/'
MONTHS = {m: i + 1 for i, m in enumerate(['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'])}
BASE_A = ('1995-01-01', '2019-10-01')
BASE_B = ('2005-01-01', '2019-10-01')
TRAIL = 40  # quarters for candidate B
# Headline method, fixed after the launch decision (run 6, Oct 7 2026: A and B both
# passed 3/3, tie -> A by the pre-registered rule). Fixed so the headline cannot
# switch methods from one quarter to the next. Tests still run and print every quarter.
HEADLINE_METHOD = 'A'

SECTORS = {  # name: (received series, paid series)
    'all':       ('COMMODITY TOTALS - INDEX FOR PRICE RECEIVED, 2011',
                  'PPITW, (COMMODITIES, SERVICES, INTEREST, TAXES & WAGE RATES) - INDEX FOR PRICE PAID, 2011'),
    'crops':     ('CROP TOTALS - INDEX FOR PRICE RECEIVED, 2011', 'CROP SECTOR - INDEX FOR PRICE PAID, 2011'),
    'livestock': ('LIVESTOCK TOTALS - INDEX FOR PRICE RECEIVED, 2011', 'ANIMAL SECTOR - INDEX FOR PRICE PAID, 2011'),
    'dairy':     ('DAIRY PRODUCT TOTALS - INDEX FOR PRICE RECEIVED, 2011', 'ANIMAL SECTOR - INDEX FOR PRICE PAID, 2011'),
}
USDA_RATIO = 'PRICE INDEX RATIO, RECEIVED TO PAID (PPITW), 2011 - RATIO, MEASURED IN PCT'
DRIVERS = {  # label: series (2011 = 100 indexes)
    'Prices: feed grains': 'FEED GRAINS - INDEX FOR PRICE RECEIVED, 2011',
    'Prices: oilseeds': 'OIL-BEARING CROPS - INDEX FOR PRICE RECEIVED, 2011',
    'Prices: food grains': 'FOOD GRAINS - INDEX FOR PRICE RECEIVED, 2011',
    'Prices: livestock': 'LIVESTOCK TOTALS - INDEX FOR PRICE RECEIVED, 2011',
    'Prices: dairy': 'DAIRY PRODUCT TOTALS - INDEX FOR PRICE RECEIVED, 2011',
    'Costs: feed': 'FEED - INDEX FOR PRICE PAID, 2011',
    'Costs: fuel': 'FUELS - INDEX FOR PRICE PAID, 2011',
    'Costs: fertilizer': 'FERTILIZER TOTALS, INCL LIME & SOIL CONDITIONERS - INDEX FOR PRICE PAID, 2011',
    'Costs: chemicals': 'CHEMICAL TOTALS - INDEX FOR PRICE PAID, 2011',
    'Costs: seed': 'SEEDS & PLANTS TOTALS - INDEX FOR PRICE PAID, 2011',
    'Costs: interest': 'INTEREST - INDEX FOR PRICE PAID, 2011',
    'Costs: wages': 'LABOR, WAGE RATES - INDEX FOR PRICE PAID, 2011',
    'Costs: cash rent': 'RENT, CASH - INDEX FOR PRICE PAID, 2011',
    'Costs: machinery': 'MACHINERY TOTALS - INDEX FOR PRICE PAID, 2011',
}
FARM_PRICES = {  # label: (series, unit)
    'Corn': ('CORN, GRAIN - PRICE RECEIVED, MEASURED IN $ / BU', '$/bu'),
    'Soybeans': ('SOYBEANS - PRICE RECEIVED, MEASURED IN $ / BU', '$/bu'),
    'Wheat': ('WHEAT - PRICE RECEIVED, MEASURED IN $ / BU', '$/bu'),
    'Milk': ('MILK - PRICE RECEIVED, MEASURED IN $ / CWT', '$/cwt'),
    'Steers & heifers': ('CATTLE, STEERS & HEIFERS, GE 500 LBS - PRICE RECEIVED, MEASURED IN $ / CWT', '$/cwt'),
    'Hogs': ('HOGS - PRICE RECEIVED, MEASURED IN $ / CWT', '$/cwt'),
    'Alfalfa hay': ('HAY, ALFALFA - PRICE RECEIVED, MEASURED IN $ / TON', '$/ton'),
}
FRED_IDS = {'nfi': 'B1448C1A027NBEA', 'subsidies': 'L312041A027NBEA', 'cpi': 'CPIAUCSL', 'delinquency': 'DRFAPGACBS'}


# ------------------------------------------------------------------ data
def http_json(url, timeout=90, tries=3):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'farmers1st.com FFAI v4'})
            return json.loads(urllib.request.urlopen(req, timeout=timeout).read().decode('utf-8'))
        except Exception as e:
            last = e; time.sleep(3 * (i + 1))
    raise last


def nass_monthly(names, key, local_csv=None):
    """Monthly values for each NASS short_desc. local_csv = probe file, for offline tests."""
    if local_csv:
        d = pd.read_csv(local_csv)
        d = d[(d.freq == 'MONTHLY') & d.series.isin(names)].drop_duplicates(['series', 'date'])
        d['date'] = pd.to_datetime(d.date)
        return d.pivot(index='date', columns='series', values='value').sort_index()
    cols = {}
    for n in names:
        q = urllib.parse.urlencode({'key': key, 'format': 'JSON', 'short_desc': n, 'agg_level_desc': 'NATIONAL',
                                    'freq_desc': 'MONTHLY'})
        data = http_json(f'{NASS}api_GET/?{q}').get('data', [])
        s = {}
        for r in data:
            m = MONTHS.get((r.get('reference_period_desc') or '')[:3].upper())
            try:
                v = float(str(r.get('Value', '')).replace(',', ''))
            except ValueError:
                continue
            if m:
                s[pd.Timestamp(int(r['year']), m, 1)] = v
        if not s:
            raise RuntimeError(f'NASS returned no monthly values for {n!r}')
        cols[n] = pd.Series(s)
    return pd.DataFrame(cols).sort_index()


def fred(series_id, key):
    q = urllib.parse.urlencode({'series_id': series_id, 'api_key': key, 'file_type': 'json'})
    obs = http_json(f'https://api.stlouisfed.org/fred/series/observations?{q}')['observations']
    s = pd.Series({pd.Timestamp(o['date']): float(o['value']) for o in obs if o['value'] not in ('.', '')})
    return s.sort_index()


def to_quarters(m):
    """Quarter mean, kept only where all 3 months exist."""
    q = m.resample('QS').mean()
    n = m.resample('QS').count()
    return q.where(n == 3)


def qlabel(t):
    return f"Q{(t.month - 1) // 3 + 1}'{str(t.year)[2:]}"


# ------------------------------------------------------------------ scoring
def pct_in(base, x):
    """Percentile of x within base (share of base values <= x, 0-100)."""
    b = np.asarray(base.dropna())
    return np.nan if np.isnan(x) or len(b) == 0 else 100.0 * (b <= x).mean()


def score(q):
    out = pd.DataFrame(index=q.index)
    for s, (rcv, pd_) in SECTORS.items():
        ratio = 100 * q[rcv] / q[pd_]
        out[f'{s}_ratio'] = ratio
        base_a = ratio.loc[BASE_A[0]:BASE_A[1]]
        out[f'{s}_A'] = [pct_in(base_a, v) for v in ratio]
        trail = ratio.shift(1).rolling(TRAIL, min_periods=TRAIL).mean()
        rel = ratio / trail
        out[f'{s}_rel'] = rel
        base_b = rel.loc[BASE_B[0]:BASE_B[1]]
        out[f'{s}_B'] = [pct_in(base_b, v) for v in rel]
    return out


def regime(v):
    return None if v is None or np.isnan(v) else 'STRONG' if v >= 70 else 'FAVORABLE' if v >= 55 else 'GUARDED' if v >= 40 else 'STRESSED'


# ------------------------------------------------------------------ validation
def eff_n_p(x, y):
    d = pd.concat([x, y], axis=1).dropna()
    n = len(d)
    if n < 8:
        return np.nan, n, np.nan, np.nan
    r = d.iloc[:, 0].corr(d.iloc[:, 1])
    r1, r2 = d.iloc[:, 0].autocorr(1), d.iloc[:, 1].autocorr(1)
    ne = n * (1 - r1 * r2) / (1 + r1 * r2) if (1 + r1 * r2) > 0 else n
    ne = max(min(ne, n), 3)
    t = r * math.sqrt((ne - 2) / max(1 - r * r, 1e-12))
    return r, n, ne, stats.t.sf(t, ne - 2)  # one-sided, H1: r > 0


def oos(x, y, warm=10):
    d = pd.concat([x, y], axis=1, keys=['x', 'y']).dropna()
    e_model, e_zero, e_last = [], [], []
    for i in range(warm, len(d)):
        tr = d.iloc[:i]
        A = np.c_[np.ones(len(tr)), tr.x.values]
        b = np.linalg.lstsq(A, tr.y.values, rcond=None)[0]
        yhat = b[0] + b[1] * d.x.iloc[i]
        e_model.append(d.y.iloc[i] - yhat)
        e_zero.append(d.y.iloc[i])
        e_last.append(d.y.iloc[i] - d.y.iloc[i - 1])
    r = lambda e: float(np.sqrt(np.mean(np.square(e)))) if e else np.nan
    return r(e_model), r(e_zero), r(e_last), len(e_model)


def validate(sc, fr, md):
    cpi_a = fr['cpi'].groupby(fr['cpi'].index.year).mean()
    nfi = fr['nfi'].groupby(fr['nfi'].index.year).mean()
    sub = fr['subsidies'].groupby(fr['subsidies'].index.year).mean()
    real = (nfi / cpi_a).dropna()
    market = ((nfi - sub) / cpi_a).dropna()
    targets = {'real net farm income': np.log(real).diff(),
               'real market income (NFI minus federal ag subsidies)': np.log(market[market > 0]).diff()}
    res = {}
    detail = {}
    md += ['', '## Pre-registered validation (annual, year-over-year changes)', '',
           'Measures use the all-farms ratio. A = log ratio; B = log(ratio / previous 40-quarter average). '
           'Annual value = mean of the year\'s 4 quarters (years with all 4 only).', '']
    for cand, col in (('A', 'all_ratio'), ('B', 'all_rel')):
        s = np.log(sc[col])
        yr = s.groupby(s.index.year)
        ann = yr.mean().where(yr.count() == 4).dropna()
        dx = ann.diff()
        passes = {}
        rows = []
        for tname, dy in targets.items():
            r, n, ne, p = eff_n_p(dx, dy)
            rows.append(f'| {cand} | corr with change in {tname} | r = {r:+.2f} | n = {n} years, effective n = {ne:.1f} | one-sided p = {p:.3f} | {"PASS" if (r > 0 and p < 0.05) else "fail"} |')
            tk = 'T1' if tname.startswith('real net') else 'T2'
            passes[tk] = bool(r > 0 and p < 0.05)
            detail.setdefault(cand, {})[tk] = {'r': round(float(r), 3), 'n_years': int(n), 'eff_n': round(float(ne), 1), 'p_one_sided': float(f'{p:.2g}'), 'target': tname}
        m, z, l, n_oos = oos(dx, targets['real net farm income'])
        t3 = bool(m < z and m < l)
        rows.append(f'| {cand} | out-of-sample error, change in log real NFI | model {m:.3f} vs no-change {z:.3f} vs last-year {l:.3f} | {n_oos} test years | | {"PASS" if t3 else "fail"} |')
        passes['T3'] = t3
        detail.setdefault(cand, {})['T3'] = {'rmse_model': round(m, 3), 'rmse_no_change': round(z, 3), 'rmse_last_year': round(l, 3), 'test_years': int(n_oos)}
        res[cand] = passes
        md += ['| Cand. | Test | Result | Sample | p | Verdict |', '|---|---|---|---|---|---|'] if cand == 'A' else []
        md += rows
    na, nb = sum(res['A'].values()), sum(res['B'].values())  # before detail is added
    rule_pick = 'B' if nb > na else 'A'
    winner = HEADLINE_METHOD
    validated = res[winner]['T1']
    md += ['', f'Tests passed: A {na}/3, B {nb}/3 (the launch rule would pick {rule_pick} today). Headline uses **{winner}**, fixed at launch '
               f'({"validated against real net farm income" if validated else "NOT validated: fails T1; ship as descriptive only"}).']
    # reference only
    dq = fr['delinquency']
    for cand, col in (('A', 'all_ratio'), ('B', 'all_rel')):
        x = np.log(sc[col]).diff(); y = dq.reindex(sc.index).diff()
        r, n, ne, p = eff_n_p(-x, y)
        md.append(f'- Reference only: quarterly change in {cand} vs change in national ag loan delinquency: r = {(-r):+.2f} (n = {n}). No claim made.')
    res['detail'] = detail
    return winner, validated, res


# ------------------------------------------------------------------ main
def main():
    key, fkey = os.environ.get('NASS_API_KEY', '').strip(), os.environ.get('FRED_API_KEY', '').strip()
    local = os.environ.get('FFAI_V4_LOCAL_CSV')
    if not local and not key:
        sys.exit('ERROR: NASS_API_KEY is not set.')
    names = sorted({x for p in SECTORS.values() for x in p} | set(DRIVERS.values()) | {v[0] for v in FARM_PRICES.values()} | {USDA_RATIO})
    m = nass_monthly(names, key, local)
    missing = [n for n in names if n not in m.columns]
    if missing:
        sys.exit(f'ERROR: NASS series missing: {missing}')
    q = to_quarters(m)
    need = [x for p in SECTORS.values() for x in p]
    q = q[q[need].notna().all(axis=1)]
    sc = score(q)
    md = ['# FFAI v4 build report (website unchanged)', '',
          f'- NASS data: {m.index.min():%b %Y} to {m.index.max():%b %Y}; complete quarters {qlabel(q.index[0])} to {qlabel(q.index[-1])} ({len(q)})',
          f'- USDA published ratio vs ours, last quarter: USDA {q[USDA_RATIO].iloc[-1]:.1f}, ours {sc["all_ratio"].iloc[-1]:.1f}']
    fr = {k: fred(v, fkey) for k, v in FRED_IDS.items()} if fkey else None
    if fr:
        md.append(f'- FRED: net farm income {fr["nfi"].index.min().year}-{fr["nfi"].index.max().year}, '
                  f'subsidies {fr["subsidies"].index.min().year}-{fr["subsidies"].index.max().year}')
        winner, validated, res = validate(sc, fr, md)
    else:
        winner, validated, res = HEADLINE_METHOD, False, {}
        md.append('- FRED_API_KEY not set: validation skipped (offline test).')

    last = sc.index[-1]
    md += ['', f'## Latest quarter: {qlabel(last)}', '', '| Sector | Ratio (2011 = 100) | A (level pct) | B (vs decade pct) | Headline score | Regime |', '|---|---|---|---|---|---|']
    for s in SECTORS:
        a, b = sc.loc[last, f'{s}_A'], sc.loc[last, f'{s}_B']
        h = b if winner == 'B' else a
        md.append(f'| {s} | {sc.loc[last, f"{s}_ratio"]:.1f} | {a:.1f} | {b:.1f} | {h:.1f} | {regime(h)} |')

    # drivers: quarter-on-quarter and year-on-year % changes
    md += ['', '## What moved (quarter average, % change)', '', '| Item | vs last quarter | vs a year ago |', '|---|---|---|']
    drivers = {}
    for lab, s in DRIVERS.items():
        x = q[s]; qq = 100 * (x.iloc[-1] / x.iloc[-2] - 1); yy = 100 * (x.iloc[-1] / x.iloc[-5] - 1)
        drivers[lab] = {'qoq_pct': round(qq, 1), 'yoy_pct': round(yy, 1)}
        md.append(f'| {lab} | {qq:+.1f}% | {yy:+.1f}% |')
    md += ['', '## Farm-gate prices (USDA, quarter average)', '', '| Item | ' + qlabel(q.index[-5]) + ' | ' + qlabel(q.index[-2]) + ' | ' + qlabel(last) + ' |', '|---|---|---|---|']
    prices = {}
    for lab, (s, unit) in FARM_PRICES.items():
        x = q[s]; prices[lab] = {'unit': unit, 'value': round(float(x.iloc[-1]), 2), 'prev_q': round(float(x.iloc[-2]), 2), 'year_ago': round(float(x.iloc[-5]), 2)}
        md.append(f'| {lab} ({unit}) | {x.iloc[-5]:.2f} | {x.iloc[-2]:.2f} | {x.iloc[-1]:.2f} |')

    os.makedirs(OUT, exist_ok=True)
    tab = sc.copy(); tab.insert(0, 'quarter', [qlabel(t) for t in tab.index])
    for lab, (s, unit) in FARM_PRICES.items():
        tab[f'price_{lab}'] = q[s]
    tab.round(3).to_csv(os.path.join(OUT, 'ffai_v4_quarterly.csv'))
    summary = {'quarter': qlabel(last), 'headline_method': winner, 'validated': bool(validated), 'tests': res,
               'sectors': {s: {'ratio': round(float(sc.loc[last, f'{s}_ratio']), 1),
                               'score': round(float(sc.loc[last, f'{s}_{winner}']), 1),
                               'regime': regime(sc.loc[last, f'{s}_{winner}'])} for s in SECTORS},
               'drivers': drivers, 'farm_prices': prices}
    json.dump(summary, open(os.path.join(OUT, 'ffai_v4_summary.json'), 'w'), indent=2)
    try:
        import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
        fig, ax = plt.subplots(2, 1, figsize=(11, 8), sharex=True)
        for s in SECTORS:
            ax[0].plot(sc.index, sc[f'{s}_ratio'], label=s)
        ax[0].axhline(100, color='gray', lw=.8, ls='--'); ax[0].set_title('Prices received / prices paid (2011 = 100)'); ax[0].legend(); ax[0].grid(alpha=.3)
        for s in SECTORS:
            ax[1].plot(sc.index, sc[f'{s}_{winner}'], label=s)
        ax[1].set_ylim(0, 100); ax[1].set_title(f'Score, method {winner} (0-100)'); ax[1].legend(); ax[1].grid(alpha=.3)
        plt.tight_layout(); plt.savefig(os.path.join(OUT, 'ffai_v4_chart.png'), dpi=120); plt.close()
    except Exception as e:
        md.append(f'(chart failed: {e})')
    text = '\n'.join(md) + '\n'
    open(os.path.join(OUT, 'ffai_v4_report.md'), 'w', encoding='utf-8').write(text)
    print(text)
    p = os.environ.get('GITHUB_STEP_SUMMARY')
    if p:
        open(p, 'a', encoding='utf-8').write(text)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
FFAI experiment: score the same FRED data several ways and compare.
Nothing here touches the website. Run by the "experiment" mode of
.github/workflows/ffai-update.yml; results go to the run summary and to the
artifact (engine/experiment/).

Variants of the sector scores (grain, dairy, livestock):
  S0  current engine: nominal prices, expanding z-scores, expanding percentile rank
  S1  real terms: prices and costs divided by CPI first, otherwise as S0
  S2  fixed base: z-scores against a fixed 2003-2019 base, score = normal curve 0-100
  S3  real terms + fixed base

Composite variants:
  C0  current engine composite (soy + Fed Funds regression)
  Cb  blend of the sector scores, 50% grain / 12% dairy / 38% livestock
      (the engine's own NATIONAL_WEIGHTS, by USDA cash receipts)

Measured for each:
  noise      median quarter-to-quarter move, moves of 50+ points, quarters pinned <=5 or >=95
  revisions  how much past values change when one more quarter of data is added
             (re-scored on data ending at each of the last 12 quarters)
  vs national delinquency (FRED DRFAPGACBS): level and change correlation,
             effective sample size, and whether it improves a next-quarter
             forecast over "same as last quarter" (expanding, out of sample)
  vs Chicago Fed 7th District loan repayment index (if the file can be read)

Usage:  FRED_API_KEY=... python tools/ffai_experiment.py
"""
import importlib.util, io, os, sys, math, urllib.request
import numpy as np
import pandas as pd
from scipy import stats

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'engine', 'experiment')
BASE_START, BASE_END = '2003-01-01', '2019-10-01'
NOMINAL = ['corn_bu', 'soy_bu', 'wheat_bu', 'crude', 'diesel_ppi', 'fert_ppi', 'machinery_ppi',
           'milk_ppi', 'cheese_ppi', 'butter_ppi', 'cattle_ppi', 'hogs_ppi']
SECTORS = ['grain', 'dairy', 'livestock']
WEIGHTS = {'grain': 0.50, 'dairy': 0.12, 'livestock': 0.38}
CHICAGO_URLS = [
    'https://www.chicagofed.org/-/media/others/research/data/agconditions/credit-conditions-7th-district-xls.xls?sc_lang=en&hash=20BBD1A1826B74788382F81834584451',
    'https://www.chicagofed.org/-/media/others/research/data/agconditions/credit-conditions-7th-district-xls.xls',
]


def load_engine():
    spec = importlib.util.spec_from_file_location('engine', os.path.join(ROOT, 'engine', 'ffai_v3_engine.py'))
    eng = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(eng)
    return eng


def drop_incomplete(eng, df):
    """Same rule as engine main(): last quarter needs all 3 months of every monthly input."""
    today = pd.Timestamp.today()
    if len(df) and (today - df.index[-1]).days < 60:
        df = df.iloc[:-1]
    while len(df):
        last = df.index[-1]
        short = [n for n, c in eng.MONTH_COUNTS.items() if n != 'delinquency' and int(c.get(last, 0)) < 3]
        if not short:
            break
        df = df.iloc[:-1]
    return df


# ---------------------------------------------------------------- scoring
def zscore_fixed_factory(index):
    base = (index >= pd.Timestamp(BASE_START)) & (index <= pd.Timestamp(BASE_END))
    def zfixed(series):
        v = series.values.astype(float)
        b = v[base & ~np.isnan(v)]
        if len(b) < 8:
            return np.full(len(v), np.nan)
        return (v - b.mean()) / (b.std() + 0.001)
    return zfixed


def score(eng, raw, real, fixed):
    df = raw.copy()
    if real:
        cpi = df['cpi'] / df['cpi'].dropna().iloc[0]
        for c in NOMINAL:
            if c in df.columns:
                df[c] = df[c] / cpi
    orig = eng.zscore_expanding
    if fixed:
        eng.zscore_expanding = zscore_fixed_factory(df.index)
    try:
        df, _ = eng.compute_sub_indexes(df)
    finally:
        eng.zscore_expanding = orig
    if fixed:
        base = (df.index >= pd.Timestamp(BASE_START)) & (df.index <= pd.Timestamp(BASE_END))
        for s in SECTORS:
            m = df[f'{s}_margin']
            b = m[base].dropna()
            df[s] = 100 * stats.norm.cdf((m - b.mean()) / (b.std() + 1e-9))
    else:
        df = eng.scale_sub_indexes(df)
    df['blend'] = sum(WEIGHTS[s] * df[s] for s in SECTORS)
    return df


def engine_composite(eng, raw):
    return eng.compute_composite(raw.copy())['composite']


# ---------------------------------------------------------------- metrics
def noise(s):
    s = s.dropna(); ch = s.diff().abs().dropna()
    return {'median_move': ch.median(), 'moves_50': int((ch >= 50).sum()),
            'pinned': int(((s <= 5) | (s >= 95)).sum()), 'n': len(s)}


def eff_n(a, b):
    r1, r2 = a.autocorr(1), b.autocorr(1)
    return len(a) * (1 - r1 * r2) / (1 + r1 * r2)


def vs_target(x, y):
    """x: index series, y: target series (higher = more stress for delinquency)."""
    d = pd.concat([x, y], axis=1, keys=['x', 'y']).dropna()
    if len(d) < 25:
        return None
    r = d.x.corr(d.y); ne = eff_n(d.x, d.y)
    t = r * math.sqrt(max(ne - 2, 1e-9) / max(1 - r * r, 1e-9))
    p = 2 * stats.t.sf(abs(t), max(ne - 2, 1)) if ne > 2 else float('nan')
    rc = d.x.diff().corr(d.y.diff())
    # next-quarter forecast: y(t+1) ~ y(t)  vs  y(t+1) ~ y(t) + x(t), expanding, out of sample
    yy = d.y.shift(-1).iloc[:-1].values; X = d.iloc[:-1]
    A1 = np.c_[np.ones(len(X)), X.y.values]; A2 = np.c_[A1, X.x.values]
    e1, e2 = [], []
    for i in range(20, len(X)):
        b1 = np.linalg.lstsq(A1[:i], yy[:i], rcond=None)[0]; b2 = np.linalg.lstsq(A2[:i], yy[:i], rcond=None)[0]
        e1.append(yy[i] - A1[i] @ b1); e2.append(yy[i] - A2[i] @ b2)
    return {'r': r, 'eff_n': ne, 'p_adj': p, 'r_change': rc,
            'rmse_persist': float(np.sqrt(np.mean(np.square(e1)))), 'rmse_with': float(np.sqrt(np.mean(np.square(e2)))),
            'n': len(d), 'n_oos': len(e1)}


def revisions(fn, raw, k=12):
    """Mean and max change of already-published values when one quarter is added."""
    diffs = []
    for T in range(len(raw) - k, len(raw)):
        a = fn(raw.iloc[:T]); b = fn(raw.iloc[:T + 1])
        common = a.dropna().index.intersection(b.dropna().index)
        if len(common):
            diffs.extend((b[common] - a[common]).abs().tolist())
    d = np.array(diffs) if diffs else np.array([np.nan])
    return {'mean_rev': float(np.nanmean(d)), 'max_rev': float(np.nanmax(d)), 'share_changed': float(np.nanmean(d >= 0.05))}


# ---------------------------------------------------------------- Chicago Fed
def chicago_repayment(log):
    """Try to read the 7th District non-real-estate loan repayment index (quarterly)."""
    data = None
    for u in CHICAGO_URLS:
        try:
            req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0 (farmers1st.com FFAI research)'})
            data = urllib.request.urlopen(req, timeout=60).read()
            log.append(f'Chicago Fed file: downloaded {len(data)} bytes from {u.split("?")[0]}')
            break
        except Exception as e:
            log.append(f'Chicago Fed file: {u.split("?")[0]} failed: {e}')
    if not data:
        return None
    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, 'chicagofed_credit_conditions.xls'), 'wb').write(data)
    try:
        sheets = pd.read_excel(io.BytesIO(data), sheet_name=None, header=None)
    except Exception as e:
        log.append(f'Chicago Fed file: could not open as a spreadsheet: {e}')
        return None
    # Save the top of every sheet so a proper reader can be written if the guess below fails.
    with open(os.path.join(OUT, 'chicagofed_layout.txt'), 'w', encoding='utf-8') as f:
        for name, sh in sheets.items():
            f.write(f'=== sheet {name!r} shape {sh.shape}\n{sh.head(15).to_string()}\n\n')
    for name, sh in sheets.items():
        for hr in range(min(15, len(sh))):
            row = [str(v).lower() for v in sh.iloc[hr].values]
            cols = [j for j, v in enumerate(row) if 'repayment' in v]
            if not cols:
                continue
            body = sh.iloc[hr + 1:]
            dates = pd.to_datetime(body.iloc[:, 0], errors='coerce')
            vals = pd.to_numeric(body.iloc[:, cols[0]], errors='coerce')
            s = pd.Series(vals.values, index=dates).dropna()
            s = s[s.index.notna()]
            if len(s) >= 25:
                s.index = s.index.to_period('Q').to_timestamp()
                s = s.groupby(level=0).mean()
                log.append(f'Chicago Fed repayment index: sheet {name!r}, column {sh.iloc[hr, cols[0]]!r}, '
                           f'{len(s)} quarters, {s.index[0].date()} to {s.index[-1].date()}, latest {s.iloc[-1]}')
                return s
    log.append('Chicago Fed file: no "repayment" column found automatically; see chicagofed_layout.txt in the artifact')
    return None


# ---------------------------------------------------------------- main
def main():
    eng = load_engine()
    log = []
    raw = drop_incomplete(eng, eng.pull_fred_data())
    log.append(f'FRED data through {raw["quarter"].iloc[-1]} ({len(raw)} quarters)')

    variants = {'S0': (False, False), 'S1': (True, False), 'S2': (False, True), 'S3': (True, True)}
    names = {'S0': 'current', 'S1': 'real terms', 'S2': 'fixed base', 'S3': 'real + fixed base'}
    res = {k: score(eng, raw, *v) for k, v in variants.items()}
    comp0 = engine_composite(eng, raw)

    # common evaluation window: quarters where the current engine publishes a score
    win = res['S0']['grain'].dropna().index.intersection(comp0.dropna().index)
    delq = raw['delinquency']
    chi = chicago_repayment(log)

    series = {'C0 composite (current)': comp0}
    for k in variants:
        for s in SECTORS:
            series[f'{k} {s}'] = res[k][s]
        series[f'{k} blend composite'] = res[k]['blend']
    table = pd.DataFrame({k: v.reindex(win) for k, v in series.items()})
    os.makedirs(OUT, exist_ok=True)
    out = table.copy(); out.insert(0, 'quarter', raw['quarter'].reindex(win)); out['delinquency'] = delq.reindex(win)
    if chi is not None:
        out['chicago_repayment'] = chi.reindex(win)
    out.round(2).to_csv(os.path.join(OUT, 'experiment_series.csv'))

    md = ['## FFAI experiment (nothing published)', '', *[f'- {l}' for l in log],
          f'- Evaluation window: {raw["quarter"].reindex(win).iloc[0]} to {raw["quarter"].reindex(win).iloc[-1]} ({len(win)} quarters)',
          f'- Fixed base period for S2/S3: {BASE_START[:4]}-{BASE_END[:4]}', '']

    md += ['### Latest quarter, each way', '', '| Series | ' + ' | '.join(raw['quarter'].reindex(win).iloc[-4:]) + ' |',
           '|---|' + '---|' * 4]
    for k, v in table.items():
        md.append(f'| {k} | ' + ' | '.join(f'{x:.1f}' for x in v.iloc[-4:]) + ' |')

    md += ['', '### Noise (lower is steadier)', '', '| Series | median move | moves 50+ | pinned <=5 or >=95 |', '|---|---|---|---|']
    for k, v in table.items():
        z = noise(v); md.append(f'| {k} | {z["median_move"]:.1f} | {z["moves_50"]} | {z["pinned"]}/{z["n"]} |')

    md += ['', '### Revisions to past values when one quarter is added (last 12 quarters)', '',
           'From the scoring method only (rescaling, ranking). FRED revising its own data is on top of this and is not simulated here.', '',
           '| Series | mean change | max change | share of past values that move |', '|---|---|---|---|']
    rev_fns = {'C0 composite (current)': lambda r: engine_composite(eng, r)}
    for k, v in variants.items():
        rev_fns[f'{k} grain'] = (lambda r, v=v: score(eng, r, *v)['grain'])
        rev_fns[f'{k} blend composite'] = (lambda r, v=v: score(eng, r, *v)['blend'])
    for k, fn in rev_fns.items():
        z = revisions(fn, raw); md.append(f'| {k} | {z["mean_rev"]:.2f} | {z["max_rev"]:.1f} | {100*z["share_changed"]:.0f}% |')

    def target_table(title, target, note):
        rows = ['', f'### vs {title}', '', note, '',
                '| Series | r (level) | effective N | p (adjusted) | r (changes) | next-qtr error: last qtr only | + this series | helps? |',
                '|---|---|---|---|---|---|---|---|']
        for k, v in table.items():
            z = vs_target(v, target.reindex(win))
            if z is None:
                continue
            helps = 'yes' if z['rmse_with'] < z['rmse_persist'] else 'no'
            rows.append(f'| {k} | {z["r"]:+.2f} | {z["eff_n"]:.1f} | {z["p_adj"]:.2f} | {z["r_change"]:+.2f} | '
                        f'{z["rmse_persist"]:.3f} | {z["rmse_with"]:.3f} | {helps} |')
        return rows

    md += target_table('national farm loan delinquency (FRED DRFAPGACBS)', delq,
                       'Good index = negative r (higher score, less delinquency) and "helps? yes".')
    if chi is not None:
        md += target_table('Chicago Fed 7th District loan repayment index', chi,
                           'Good index = positive r (higher score, better repayment) and "helps? yes".')
    else:
        md += ['', '### vs Chicago Fed repayment index', '', 'Not available this run (see log lines above).']

    # chart
    try:
        import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
        fig, ax = plt.subplots(2, 1, figsize=(11, 8), sharex=True)
        for k in ['C0 composite (current)', 'S0 blend composite', 'S3 blend composite']:
            ax[0].plot(table.index, table[k], label=k)
        ax[0].set_title('Composite variants'); ax[0].set_ylim(0, 100); ax[0].legend(); ax[0].grid(alpha=.3)
        for k in ['S0 grain', 'S1 grain', 'S2 grain', 'S3 grain']:
            ax[1].plot(table.index, table[k], label=k)
        ax[1].set_title('Grain sub-index variants'); ax[1].set_ylim(0, 100); ax[1].legend(); ax[1].grid(alpha=.3)
        plt.tight_layout(); plt.savefig(os.path.join(OUT, 'experiment_chart.png'), dpi=120); plt.close()
    except Exception as e:
        md.append(f'\n(chart failed: {e})')

    text = '\n'.join(md) + '\n'
    open(os.path.join(OUT, 'experiment_report.md'), 'w', encoding='utf-8').write(text)
    print(text)
    p = os.environ.get('GITHUB_STEP_SUMMARY')
    if p:
        open(p, 'a', encoding='utf-8').write(text)


if __name__ == '__main__':
    main()

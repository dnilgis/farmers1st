#!/usr/bin/env python3
"""
FFAI v4 stress test. Publishes nothing and changes no site file.

    FFAI_V4_LOCAL_CSV=engine/v4probe/nass_national_indexes.csv python tools/ffai_v4_stress.py
    NASS_API_KEY=... FRED_API_KEY=... python tools/ffai_v4_stress.py

Uses the engine's own functions (engine/ffai_v4.py) so it scores exactly what the
site scores. Writes engine/stress/stress_report.md and prints it.

Part 1 needs only USDA NASS (works offline from the probe CSV):
  reproduce the committed engine CSV; all-farms ratio vs USDA's published ratio;
  the latest quarter under other base periods; how often each regime label has been
  true; published (whole-period) scores vs what a reader saw at the time; how often
  the two pre-registered candidates disagree; seasonality; a +/-5% shock to each side;
  the dairy score under other USDA cost indexes; how well the first one or two months
  of a quarter predict the full quarter (a possible monthly reading).
Part 2 needs FRED_API_KEY (skipped offline, and says so):
  the pre-registered tests re-run under other start years, without 2020-2022, without
  the latest (forecast) year, with no deflator and with USDA's own CPI series; 95%
  ranges for r; a Holm correction across all tests; real net farm income in years
  under each regime label; and, where ALFRED has them, the tests on the net farm
  income figures first published for each year instead of today's revised ones.
"""
import importlib.util, math, os, sys
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'engine', 'stress')
spec = importlib.util.spec_from_file_location('ffai_v4', os.path.join(ROOT, 'engine', 'ffai_v4.py'))
E = importlib.util.module_from_spec(spec); spec.loader.exec_module(E)

CPI_NASS = 'CONSUMER PRICE INDEX - INDEX FOR PRICE PAID, 2011'
PITW = 'PITW, (PRODUCTION ITEMS, INTEREST TAXES & WAGE RATES) - INDEX FOR PRICE PAID, 2011'
PROD = 'PRODUCTION ITEMS - INDEX FOR PRICE PAID, 2011'
REGIMES = ('STRESSED', 'GUARDED', 'FAVORABLE', 'STRONG')


# ------------------------------------------------------------------ helpers (tested)
def fisher_ci(r, n_eff):
    if r is None or not np.isfinite(r) or n_eff is None or n_eff <= 3 or abs(r) >= 1:
        return (np.nan, np.nan)
    z, se = math.atanh(r), 1 / math.sqrt(n_eff - 3)
    return (math.tanh(z - 1.96 * se), math.tanh(z + 1.96 * se))


def holm(pvals, alpha=0.05):
    """True/False per p value: rejected under Holm's step-down correction."""
    order = sorted(range(len(pvals)), key=lambda i: pvals[i])
    out, stop = [False] * len(pvals), False
    for rank, i in enumerate(order):
        if not stop and pvals[i] < alpha / (len(pvals) - rank):
            out[i] = True
        else:
            stop = True
    return out


def seasonal_factors(series):
    """Mean log deviation (in %) from a centred 2x4 moving average, by quarter of year."""
    r = np.log(series.dropna())
    ma = (r.rolling(4).mean().shift(-2) + r.rolling(4).mean().shift(-1)) / 2
    dev = (r - ma).dropna()
    g = dev.groupby(dev.index.quarter)
    return {int(k): (100 * g.mean()[k], 100 * g.std()[k] / math.sqrt(g.count()[k])) for k in g.mean().index}


def partial_quarter_error(rcv, paid, months):
    """Ratio from the first `months` months of each quarter vs the full-quarter ratio, in %."""
    full = 100 * E.to_quarters(rcv) / E.to_quarters(paid)
    m = pd.concat([rcv, paid], axis=1, keys=['r', 'p']).dropna()
    m = m[m.index.month.isin([mm for mm in range(1, 13) if (mm - 1) % 3 < months])]
    part = m.resample('QS').mean()
    part = 100 * part.r / part.p
    err = 100 * (part / full - 1)
    return err.dropna(), part, full


def regime_freq(scores):
    v = scores.dropna().map(E.regime).value_counts()
    return {k: int(v.get(k, 0)) for k in REGIMES}


# ------------------------------------------------------------------ part 1
def part1(m, q, sc, md):
    last = sc.index[-1]
    md += ['## Part 1: USDA NASS only', '']
    committed = os.path.join(ROOT, 'engine', 'v4', 'ffai_v4_quarterly.csv')
    if os.path.exists(committed):
        c = pd.read_csv(committed, index_col=0, parse_dates=True)
        common = c.index.intersection(sc.index)
        diff = max(float((c.loc[common, f'{s}_A'] - sc.loc[common, f'{s}_A']).abs().max()) for s in E.SECTORS)
        dr = max(float((c.loc[common, f'{s}_ratio'] - sc.loc[common, f'{s}_ratio']).abs().max()) for s in E.SECTORS)
        md.append(f'- Rebuild vs committed engine CSV: {len(common)} quarters in common; largest ratio gap {dr:.3f}, largest score gap {diff:.1f}.')
    gap = sc['all_ratio'] - q[E.USDA_RATIO]
    md.append(f'- All-farms ratio minus USDA published ratio (USDA rounds to whole numbers): mean {gap.mean():+.2f}, '
              f'largest {gap.abs().max():.2f} ({E.qlabel(gap.abs().idxmax())}), over {gap.notna().sum()} quarters.')

    md += ['', f'### Latest quarter ({E.qlabel(last)}) under other base periods (score A)', '',
           '| Base | All | Crops | Livestock | Dairy |', '|---|---|---|---|---|']
    for b0, b1 in (('1995', '2019'), ('2000', '2019'), ('2010', '2019'), ('1995', '2025'), ('2005', '2024'), ('2016', '2025')):
        row = [E.pct_in(sc[f'{s}_ratio'].loc[b0:f'{b1}-12-31'], sc.loc[last, f'{s}_ratio']) for s in E.SECTORS]
        md.append(f'| {b0}-{b1}{" (published)" if (b0, b1) == ("1995", "2019") else ""} | ' + ' | '.join(f'{v:.0f}' for v in row) + ' |')
    b = sc['all_ratio'].loc[E.BASE_A[0]:E.BASE_A[1]]
    slope = np.polyfit(np.arange(len(b)) / 4, b.values, 1)[0]
    md += ['', f'Trend in the all-farms ratio over the base: {slope:+.2f} points a year.', '']

    md += ['### How often each label has been true (quarters)', '', '| Sector | Score | Whole history | 2020 on |', '|---|---|---|---|']
    for s in E.SECTORS:
        for cand in ('A', 'B'):
            f_all, f_new = regime_freq(sc[f'{s}_{cand}']), regime_freq(sc[f'{s}_{cand}'].loc['2020':])
            fmt = lambda f: ', '.join(f'{k} {v}' for k, v in f.items())
            md.append(f'| {s} | {cand} | {fmt(f_all)} | {fmt(f_new)} |')
    yr = sc['all_A'].groupby(sc.index.year).mean()
    md += ['', 'All-farms score A, yearly average: ' + ', '.join(f'{y} {v:.0f}' for y, v in yr.items()), '']

    rt = pd.Series({t: E.pct_in(sc['all_ratio'].loc[:t].iloc[:-1], sc.loc[t, 'all_ratio']) for t in sc.loc['2000':'2019'].index})
    ins = sc['all_A'].loc['2000':'2019']
    md += ['### Published scores vs what a reader saw at the time (2000-2019)', '',
           f'Published scores rank 1995-2019 quarters against the whole period, later years included. Ranked only against '
           f'quarters already published (from 1995), the score differs by {(rt - ins).abs().mean():.1f} points on average '
           f'(published minus real time {(ins - rt).mean():+.1f}); the label differs in {(rt.map(E.regime) != ins.map(E.regime)).sum()} of {len(rt)} quarters. '
           'From 2020 on the base is entirely in the past, so those scores are real time.', '']

    both = sc[['all_A', 'all_B']].dropna()
    ra, rb = both.all_A.map(E.regime), both.all_B.map(E.regime)
    opp = ((both.all_A < 40) & (both.all_B >= 70)) | ((both.all_A >= 70) & (both.all_B < 40))
    md += ['### The two pre-registered candidates', '',
           f'Both passed all three tests. Their labels differ in {(ra != rb).sum()} of {len(both)} quarters; in {opp.sum()} one says '
           f'STRESSED and the other STRONG. Latest: A {sc.loc[last, "all_A"]:.0f} {E.regime(sc.loc[last, "all_A"])}, '
           f'B {sc.loc[last, "all_B"]:.0f} {E.regime(sc.loc[last, "all_B"])}. The tests checked changes, not levels, so they cannot say which label is right.', '']

    md += ['### Seasonality (mean % above or below the trend, by quarter, with standard error)', '', '| Sector | Q1 | Q2 | Q3 | Q4 |', '|---|---|---|---|---|']
    for s in E.SECTORS:
        f = seasonal_factors(sc[f'{s}_ratio'])
        md.append(f'| {s} | ' + ' | '.join(f'{f[k][0]:+.1f} ({f[k][1]:.1f})' for k in (1, 2, 3, 4)) + ' |')
    mq = sc['all_A'].loc[:'2019']
    md += ['', 'Mean all-farms score by quarter of year, 1995-2019: ' + ', '.join(f'Q{k} {v:.0f}' for k, v in mq.groupby(mq.index.quarter).mean().items()), '']

    md += ['### Shock each side of the latest quarter by 5%', '', '| Sector | Now | Received +5% | Received -5% | Paid +5% | Paid -5% |', '|---|---|---|---|---|---|']
    for s in E.SECTORS:
        x, base = sc.loc[last, f'{s}_ratio'], sc[f'{s}_ratio'].loc[E.BASE_A[0]:E.BASE_A[1]]
        vals = [E.pct_in(base, x * k) for k in (1, 1.05, 0.95, 1 / 1.05, 1 / 0.95)]
        md.append(f'| {s} | ' + ' | '.join(f'{v:.0f}' for v in vals) + ' |')

    rcv = E.SECTORS['dairy'][0]
    md += ['', '### Dairy score under other USDA cost indexes (latest quarter)', '', '| Cost index | Ratio | Score |', '|---|---|---|']
    for lab, p in (('Animal sector (published)', E.SECTORS['dairy'][1]), ('Feed only', E.FEED_PAID), ('Production items', PROD),
                   ('Production items, interest, taxes, wages', PITW), ('Everything farms pay (PPITW)', E.SECTORS['all'][1])):
        if p in q:
            r = 100 * q[rcv] / q[p]
            md.append(f'| {lab} | {r.iloc[-1]:.1f} | {E.pct_in(r.loc[E.BASE_A[0]:E.BASE_A[1]], r.iloc[-1]):.0f} |')

    md += ['', '### A monthly reading between quarters? (all farms)', '']
    rc, pdm = m[E.SECTORS['all'][0]].loc['1995':], m[E.SECTORS['all'][1]].loc['1995':]
    base = sc['all_ratio'].loc[E.BASE_A[0]:E.BASE_A[1]]
    for k in (1, 2):
        err, part, full = partial_quarter_error(rc, pdm, k)
        agree = np.mean([E.regime(E.pct_in(base, part[t])) == E.regime(E.pct_in(base, full[t])) for t in err.index])
        md.append(f'- First {k} month(s) of the quarter vs the full quarter: typical error {err.abs().median():.1f}%, '
                  f'90% of errors within {err.abs().quantile(.9):.1f}%, same label {100 * agree:.0f}% of {len(err)} quarters.')
    md += ['- These use today\'s revised USDA data. The latest month is preliminary when first published, so a real-time '
           'monthly reading would miss by more. Not validated against farm income; experimental only.', '']


# ------------------------------------------------------------------ part 2
def tests_on(dx, targets):
    out = {}
    for name, dy in targets.items():
        r, n, ne, p = E.eff_n_p(dx, dy)
        out[name] = (r, n, ne, p, fisher_ci(r, ne))
    out['T3'] = E.oos(dx, targets['T1'])
    return out


def fred_asof(series_id, key, date):
    """Values of a FRED series as they stood on `date` (ALFRED real-time period)."""
    import urllib.parse
    qs = urllib.parse.urlencode({'series_id': series_id, 'api_key': key, 'file_type': 'json',
                                 'realtime_start': date, 'realtime_end': date})
    obs = E.http_json(f'https://api.stlouisfed.org/fred/series/observations?{qs}')['observations']
    return pd.Series({pd.Timestamp(o['date']): float(o['value']) for o in obs if o['value'] not in ('.', '')}).sort_index()


def part2(m, q, sc, md, fkey):
    md += ['## Part 2: against net farm income (FRED)', '']
    if not fkey:
        md += ['FRED_API_KEY not set, so the income tests were not re-run here. Run the workflow in stress mode to get them.', '']
        return
    fr = {k: E.fred(v, fkey) for k, v in E.FRED_IDS.items()}
    ann = lambda s: s.groupby(s.index.year).mean()
    cpi, nfi, sub = ann(fr['cpi']), ann(fr['nfi']), ann(fr['subsidies'])
    cpi_nass = ann(m[CPI_NASS]) if CPI_NASS in m else None

    def targets(nfi_s, defl):
        real = (nfi_s / defl).dropna() if defl is not None else nfi_s
        mk = ((nfi_s - sub) / defl).dropna() if defl is not None else (nfi_s - sub)
        return {'T1': np.log(real[real > 0]).diff(), 'T2': np.log(mk[mk > 0]).diff()}

    def measure(col):
        s = np.log(sc[col]); g = s.groupby(s.index.year)
        return g.mean().where(g.count() == 4).dropna().diff()

    dA, dB = measure('all_ratio'), measure('all_rel')
    last_year = int(nfi.index.max())
    variants = [('as published (CPI-U)', None, None, cpi, nfi), ('start 2000', 2000, None, cpi, nfi), ('start 2005', 2005, None, cpi, nfi),
                ('without 2020-2022', None, (2020, 2022), cpi, nfi), (f'without {last_year} (USDA forecast)', None, (last_year, last_year), cpi, nfi),
                ('no deflator', None, None, None, nfi)]
    if cpi_nass is not None:
        variants.append(('USDA CPI series as deflator', None, None, cpi_nass, nfi))
    md += ['| Candidate | Variant | T1 r (95% range), n / eff. n, p | T2 r | T3 model vs no change vs last year (test years) |', '|---|---|---|---|---|']
    allp = []
    for cand, dx in (('A', dA), ('B', dB)):
        for lab, start, drop, defl, nf in variants:
            x = dx.copy()
            if start:
                x = x.loc[start:]
            if drop:
                x = x.drop([y for y in range(drop[0], drop[1] + 1) if y in x.index])
            res = tests_on(x, targets(nf, defl))
            r, n, ne, p, ci = res['T1']; r2, *_ , p2, _ = res['T2']; mm, z, l, nt = res['T3']
            if lab.startswith('as published'):
                allp += [p, p2]
            md.append(f'| {cand} | {lab} | {r:+.2f} ({ci[0]:.2f} to {ci[1]:.2f}), {n} / {ne:.1f}, {p:.1g} | {r2:+.2f} | '
                      f'{mm:.3f} vs {z:.3f} vs {l:.3f} ({nt}) |')
    md += ['', f'Holm correction over the 4 published correlation tests: {sum(holm(allp))} of 4 still below 0.05.', '']

    # Regime labels against income
    real = (nfi / cpi).dropna()
    yrA = sc['all_A'].groupby(sc.index.year).mean()
    med = real.loc[1995:2019].median()
    md += ['### Real net farm income in years under each label (all farms, yearly average score A)', '',
           '| Label | Years | Real NFI above its 1995-2019 middle value | Mean change in log real NFI same year | next year |', '|---|---|---|---|---|']
    dl = np.log(real).diff()
    for reg in REGIMES:
        ys = [y for y, v in yrA.items() if E.regime(v) == reg and y in real.index]
        if not ys:
            md.append(f'| {reg} | 0 | | | |'); continue
        above = sum(real[y] > med for y in ys)
        same = np.nanmean([dl.get(y, np.nan) for y in ys]); nxt = np.nanmean([dl.get(y + 1, np.nan) for y in ys])
        md.append(f'| {reg} | {len(ys)} | {above} of {len(ys)} | {same:+.3f} | {nxt:+.3f} |')
    md += ['', 'Years overlap and the labels trend with the base, so these are descriptions, not tests.', '']

    # Vintage: NFI as first published for each year
    try:
        first = {}
        for y in range(1996, last_year + 1):
            s = fred_asof(E.FRED_IDS['nfi'], fkey, f'{y + 1}-03-31')
            if pd.Timestamp(y, 1, 1) in s.index and pd.Timestamp(y - 1, 1, 1) in s.index:
                first[y] = math.log(s[pd.Timestamp(y, 1, 1)] / cpi[y]) - math.log(s[pd.Timestamp(y - 1, 1, 1)] / cpi[y - 1])
        fp = pd.Series(first)
        if len(fp) >= 10:
            r, n, ne, p = E.eff_n_p(dA, fp)
            md += [f'Vintage check: change in log real NFI as published by the end of March after each year ({len(fp)} years): '
                   f'T1 for A r = {r:+.2f}, eff. n {ne:.1f}, p {p:.1g}.', '']
        else:
            md += [f'Vintage check: ALFRED returned first-print values for only {len(fp)} years; not enough to test.', '']
    except Exception as e:  # ALFRED unavailable or series has no vintages
        md += [f'Vintage check not run: {e}', '']


def main():
    key, fkey = os.environ.get('NASS_API_KEY', '').strip(), os.environ.get('FRED_API_KEY', '').strip()
    local = os.environ.get('FFAI_V4_LOCAL_CSV')
    if not local and not key:
        sys.exit('ERROR: set NASS_API_KEY, or FFAI_V4_LOCAL_CSV to the probe CSV.')
    names = sorted({x for p in E.SECTORS.values() for x in p} | {E.USDA_RATIO, E.FEED_PAID, CPI_NASS, PITW, PROD})
    m = E.nass_monthly(names, key, local)
    q = E.to_quarters(m)
    need = [x for p in E.SECTORS.values() for x in p]
    q = q[q[need].notna().all(axis=1)]
    sc = E.score(q)
    md = ['# FFAI v4 stress test (publishes nothing)', '',
          f'NASS data {m.index.min():%b %Y} to {m.index.max():%b %Y}; complete quarters {E.qlabel(q.index[0])} to {E.qlabel(q.index[-1])} ({len(q)}).', '']
    part1(m, q, sc, md)
    part2(m, q, sc, md, fkey)
    os.makedirs(OUT, exist_ok=True)
    text = '\n'.join(md) + '\n'
    open(os.path.join(OUT, 'stress_report.md'), 'w', encoding='utf-8').write(text)
    print(text)
    p = os.environ.get('GITHUB_STEP_SUMMARY')
    if p:
        open(p, 'a', encoding='utf-8').write(text)


if __name__ == '__main__':
    main()

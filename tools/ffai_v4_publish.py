#!/usr/bin/env python3
"""
Write FFAI v4 engine output into the website.

    python tools/ffai_v4_publish.py [--today 2026-10-07]

Reads   engine/v4/ffai_v4_quarterly.csv, engine/v4/ffai_v4_summary.json
Writes  ffai-v4.js            numbers the page reads (never the commentary)
        api/v4/current.json   latest quarter
        api/v4/history.json   every quarter since Q1 1995
        api/v4/history.csv    the same, as a spreadsheet
        api/v4/meta.json      method and validation results
        og-share.png          share image
        index.html            meta description, og:title, twitter:title
Commentary lives in ffai-commentary.js and is written by hand.

Refuses to write anything if a ratio is not positive, a score is outside
0-100, quarters are not consecutive, history got shorter, the engine did
not record its validation results, or the all-farms ratio stops matching
USDA's own published ratio (a sign a series was misread).
"""
import csv, json, math, os, re, subprocess, sys, tempfile
from datetime import date, datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V4 = os.path.join(ROOT, 'engine', 'v4')
sys.path.insert(0, os.path.join(ROOT, 'engine'))
import ffai_v4_labels as L  # noqa: E402  (the one place the label lines live)
SECT = ('all', 'crops', 'livestock', 'dairy')
LABEL = {'all': 'All farms', 'crops': 'Crops', 'livestock': 'Livestock', 'dairy': 'Dairy'}
BASE = '1995–2019'


def fail(msg):
    print(f'REFUSED: {msg}')
    p = os.environ.get('GITHUB_STEP_SUMMARY')
    if p:
        open(p, 'a', encoding='utf-8').write(f'### FFAI v4 publish refused\n\n{msg}\n')
    sys.exit(1)


BASE_TXT = L.BASE_TEXT  # plain hyphen, for metadata and the API
FIRST_LIVE = "Q2'26"    # first quarter v4 scored and published live (Oct 7, 2026); earlier quarters were back-filled
LABEL_COLOUR = {'LOW': '#a63030', 'BELOW MIDDLE': '#8b6508', 'ABOVE MIDDLE': '#2d6a2e', 'HIGH': '#2d6a2e'}


def regime(v):
    """The label (LOW / BELOW MIDDLE / ABOVE MIDDLE / HIGH vs 1995-2019). Computed here, once."""
    return L.label(v)


def colour(v):
    return LABEL_COLOUR[regime(v)]


def qkey(label):
    q, y = parse_q(label)
    return y * 4 + q


def is_real_time(label):
    """True only for quarters scored live, from the v4 launch quarter on. Earlier quarters were
    back-filled; 1995-2019 are also in-sample (ranked against a base that includes later quarters)."""
    return qkey(label) >= qkey(FIRST_LIVE)


def pct(a, b):
    try:
        a, b = float(a), float(b)
    except (TypeError, ValueError):
        return None
    return r1(100 * (a / b - 1)) if b and math.isfinite(a) and math.isfinite(b) else None


def parse_q(label):
    m = re.fullmatch(r"Q([1-4])'(\d\d)", label)
    if not m:
        fail(f'bad quarter label {label!r}')
    yy = int(m.group(2))
    return int(m.group(1)), (1900 + yy if yy >= 90 else 2000 + yy)  # history starts 1995


def next_label(label):
    q, y = parse_q(label)
    return f"Q1'{(y + 1) % 100:02d}" if q == 4 else f"Q{q + 1}'{y % 100:02d}"


def quarter_end(label):
    q, y = parse_q(label)
    return date(y + 1, 1, 1) - timedelta(days=1) if q == 4 else date(y, 3 * q + 1, 1) - timedelta(days=1)


def r1(x):
    return round(float(x), 1)


def load():
    rows = list(csv.DictReader(open(os.path.join(V4, 'ffai_v4_quarterly.csv'), encoding='utf-8')))
    summ = json.load(open(os.path.join(V4, 'ffai_v4_summary.json'), encoding='utf-8'))
    method = summ.get('headline_method')
    if method not in ('A', 'B'):
        fail('summary has no headline method')
    det = (summ.get('tests') or {}).get('detail')
    if not det or method not in det:
        fail('engine summary has no validation detail; run the v4 engine first')
    hist = []
    for r in rows:
        dcol = r.get('') or r.get('date') or next(iter(r.values()))  # index column, however pandas named it
        rec = {'quarter': r['quarter'], 'date': dcol[:10]}
        for s in SECT:
            ratio = r.get(f'{s}_ratio', '')
            sc = r.get(f'{s}_{method}', '')
            rec[s] = r1(ratio) if ratio else None
            rec[f'{s}_score'] = r1(sc) if sc else None
        if rec['all'] is None or rec['all_score'] is None:
            continue
        for s in SECT:
            if rec[s] is not None and not (rec[s] > 0 and math.isfinite(rec[s])):
                fail(f'{rec["quarter"]}: {s} ratio {rec[s]} is not positive')
            if rec[f'{s}_score'] is not None and not (0 <= rec[f'{s}_score'] <= 100):
                fail(f'{rec["quarter"]}: {s} score {rec[f"{s}_score"]} outside 0-100')
        hist.append(rec)
    if len(hist) < 8:
        fail('fewer than 8 scored quarters')
    for h in hist:
        q, y = parse_q(h['quarter'])
        if h['date'] != f'{y}-{3 * q - 2:02d}-01':
            fail(f'{h["quarter"]}: date {h["date"]} does not match the quarter')
    for a, b in zip(hist, hist[1:]):
        if next_label(a['quarter']) != b['quarter']:
            fail(f'quarters not consecutive: {a["quarter"]} then {b["quarter"]}')
    if hist[-1]['quarter'] != summ.get('quarter'):
        fail(f'CSV ends {hist[-1]["quarter"]} but summary says {summ.get("quarter")}')
    gap = usda_check(rows)
    if gap and gap[0] > USDA_TOL:
        fail(f'all-farms ratio is {gap[0]:.2f} points from USDA\'s published ratio in {gap[1]} (limit {USDA_TOL}); check the NASS series')
    old = os.path.join(ROOT, 'api', 'v4', 'history.json')
    if os.path.exists(old):
        n_old = json.load(open(old)).get('count', 0)
        if len(hist) < n_old:
            fail(f'history would shrink from {n_old} to {len(hist)} quarters')
    return hist, summ, method, det, rows


def records(hist, s):
    vals = [(h[s], h['quarter']) for h in hist if h[s] is not None]
    lo, hi = min(vals), max(vals)
    base = [h[s] for h in hist if h[s] is not None and 1995 <= parse_q(h['quarter'])[1] <= 2019]
    return {'low': lo[0], 'low_q': lo[1], 'high': hi[0], 'high_q': hi[1],
            'base_min': min(base), 'base_max': max(base)}


TRAIL = 40  # quarters; matches engine candidate B
USDA_TOL = 1.5  # max gap, all-farms ratio vs USDA's published ratio (USDA rounds to whole numbers)
THRESHOLDS = L.LINES  # (label, score where it starts); defined once in engine/ffai_v4_labels.py


def base_ratios(rows, s):
    """Unrounded 1995-2019 ratios for sector s, straight from the engine CSV."""
    return sorted(float(r[f'{s}_ratio']) for r in rows
                  if r.get(f'{s}_ratio') and 1995 <= parse_q(r['quarter'])[1] <= 2019)


def to_reach(base, x):
    """For each regime line, the ratio where the score reaches it and the % move in the
    ratio that takes it there (prices received moving, prices paid held). Score = share of
    base quarters at or below the ratio, so the line sits at the k-th smallest base value."""
    out = []
    for name, t in THRESHOLDS:
        k = max(-(-t * len(base) // 100) - 1, 0)  # integer ceiling; float 55/100*100 is 55.000000000000007
        v = base[k]
        out.append({'label': name, 'regime': name, 'score': t, 'ratio': r1(v), 'move_pct': r1(100 * (v / x - 1)), 'reached': x >= v})
    return out


def fisher_ci(r, n_eff):
    """95% range for a correlation, Fisher z with the effective sample size."""
    if r is None or n_eff is None or n_eff <= 3 or abs(r) >= 1:
        return None
    z, se = math.atanh(r), 1 / math.sqrt(n_eff - 3)
    return [round(math.tanh(z - 1.96 * se), 2), round(math.tanh(z + 1.96 * se), 2)]


def multiple_tests(tests, det):
    """Say how many tests ran and whether the correlation tests survive a Holm correction."""
    names = [(c, t) for c in ('A', 'B') if c in tests for t in ('T1', 'T2', 'T3')]
    passed = sum(bool(tests[c][t]) for c, t in names)
    ps = sorted(float(det[c][t]['p_one_sided']) for c, t in names if t != 'T3' and c in det and t in det[c])
    holm = all(p < 0.05 / (len(ps) - i) for i, p in enumerate(ps)) if ps else False
    return (f'{len(names)} tests ran ({len(names) // 3} candidate scores x 3 tests); {passed} passed. '
            + ('All correlation tests stay below 0.05 after a Holm correction for running them together. '
               if holm else 'Not every correlation test survives a Holm correction for running them together. ')
            + 'The error tests (T3) have no p value; with ' + ' and '.join(str(det[c]['T3']['test_years']) for c in ('A', 'B') if c in det)
            + ' test years the gap is not tested for significance.')


def usda_check(rows):
    """Largest gap between our all-farms ratio and USDA's published ratio, by quarter."""
    gaps = [(abs(float(r['all_ratio']) - float(r['usda_ratio'])), r['quarter']) for r in rows
            if r.get('usda_ratio') and r.get('all_ratio')]
    return max(gaps) if gaps else None


def revisions(old_hist, hist, tol=0.05):
    """Past quarters whose published ratio or score changed (USDA revisions)."""
    old = {h['quarter']: h for h in old_hist}
    out = []
    for h in hist:
        o = old.get(h['quarter'])
        if o and (abs(o['ratio'] - h['all']) > tol or abs(o['score'] - h['all_score']) > tol):
            out.append(f"{h['quarter']}: ratio {o['ratio']} -> {h['all']}, score {o['score']} -> {h['all_score']}")
    return out


def decade(hist):
    """Latest all-farms ratio against its average over the previous 40 quarters."""
    prev = [h['all'] for h in hist[-1 - TRAIL:-1]]
    if len(prev) < TRAIL:
        return None
    avg = sum(prev) / len(prev)
    return {'avg': r1(avg), 'pct': r1(100 * (hist[-1]['all'] / avg - 1)), 'from': hist[-1 - TRAIL]['quarter'], 'to': hist[-2]['quarter']}


def pfmt(det):
    """Copy of validation detail with tiny p-values shown as '<0.001'."""
    out = json.loads(json.dumps(det))
    for c in out.values():
        for t in c.values():
            if isinstance(t, dict) and 'p_one_sided' in t and t['p_one_sided'] < 0.001:
                t['p_one_sided'] = '<0.001'
    return out


DRIVER_NAME = {'Prices: livestock': 'Prices: meat animals'}
MONTHS = ('January–March', 'April–June', 'July–September', 'October–December')


def check_js(js, expect):
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f:
        f.write(js + '\nprocess.stdout.write(JSON.stringify(FFAI4));\n'); tmp = f.name
    try:
        out = subprocess.run(['node', tmp], capture_output=True, text=True, timeout=30)
    except FileNotFoundError:
        fail('node is not installed, cannot check ffai-v4.js')
    finally:
        os.unlink(tmp)
    if out.returncode:
        fail('ffai-v4.js does not parse: ' + out.stderr.strip().splitlines()[-1])
    got = json.loads(out.stdout)
    for k, v in expect.items():
        cur = got
        for part in k.split('.'):
            cur = cur[part]
        if cur != v:
            fail(f'ffai-v4.js check: {k} is {cur!r}, expected {v!r}')


def chg_words(p):
    """'down 9.5%' / 'up 2.0%' / 'unchanged' for a percent change."""
    if p is None:
        return None
    return 'unchanged' if abs(p) < 0.05 else f"{'up' if p > 0 else 'down'} {abs(p):.1f}%"


def headline_text(d):
    """The one-line headline, built once here. The page, og:title, meta description and badge use it."""
    h = d['headline']
    q, y = parse_q(d['quarter'])
    yq, yy = parse_q(h['year_ago_quarter']) if h.get('year_ago_quarter') else (None, None)
    yr = f" from Q{yq} {yy}" if yq else ''
    lead = f"Farm prices received vs prices paid, Q{q} {y}: {h['ratio']:.1f} (2011 = 100)"
    if h.get('ratio_yoy_pct') is not None:
        lead += f", {chg_words(h['ratio_yoy_pct'])}{yr}"
    return lead


def draw_og(path, d):
    from PIL import Image, ImageDraw, ImageFont
    try:
        import matplotlib
        fd = os.path.join(matplotlib.get_data_path(), 'fonts', 'ttf')
    except Exception:
        fd = '/usr/share/fonts/truetype/dejavu'
    F = lambda n, s: ImageFont.truetype(os.path.join(fd, n), s)
    BG, GRN, INK, ORANGE, GREY, SUB = '#f5f5f0', '#2d6a2e', '#1a1a1a', '#d97218', '#999999', '#555555'
    im = Image.new('RGB', (1200, 630), BG); dr = ImageDraw.Draw(im)
    dr.rectangle([0, 0, 1199, 6], fill=GRN); dr.rectangle([0, 623, 1199, 629], fill=GRN)
    h = d['headline']; q, y = parse_q(d['quarter'])
    dr.text((60, 52), f'FFAI v4  |  U.S. FARM PRICES RECEIVED vs PAID  |  Q{q} {y}', font=F('DejaVuSansMono-Bold.ttf', 24), fill=GRN)
    big = F('DejaVuSans-Bold.ttf', 96)
    dr.text((60, 100), f"{h['ratio']:.1f}", font=big, fill=INK)
    w = dr.textlength(f"{h['ratio']:.1f}", font=big)
    dr.text((60 + w + 30, 118), 'ratio, 2011 = 100', font=F('DejaVuSans.ttf', 26), fill=SUB)
    if h.get('ratio_yoy_pct') is not None:
        yq, yy = parse_q(h['year_ago_quarter'])
        col = '#2d6a2e' if h['ratio_yoy_pct'] > 0 else '#a63030'
        dr.text((60 + w + 30, 156), f"{chg_words(h['ratio_yoy_pct'])} from Q{yq} {yy} ({h['year_ago_ratio']:.1f})",
                font=F('DejaVuSans-Bold.ttf', 30), fill=col)
    dr.rectangle([60, 236, 560, 239], fill=ORANGE)
    lab = h['label']
    dr.text((60, 262), f"Score {h['score']:.0f} of 100:  {lab} vs {BASE_TXT}", font=F('DejaVuSans-Bold.ttf', 34), fill=colour(h['score']))
    dr.text((60, 318), f"Lower than {h['worse_than_base_pct']:.0f} of 100 quarters from {BASE_TXT}. A price position, not a farm income reading.",
            font=F('DejaVuSans.ttf', 21), fill=SUB)
    labf, val = F('DejaVuSans.ttf', 20), F('DejaVuSans-Bold.ttf', 34)
    for i, s in enumerate(('crops', 'livestock', 'dairy')):
        x = 60 + 300 * i; sv = d['sectors'][s]
        dr.text((x, 398), s.upper(), font=labf, fill=GREY)
        dr.text((x, 426), f"{sv['ratio']:.1f}", font=val, fill=INK)
        dr.text((x, 470), f"{sv['label']} ({sv['score']:.0f})", font=F('DejaVuSans-Bold.ttf', 18), fill=colour(sv['score']))
    dr.text((60, 562), 'farmers1st.com', font=F('DejaVuSansMono-Bold.ttf', 26), fill=GRN)
    dr.text((400, 567), f"USDA NASS prices received / paid  |  {d['published_month']}", font=F('DejaVuSans.ttf', 20), fill=GREY)
    im.save(path, optimize=True)


def sub1(text, pattern, repl, what):
    new, n = re.subn(pattern, repl, text, count=1)
    if n != 1:
        fail(f'could not update {what}')
    return new


def main():
    args = sys.argv[1:]
    today = datetime.now(timezone.utc).date()
    if '--today' in args:
        i = args.index('--today'); today = date.fromisoformat(args[i + 1]); del args[i:i + 2]
    hist, summ, method, det, rows = load()
    last, prev = hist[-1], hist[-2]
    # Same quarter and same numbers as what is already published: keep the old dates,
    # so a re-run does not reset "published" or push back the stale-data banner.
    gen_keep = None
    revised = []
    try:
        oc = json.load(open(os.path.join(ROOT, 'api', 'v4', 'current.json'), encoding='utf-8'))
        oh = json.load(open(os.path.join(ROOT, 'api', 'v4', 'history.json'), encoding='utf-8'))
        new_q = [{'quarter': h['quarter'], 'ratio': h['all'], 'score': h['all_score']} for h in hist]
        old_q = [{'quarter': h['quarter'], 'ratio': h['ratio'], 'score': h['score']} for h in oh['quarters']]
        revised = revisions(oh['quarters'], hist)
        if oc.get('quarter') == last['quarter'] and new_q == old_q and oc.get('generated'):
            gen_keep = oc['generated']
            today = date.fromisoformat(gen_keep[:10])
            print(f'No new data since {gen_keep}; keeping the published date.')
    except (OSError, ValueError, KeyError):
        pass
    qn, yr = parse_q(last['quarter'])
    due = quarter_end(next_label(last['quarter'])) + timedelta(days=35)  # NASS posts a month's prices about a month later
    a = det[method]
    ci = {t: fisher_ci(a[t].get('r'), a[t].get('eff_n')) for t in ('T1', 'T2')}
    reach = {s: to_reach(base_ratios(rows, s), float(rows[-1][f'{s}_ratio'])) for s in SECT}
    raw = {r['quarter']: r for r in rows}  # unrounded engine values, for percent changes
    yago = hist[-5] if len(hist) >= 5 else None
    if yago and qkey(last['quarter']) - qkey(yago['quarter']) != 4:
        fail(f'year-ago quarter {yago["quarter"]} is not four quarters before {last["quarter"]}')

    def rchg(s, other):
        """Percent change in sector s's ratio from quarter `other` to the latest, from unrounded values."""
        return pct(raw[last['quarter']].get(f'{s}_ratio'), raw[other['quarter']].get(f'{s}_ratio')) if other else None

    lab = regime(last['all_score'])
    headline = {'ratio': last['all'], 'score': last['all_score'], 'label': lab, 'regime': lab, 'label_vs': BASE_TXT,
                'label_legacy': L.label_legacy(last['all_score']),
                'year_ago_quarter': yago and yago['quarter'], 'year_ago_score': yago and yago['all_score'],
                'year_ago_ratio': yago and yago['all'], 'ratio_yoy_pct': rchg('all', yago),
                'prev_ratio': prev['all'], 'prev_score': prev['all_score'], 'prev_quarter': prev['quarter'],
                'ratio_qoq_pct': rchg('all', prev),
                'pct_less_than_2011': r1(100 - last['all']), 'worse_than_base_pct': r1(100 - last['all_score']),
                'records': records(hist, 'all'), 'decade': decade(hist)}
    sectors = {s: {'ratio': last[s], 'score': last[f'{s}_score'], 'label': regime(last[f'{s}_score']),
                   'regime': regime(last[f'{s}_score']), 'label_legacy': L.label_legacy(last[f'{s}_score']),
                   'year_ago_ratio': yago and yago[s], 'year_ago_score': yago and yago[f'{s}_score'], 'ratio_yoy_pct': rchg(s, yago),
                   'prev_ratio': prev[s], 'prev_score': prev[f'{s}_score'], 'ratio_qoq_pct': rchg(s, prev),
                   'records': records(hist, s)}
               for s in ('crops', 'livestock', 'dairy')}
    drivers = [{'item': DRIVER_NAME.get(k, k), **v, 'missing': v.get('qoq_pct') is None,
                'not_updated': v.get('qoq_pct') is not None and abs(v['qoq_pct']) < 0.05} for k, v in summ['drivers'].items()]
    # Chart: the label lines for all farms (the band between 25 and 75 is the middle half of 1995-2019).
    lines = {t['label']: t['ratio'] for t in reach['all']}
    chart = {'band_low': lines['BELOW MIDDLE'], 'band_mid': lines['ABOVE MIDDLE'], 'band_high': lines['HIGH'],
             'base_from': "Q1'95", 'base_to': "Q4'19", 'first_live': FIRST_LIVE}
    data = {
        'version': '4.1', 'quarter': last['quarter'], 'date': f'Q{qn} {yr}', 'months': f'{MONTHS[qn - 1]} {yr}',
        'published': f'{today.strftime("%B")} {today.day}, {today.year}', 'publishedISO': today.isoformat(),
        'published_month': today.strftime('%B %Y'),
        'nextUpdate': f"{due.strftime('%b').upper()} '{due.year % 100:02d}", 'nextUpdateISO': due.isoformat(),
        'method': method, 'base': BASE, 'validated': bool(summ.get('validated')),
        'labels': [{'label': n, 'range': L.RANGES[n]} for n in L.NAMES],
        'validation': {'T1_r': a['T1']['r'], 'T1_years': a['T1']['n_years'], 'T2_r': a['T2']['r'],
                       'T3_model': a['T3']['rmse_model'], 'T3_no_change': a['T3']['rmse_no_change'],
                       'T3_last_year': a['T3']['rmse_last_year'], 'T3_years': a['T3']['test_years'],
                       'T1_eff_n': a['T1'].get('eff_n'), 'T1_ci': ci['T1'], 'T2_ci': ci['T2'],
                       'T1_pass': bool(summ['tests'][method]['T1']), 'T2_pass': bool(summ['tests'][method]['T2']),
                       'T3_pass': bool(summ['tests'][method]['T3'])},
        'headline': headline, 'sectors': sectors, 'drivers': drivers, 'farm_prices': summ['farm_prices'],
        'to_reach': reach, 'dairy_cost_check': summ.get('dairy_cost_check'), 'chart': chart,
        # [quarter, all, crops, livestock, dairy, all score, all label, real_time]
        'history': [[h['quarter'], h['all'], h['crops'], h['livestock'], h['dairy'], h['all_score'],
                     regime(h['all_score']), is_real_time(h['quarter'])] for h in hist],
    }
    headline['text'] = headline_text(data)
    js = ('// FFAI v4 numbers. Written by tools/ffai_v4_publish.py from engine/v4/ output.\n'
          '// Do not edit by hand; commentary is in ffai-commentary.js.\n'
          'var FFAI4 = ' + json.dumps(data, ensure_ascii=False, indent=1) + ';\n')
    check_js(js, {'quarter': last['quarter'], 'headline.score': last['all_score'], 'headline.ratio': last['all'],
                  'headline.label': lab})
    open(os.path.join(ROOT, 'ffai-v4.js'), 'w', encoding='utf-8').write(js)

    now = gen_keep or datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    api = os.path.join(ROOT, 'api', 'v4'); os.makedirs(api, exist_ok=True)
    common = {'source': 'https://farmers1st.com', 'api_docs': 'https://farmers1st.com/api/', 'license': 'CC BY 4.0'}
    current = {'ffai_version': '4.1', 'generated': now, 'quarter': last['quarter'], 'date': last['date'],
               'headline': headline['text'],
               'ratio': last['all'],
               'year_ago': yago and {'quarter': yago['quarter'], 'score': yago['all_score'], 'ratio': yago['all'],
                                     'label': regime(yago['all_score'])},
               'ratio_change_vs_year_ago_pct': headline['ratio_yoy_pct'],
               'score': last['all_score'], 'label': lab, 'label_vs': BASE_TXT,
               'regime': lab, 'label_legacy': L.label_legacy(last['all_score']),
               'previous': {'quarter': prev['quarter'], 'score': prev['all_score'], 'ratio': prev['all']},
               'ratio_change_vs_previous_pct': headline['ratio_qoq_pct'],
               'ratio_change_vs_previous_note': 'partly seasonal; compare with the same quarter a year earlier first',
               'vs_previous_10yr_avg_pct': (decade(hist) or {}).get('pct'),
               'sectors': {s: {'ratio': last[s], 'score': last[f'{s}_score'], 'label': regime(last[f'{s}_score']),
                               'regime': regime(last[f'{s}_score']), 'label_legacy': L.label_legacy(last[f'{s}_score']),
                               'year_ago_ratio': yago and yago[s], 'ratio_change_vs_year_ago_pct': rchg(s, yago)}
                           for s in ('crops', 'livestock', 'dairy')},
               'to_reach': {s: [{k: t[k] for k in ('label', 'regime', 'score', 'ratio', 'move_pct')} for t in reach[s]] for s in SECT},
               'label_lines': dict(L.RANGES), 'regime_thresholds': dict(L.RANGES),
               'label_legacy_thresholds': dict(L.LEGACY_RANGES),
               'label_meaning': f'Where the ratio of prices received to prices paid sits against the {BASE_TXT} quarters. '
                                'A LOW reading means farm prices buy less of what farms pay for than in most of those quarters. '
                                'It does not by itself mean farm income is low: yields, volumes sold and government payments are not in it.',
               'next_update': f'{due.year}-{due.month:02d}', **common}
    fields = ['quarter', 'date', 'ratio', 'score', 'crops_ratio', 'crops_score', 'livestock_ratio',
              'livestock_score', 'dairy_ratio', 'dairy_score', 'label', 'real_time']
    history = {'ffai_version': '4.1', 'generated': now, 'count': len(hist), 'frequency': 'quarterly',
               'start': hist[0]['quarter'], 'end': last['quarter'], 'first_real_time': FIRST_LIVE,
               'real_time_note': f'real_time is true only for quarters scored live, from {FIRST_LIVE} (the v4 launch, Oct 7, 2026) on. '
                                 'Earlier quarters were back-filled; 1995-2019 are also in-sample, ranked against a period that includes later quarters.',
               'fields': fields,
               'quarters': [{'quarter': h['quarter'], 'date': h['date'], 'ratio': h['all'], 'score': h['all_score'],
                             **{f'{s}_{k}': h[s if k == 'ratio' else f'{s}_score'] for s in ('crops', 'livestock', 'dairy') for k in ('ratio', 'score')},
                             'label': regime(h['all_score']), 'real_time': is_real_time(h['quarter'])}
                            for h in hist], **common}
    meta = {'ffai_version': '4.1', 'generated': now, 'name': 'Farmers First Ag Index v4',
            'description': 'National ratio of prices farms receive to prices farms pay (USDA NASS indexes, 2011 = 100), '
                           'scored as a percentile of the 1995-2019 quarters.',
            'ratios': {'all': 'COMMODITY TOTALS received / PPITW paid (matches USDA\'s published ratio within about one point)', 'crops': 'CROP TOTALS received / CROP SECTOR paid',
                       'livestock': 'LIVESTOCK TOTALS received / ANIMAL SECTOR paid', 'dairy': 'DAIRY PRODUCT TOTALS received / ANIMAL SECTOR paid (the animal-sector cost index includes feeder cattle and replacement cows bought)'},
            'score': 'share of 1995-2019 quarters at or below this quarter\'s ratio, 0-100', 'base_period': '1995-2019',
            'labels': {'lines': dict(L.RANGES),
                       'meaning': 'The label says where the ratio sits against the 1995-2019 quarters, split at their quartiles. '
                                  'It describes prices received against prices paid, not farm income. Show it with "vs 1995-2019".',
                       'legacy': 'Until Oct 2026 the labels were STRESSED (0-40), GUARDED (40-55), FAVORABLE (55-70) and STRONG (70-100). '
                                 'They were never tested and read STRESSED in every quarter from 2020, so they were replaced. '
                                 'The old label is still published as label_legacy.'},
            'comparisons': 'The main comparison is the same quarter a year earlier. Quarter-to-quarter changes are partly seasonal.',
            'real_time': history['real_time_note'],
            'quarter_rule': 'average of 3 months; a quarter is published only when all 3 months of both sides are out',
            'validation': {'preregistered_in': 'engine/ffai_v4.py (git commit 163cc4b, before the first validation run)',
                           'target': 'year-over-year change in USDA net farm income (FRED B1448C1A027NBEA) deflated by CPI',
                           'method_used': method, 'results': pfmt(det), 'validated': bool(summ.get('validated')),
                           'r_95pct_range': {'T1': ci['T1'], 'T2': ci['T2'], 'how': 'Fisher z with the effective sample size'},
                           'tests_run': multiple_tests(summ['tests'], det),
                           'scope': 'year-over-year changes in the all-farms ratio; the 0-100 score level, the labels and the sector scores were not tested',
                           'same_year_only': 'the relationship is within the same year; it is not a forecast',
                           'headline_lock': 'A and B both passed 3/3; by the pre-registered tie rule A was chosen, and the engine was then set to keep A (HEADLINE_METHOD) so a later run cannot switch it',
                           'note': 'the latest year of net farm income is a USDA forecast and can be revised',
                           'not_claimed': 'no relationship with national farm loan delinquency (r about 0)'},
            'limitations': ['Prices only: yields, volumes and government payments are not in the ratio.',
                            'The ratio declined about 1.2 points a year over 1995-2019, consistent with rising yields; scores against 1995-2019 therefore run low in most recent years. LOW means low against that period, not low income.',
                            'Scores for 1995-2019 are ranked against the whole period, including later years; they are not what a reader would have seen at the time (real_time is false for them).',
                            'The quarterly ratio is seasonal; compare with the same quarter a year earlier.',
                            'Prices paid includes household living costs as well as farm inputs.',
                            'Interest, cash rent, seed and taxes are updated by USDA once a year; the wage index has not changed since April 2025.',
                            'The latest month of prices received is preliminary and is revised the following month.'],
            'sources': ['USDA NASS Quick Stats, Agricultural Prices', 'FRED (validation only)'], **common}
    meta['fields_stable'] = ('Fields in current.json, history.json and history.csv keep their names within v4; new fields may be added. '
                             'A change in meaning gets a new version number. '
                             'Version 4.1 (Oct 2026): the label values changed. regime now carries the new label '
                             '(LOW 0-25, BELOW MIDDLE 25-50, ABOVE MIDDLE 50-75, HIGH 75-100, vs 1995-2019) and equals label; '
                             'the old value (STRESSED / GUARDED / FAVORABLE / STRONG) is in label_legacy, with its lines in label_legacy_thresholds. '
                             'to_reach entries use the new lines (25, 50, 75) and carry both label and regime. '
                             'Added: headline, label, label_vs, ratio_change_vs_year_ago_pct, ratio_change_vs_previous_pct, sector year-ago fields, '
                             'and label and real_time in history.json and history.csv (as the last two CSV columns). '
                             'score, ratio and every other field are unchanged.')
    for n, o in (('current.json', current), ('history.json', history), ('meta.json', meta)):
        with open(os.path.join(api, n), 'w', encoding='utf-8') as f:
            json.dump(o, f, indent=2, ensure_ascii=False, allow_nan=False); f.write('\n')
    with open(os.path.join(api, 'history.csv'), 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerow(history['fields'])
        for h in history['quarters']:
            w.writerow(['' if h[k] is None else ('true' if h[k] is True else 'false' if h[k] is False else h[k]) for k in history['fields']])

    draw_og(os.path.join(ROOT, 'og-share.png'), data)

    ip = os.path.join(ROOT, 'index.html'); html = open(ip, encoding='utf-8').read()
    s = last['all_score']
    yq = parse_q(yago['quarter']) if yago else None
    yoy = headline['ratio_yoy_pct']
    yoy_txt = f", {chg_words(yoy)} from Q{yq[0]} {yq[1]}" if yago and yoy is not None else ''
    short = f'{last["all"]:.1f}{yoy_txt}'
    ratio_txt = f'{last["all"]:.1f} (2011 = 100){yoy_txt}'
    html = sub1(html, r'<meta name="description" content="FFAI Q\d \d{4}: [^"]*">',
                f'<meta name="description" content="FFAI Q{qn} {yr}: ratio of U.S. farm prices received to prices paid {ratio_txt}. '
                f'Score {s:.0f} of 100, {lab} vs {BASE_TXT}. Free quarterly index plus crop insurance in WI &amp; MN. 715-797-2428.">', 'meta description')
    html = sub1(html, r'<meta property="og:title" content="FFAI [^"]*">',
                f'<meta property="og:title" content="FFAI Q{qn} {yr}: farm price ratio {short} | Farmers First Ag Index">', 'og:title')
    html = sub1(html, r'<meta name="twitter:title" content="FFAI [^"]*">',
                f'<meta name="twitter:title" content="FFAI Q{qn} {yr}: farm price ratio {short}">', 'twitter:title')
    html = sub1(html, r'"headline":"FFAI v4: [^"]*","author"', f'"headline":"FFAI v4: Q{qn} {yr} farm price ratio {short}","author"', 'article headline')
    pub = today.isoformat()
    tag = f'Q{qn}-{yr % 100:02d}'
    html = sub1(html, r'"datePublished":"[0-9-]+","dateModified":"[0-9-]+","image":"[^"]*"',
                f'"datePublished":"{pub}","dateModified":"{pub}","image":"https://farmers1st.com/og-share.png?q={tag}"', 'article dates')
    desc = (f'Q{qn} {yr}: ratio of prices U.S. farms receive to prices they pay {ratio_txt} (USDA). '
            f'Score {s:.0f} of 100, {lab} vs {BASE_TXT}: a price position, not an income reading. Crops, livestock and dairy too. Free, quarterly.')
    html = sub1(html, r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{desc}">', 'og:description')
    html = sub1(html, r'<meta name="twitter:description" content="[^"]*">', f'<meta name="twitter:description" content="{desc}">', 'twitter:description')
    html = sub1(html, r'<meta property="og:image" content="[^"]*">', f'<meta property="og:image" content="https://farmers1st.com/og-share.png?q={tag}">', 'og:image')
    html = sub1(html, r'<meta name="twitter:image" content="[^"]*">', f'<meta name="twitter:image" content="https://farmers1st.com/og-share.png?q={tag}">', 'twitter:image')
    open(ip, 'w', encoding='utf-8').write(html)

    sp = os.path.join(ROOT, 'sitemap.xml'); sm = open(sp, encoding='utf-8').read()
    sm = sub1(sm, r'(<loc>https://farmers1st\.com/</loc><lastmod>)[0-9-]+(</lastmod>)', rf'\g<1>{pub}\g<2>', 'sitemap lastmod')
    open(sp, 'w', encoding='utf-8').write(sm)

    def ych(x):
        return 'n/a' if x is None else f'{x:+.1f}%'
    md = [f'### FFAI v4 published data: {last["quarter"]}', '',
          headline['text'], '',
          f'All farms: ratio {last["all"]} (2011 = 100), vs {yago["quarter"] if yago else "n/a"} {ych(yoy)}; '
          f'score {s:.0f}, {lab} vs {BASE_TXT} (vs {prev["quarter"]}: ratio {ych(headline["ratio_qoq_pct"])}, partly seasonal)', '',
          '| Sector | Ratio | vs a year ago | Score | Label (vs 1995-2019) |', '|---|---|---|---|---|'] + \
         [f'| {LABEL[x]} | {last[x]} | {ych(rchg(x, yago))} | {last[f"{x}_score"]:.0f} | {regime(last[f"{x}_score"])} |' for x in SECT] + \
         ['', 'Wrote ffai-v4.js, api/v4/*.json, api/v4/history.csv, og-share.png, index.html meta, sitemap.xml lastmod.'] + \
         (['', f'USDA revised {len(revised)} past quarter(s):'] + [f'- {x}' for x in revised] if revised else [])
    print('\n'.join(md))
    p = os.environ.get('GITHUB_STEP_SUMMARY')
    if p:
        open(p, 'a', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()

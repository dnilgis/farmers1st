#!/usr/bin/env python3
"""
Write FFAI v4 engine output into the website.

    python tools/ffai_v4_publish.py [--today 2026-10-07]

Reads   engine/v4/ffai_v4_quarterly.csv, engine/v4/ffai_v4_summary.json
Writes  ffai-v4.js            numbers the page reads (never the commentary)
        api/v4/current.json   latest quarter
        api/v4/history.json   every quarter since Q1 1995
        api/v4/meta.json      method and validation results
        og-share.png          share image
        index.html            meta description, og:title, twitter:title
Commentary lives in ffai-commentary.js and is written by hand.

Refuses to write anything if a ratio is not positive, a score is outside
0-100, quarters are not consecutive, history got shorter, or the engine did
not record its validation results.
"""
import csv, json, math, os, re, subprocess, sys, tempfile
from datetime import date, datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V4 = os.path.join(ROOT, 'engine', 'v4')
SECT = ('all', 'crops', 'livestock', 'dairy')
LABEL = {'all': 'All farms', 'crops': 'Crops', 'livestock': 'Livestock', 'dairy': 'Dairy'}
BASE = '1995–2019'


def fail(msg):
    print(f'REFUSED: {msg}')
    p = os.environ.get('GITHUB_STEP_SUMMARY')
    if p:
        open(p, 'a', encoding='utf-8').write(f'### FFAI v4 publish refused\n\n{msg}\n')
    sys.exit(1)


def regime(v):
    return 'STRONG' if v >= 70 else 'FAVORABLE' if v >= 55 else 'GUARDED' if v >= 40 else 'STRESSED'


def colour(v):
    return '#2d6a2e' if v >= 55 else '#b8860b' if v >= 40 else '#a63030'


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
    old = os.path.join(ROOT, 'api', 'v4', 'history.json')
    if os.path.exists(old):
        n_old = json.load(open(old)).get('count', 0)
        if len(hist) < n_old:
            fail(f'history would shrink from {n_old} to {len(hist)} quarters')
    return hist, summ, method, det


def records(hist, s):
    vals = [(h[s], h['quarter']) for h in hist if h[s] is not None]
    lo, hi = min(vals), max(vals)
    base = [h[s] for h in hist if h[s] is not None and 1995 <= parse_q(h['quarter'])[1] <= 2019]
    return {'low': lo[0], 'low_q': lo[1], 'high': hi[0], 'high_q': hi[1],
            'base_min': min(base), 'base_max': max(base)}


TRAIL = 40  # quarters; matches engine candidate B


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


def draw_og(path, d):
    from PIL import Image, ImageDraw, ImageFont
    try:
        import matplotlib
        fd = os.path.join(matplotlib.get_data_path(), 'fonts', 'ttf')
    except Exception:
        fd = '/usr/share/fonts/truetype/dejavu'
    F = lambda n, s: ImageFont.truetype(os.path.join(fd, n), s)
    BG, GRN, INK, ORANGE, GREY, SUB = '#f5f5f0', '#2d6a2e', '#1a1a1a', '#d97218', '#999999', '#777777'
    im = Image.new('RGB', (1200, 630), BG); dr = ImageDraw.Draw(im)
    dr.rectangle([0, 0, 1199, 6], fill=GRN); dr.rectangle([0, 623, 1199, 629], fill=GRN)
    dr.text((60, 52), 'FFAI v4', font=F('DejaVuSansMono-Bold.ttf', 26), fill=GRN)
    h = d['headline']; big = F('DejaVuSans-Bold.ttf', 70)
    dr.text((60, 108), f"{h['score']:.0f}", font=big, fill=colour(h['score']))
    w = dr.textlength(f"{h['score']:.0f}", font=big)
    dr.text((60 + w + 40, 140), h['regime'], font=F('DejaVuSans-Bold.ttf', 34), fill=colour(h['score']))
    dr.rectangle([60, 210, 560, 213], fill=ORANGE)
    t = F('DejaVuSans-Bold.ttf', 34)
    dr.text((60, 234), 'U.S. farm prices vs farm costs', font=t, fill=INK)
    q, y = parse_q(d['quarter'])
    dr.text((60, 290), f"Q{q} {y}  |  Prices buy {h['pct_less_than_2011']:.1f}% less than in 2011", font=F('DejaVuSans.ttf', 22), fill=SUB)
    dr.text((60, 324), f"Lower than {h['worse_than_base_pct']:.0f} of 100 quarters, {BASE}", font=F('DejaVuSans.ttf', 22), fill=SUB)
    lab, val = F('DejaVuSans.ttf', 20), F('DejaVuSans-Bold.ttf', 34)
    for i, s in enumerate(('crops', 'livestock', 'dairy')):
        x = 60 + 200 * i; v = d['sectors'][s]['score']
        dr.text((x, 403), s.upper(), font=lab, fill=GREY)
        dr.text((x, 432), f'{v:.0f}', font=val, fill=colour(v))
    dr.text((60, 562), 'farmers1st.com', font=F('DejaVuSansMono-Bold.ttf', 26), fill=GRN)
    dr.text((400, 567), f"USDA prices received / paid  |  {d['published_month']}", font=F('DejaVuSans.ttf', 20), fill=GREY)
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
    hist, summ, method, det = load()
    last, prev = hist[-1], hist[-2]
    # Same quarter and same numbers as what is already published: keep the old dates,
    # so a re-run does not reset "published" or push back the stale-data banner.
    gen_keep = None
    try:
        oc = json.load(open(os.path.join(ROOT, 'api', 'v4', 'current.json'), encoding='utf-8'))
        oh = json.load(open(os.path.join(ROOT, 'api', 'v4', 'history.json'), encoding='utf-8'))
        new_q = [{'quarter': h['quarter'], 'ratio': h['all'], 'score': h['all_score']} for h in hist]
        old_q = [{'quarter': h['quarter'], 'ratio': h['ratio'], 'score': h['score']} for h in oh['quarters']]
        if oc.get('quarter') == last['quarter'] and new_q == old_q and oc.get('generated'):
            gen_keep = oc['generated']
            today = date.fromisoformat(gen_keep[:10])
            print(f'No new data since {gen_keep}; keeping the published date.')
    except (OSError, ValueError, KeyError):
        pass
    qn, yr = parse_q(last['quarter'])
    due = quarter_end(next_label(last['quarter'])) + timedelta(days=35)  # NASS posts a month's prices about a month later
    a = det[method]
    headline = {'ratio': last['all'], 'score': last['all_score'], 'regime': regime(last['all_score']),
                'prev_ratio': prev['all'], 'prev_score': prev['all_score'], 'prev_quarter': prev['quarter'],
                'pct_less_than_2011': r1(100 - last['all']), 'worse_than_base_pct': r1(100 - last['all_score']),
                'records': records(hist, 'all'), 'decade': decade(hist)}
    sectors = {s: {'ratio': last[s], 'score': last[f'{s}_score'], 'regime': regime(last[f'{s}_score']),
                   'prev_ratio': prev[s], 'prev_score': prev[f'{s}_score'], 'records': records(hist, s)}
               for s in ('crops', 'livestock', 'dairy')}
    drivers = [{'item': DRIVER_NAME.get(k, k), **v, 'not_updated': abs(v['qoq_pct']) < 0.05} for k, v in summ['drivers'].items()]
    data = {
        'version': '4.0', 'quarter': last['quarter'], 'date': f'Q{qn} {yr}', 'months': f'{MONTHS[qn - 1]} {yr}',
        'published': f'{today.strftime("%B")} {today.day}, {today.year}', 'publishedISO': today.isoformat(),
        'published_month': today.strftime('%B %Y'),
        'nextUpdate': f"{due.strftime('%b').upper()} '{due.year % 100:02d}", 'nextUpdateISO': due.isoformat(),
        'method': method, 'base': BASE, 'validated': bool(summ.get('validated')),
        'validation': {'T1_r': a['T1']['r'], 'T1_years': a['T1']['n_years'], 'T2_r': a['T2']['r'],
                       'T3_model': a['T3']['rmse_model'], 'T3_no_change': a['T3']['rmse_no_change'],
                       'T3_last_year': a['T3']['rmse_last_year'], 'T3_years': a['T3']['test_years'],
                       'T1_pass': bool(summ['tests'][method]['T1']), 'T2_pass': bool(summ['tests'][method]['T2']),
                       'T3_pass': bool(summ['tests'][method]['T3'])},
        'headline': headline, 'sectors': sectors, 'drivers': drivers, 'farm_prices': summ['farm_prices'],
        'history': [[h['quarter'], h['all'], h['crops'], h['livestock'], h['dairy'], h['all_score']] for h in hist],
    }
    js = ('// FFAI v4 numbers. Written by tools/ffai_v4_publish.py from engine/v4/ output.\n'
          '// Do not edit by hand; commentary is in ffai-commentary.js.\n'
          'var FFAI4 = ' + json.dumps(data, ensure_ascii=False, indent=1) + ';\n')
    check_js(js, {'quarter': last['quarter'], 'headline.score': last['all_score'], 'headline.ratio': last['all']})
    open(os.path.join(ROOT, 'ffai-v4.js'), 'w', encoding='utf-8').write(js)

    now = gen_keep or datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    api = os.path.join(ROOT, 'api', 'v4'); os.makedirs(api, exist_ok=True)
    common = {'source': 'https://farmers1st.com', 'api_docs': 'https://farmers1st.com/api/', 'license': 'CC BY 4.0'}
    current = {'ffai_version': '4.0', 'generated': now, 'quarter': last['quarter'], 'date': last['date'],
               'score': last['all_score'], 'regime': regime(last['all_score']), 'ratio': last['all'],
               'vs_previous_10yr_avg_pct': (decade(hist) or {}).get('pct'),
               'sectors': {s: {'ratio': last[s], 'score': last[f'{s}_score'], 'regime': regime(last[f'{s}_score'])}
                           for s in ('crops', 'livestock', 'dairy')},
               'previous': {'quarter': prev['quarter'], 'score': prev['all_score'], 'ratio': prev['all']},
               'regime_thresholds': {'STRONG': '70-100', 'FAVORABLE': '55-70', 'GUARDED': '40-55', 'STRESSED': '0-40'},
               'next_update': f'{due.year}-{due.month:02d}', **common}
    history = {'ffai_version': '4.0', 'generated': now, 'count': len(hist), 'frequency': 'quarterly',
               'start': hist[0]['quarter'], 'end': last['quarter'],
               'fields': ['quarter', 'date', 'ratio', 'score', 'crops_ratio', 'crops_score', 'livestock_ratio',
                          'livestock_score', 'dairy_ratio', 'dairy_score'],
               'quarters': [{'quarter': h['quarter'], 'date': h['date'], 'ratio': h['all'], 'score': h['all_score'],
                             **{f'{s}_{k}': h[s if k == 'ratio' else f'{s}_score'] for s in ('crops', 'livestock', 'dairy') for k in ('ratio', 'score')}}
                            for h in hist], **common}
    meta = {'ffai_version': '4.0', 'generated': now, 'name': 'Farmers First Ag Index v4',
            'description': 'National ratio of prices farms receive to prices farms pay (USDA NASS indexes, 2011 = 100), '
                           'scored as a percentile of the 1995-2019 quarters.',
            'ratios': {'all': 'COMMODITY TOTALS received / PPITW paid (matches USDA\'s published ratio within about one point)', 'crops': 'CROP TOTALS received / CROP SECTOR paid',
                       'livestock': 'LIVESTOCK TOTALS received / ANIMAL SECTOR paid', 'dairy': 'DAIRY PRODUCT TOTALS received / ANIMAL SECTOR paid (the animal-sector cost index includes feeder cattle and replacement cows bought)'},
            'score': 'share of 1995-2019 quarters at or below this quarter\'s ratio, 0-100', 'base_period': '1995-2019',
            'quarter_rule': 'average of 3 months; a quarter is published only when all 3 months of both sides are out',
            'validation': {'preregistered_in': 'engine/ffai_v4.py (git commit 163cc4b, before the first validation run)',
                           'target': 'year-over-year change in USDA net farm income (FRED B1448C1A027NBEA) deflated by CPI',
                           'method_used': method, 'results': pfmt(det), 'validated': bool(summ.get('validated')),
                           'scope': 'year-over-year changes in the all-farms ratio; the 0-100 score level and the sector scores were not tested',
                           'same_year_only': 'the relationship is within the same year; it is not a forecast',
                           'headline_lock': 'A and B both passed 3/3; by the pre-registered tie rule A was chosen, and the engine was then set to keep A (HEADLINE_METHOD) so a later run cannot switch it',
                           'note': 'the latest year of net farm income is a USDA forecast and can be revised',
                           'not_claimed': 'no relationship with national farm loan delinquency (r about 0)'},
            'limitations': ['Prices only: yields, volumes and government payments are not in the ratio.',
                            'The ratio declined about 1.2 points a year over 1995-2019, consistent with rising yields; scores against 1995-2019 therefore run low in most recent years. STRESSED means low against that period, not low income.',
                            'Scores for 1995-2019 are ranked against the whole period, including later years; they are not what a reader would have seen at the time.',
                            'Prices paid includes household living costs as well as farm inputs.',
                            'Interest, cash rent, seed and taxes are updated by USDA once a year; the wage index has not changed since April 2025.',
                            'The latest month of prices received is preliminary and is revised the following month.'],
            'sources': ['USDA NASS Quick Stats, Agricultural Prices', 'FRED (validation only)'], **common}
    for n, o in (('current.json', current), ('history.json', history), ('meta.json', meta)):
        with open(os.path.join(api, n), 'w', encoding='utf-8') as f:
            json.dump(o, f, indent=2, ensure_ascii=False); f.write('\n')

    draw_og(os.path.join(ROOT, 'og-share.png'), data)

    ip = os.path.join(ROOT, 'index.html'); html = open(ip, encoding='utf-8').read()
    s, rg = last['all_score'], regime(last['all_score'])
    html = sub1(html, r'<meta name="description" content="FFAI Q\d \d{4}: [^"]*">',
                f'<meta name="description" content="FFAI Q{qn} {yr}: {s:.0f} {rg}. U.S. farm prices buy {100 - last["all"]:.1f}% less of what farms pay for than in 2011. '
                f'Free quarterly index plus crop insurance in WI &amp; MN. 715-797-2428.">', 'meta description')
    html = sub1(html, r'<meta property="og:title" content="FFAI [^"]*">',
                f'<meta property="og:title" content="FFAI {s:.0f} {rg} — Farmers First Ag Index | Q{qn} {yr}">', 'og:title')
    html = sub1(html, r'<meta name="twitter:title" content="FFAI [^"]*">',
                f'<meta name="twitter:title" content="FFAI {s:.0f} {rg}">', 'twitter:title')
    html = sub1(html, r'"headline":"FFAI v4: [^"]*","author"', f'"headline":"FFAI v4: {s:.0f} {rg} — Q{qn} {yr}","author"', 'article headline')
    pub = today.isoformat()
    tag = f'Q{qn}-{yr % 100:02d}'
    html = sub1(html, r'"datePublished":"[0-9-]+","dateModified":"[0-9-]+","image":"[^"]*"',
                f'"datePublished":"{pub}","dateModified":"{pub}","image":"https://farmers1st.com/og-share.png?q={tag}"', 'article dates')
    desc = (f'Q{qn} {yr}: {s:.0f} {rg}. USDA prices U.S. farms receive vs prices they pay, 2011 = 100, '
            f'scored against 1995-2019. All farms plus crops, livestock and dairy. Free, quarterly.')
    html = sub1(html, r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{desc}">', 'og:description')
    html = sub1(html, r'<meta name="twitter:description" content="[^"]*">', f'<meta name="twitter:description" content="{desc}">', 'twitter:description')
    html = sub1(html, r'<meta property="og:image" content="[^"]*">', f'<meta property="og:image" content="https://farmers1st.com/og-share.png?q={tag}">', 'og:image')
    html = sub1(html, r'<meta name="twitter:image" content="[^"]*">', f'<meta name="twitter:image" content="https://farmers1st.com/og-share.png?q={tag}">', 'twitter:image')
    open(ip, 'w', encoding='utf-8').write(html)

    sp = os.path.join(ROOT, 'sitemap.xml'); sm = open(sp, encoding='utf-8').read()
    sm = sub1(sm, r'(<loc>https://farmers1st\.com/</loc><lastmod>)[0-9-]+(</lastmod>)', rf'\g<1>{pub}\g<2>', 'sitemap lastmod')
    open(sp, 'w', encoding='utf-8').write(sm)

    md = [f'### FFAI v4 published data: {last["quarter"]}', '',
          f'All farms: ratio {last["all"]} (2011 = 100), score {s:.0f} {rg} (prev {prev["all_score"]:.0f}, {prev["quarter"]})', '',
          '| Sector | Ratio | Score |', '|---|---|---|'] + \
         [f'| {LABEL[x]} | {last[x]} | {last[f"{x}_score"]:.0f} {regime(last[f"{x}_score"])} |' for x in SECT] + \
         ['', 'Wrote ffai-v4.js, api/v4/*.json, og-share.png, index.html meta, sitemap.xml lastmod.']
    print('\n'.join(md))
    p = os.environ.get('GITHUB_STEP_SUMMARY')
    if p:
        open(p, 'a', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()

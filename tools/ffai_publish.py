#!/usr/bin/env python3
"""
Write FFAI engine output into the website.

    python tools/ffai_publish.py engine/ffai_v3_historical.csv [--today 2026-10-06]

Run by .github/workflows/ffai-update.yml after engine/ffai_v3_engine.py.
Updates, from the engine CSV only:
    ffai-data.js          current quarter numbers + full history
                          (headline, signals, actions are NOT touched; the
                          page labels them with editorialQuarter)
    api/v3/current.json   current quarter
    api/v3/history.json   all scored quarters
    index.html            meta description, og:title, twitter:title
    og-share.png          share image
Prints a markdown summary (new quarter, revised quarters) and appends it to
$GITHUB_STEP_SUMMARY when that is set.

Refuses to write anything if a score is missing or outside 0-100, quarters
are not consecutive, or the history got shorter.

Outlook is computed by the engine but NOT published (withheld Oct 2026: over
2003-2026 a high Outlook score came before higher, not lower, loan
delinquency 4-5 quarters later; see engine/ffai_v3_validation.txt).
"""
import csv, json, math, os, re, sys
from datetime import date, datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIELDS = ('composite', 'grain', 'dairy', 'livestock')
OUTLOOK_NOTE = ('Withheld since Oct 2026: historically a high Outlook score came before higher, '
                'not lower, farm loan delinquency 4-5 quarters later.')


def fail(msg):
    print(f'REFUSED: {msg}')
    summary(f'### FFAI update refused\n\n{msg}\n')
    sys.exit(1)


def summary(md):
    p = os.environ.get('GITHUB_STEP_SUMMARY')
    if p:
        with open(p, 'a', encoding='utf-8') as f:
            f.write(md + '\n')


def regime(v):
    return 'STRONG' if v >= 70 else 'FAVORABLE' if v >= 55 else 'GUARDED' if v >= 40 else 'STRESSED'


def colour(v):  # same rule as index.html colHex()
    return '#2d6a2e' if v >= 55 else '#b8860b' if v >= 40 else '#a63030'


def parse_q(label):
    m = re.fullmatch(r"Q([1-4])'(\d\d)", label)
    if not m:
        fail(f'bad quarter label {label!r}')
    return int(m.group(1)), 2000 + int(m.group(2))


def q_start(label):
    q, y = parse_q(label)
    return date(y, 3 * q - 2, 1)


def next_label(label):
    q, y = parse_q(label)
    return f"Q1'{(y + 1) % 100:02d}" if q == 4 else f"Q{q + 1}'{y % 100:02d}"


def quarter_end(label):
    q, y = parse_q(label)
    return date(y + 1, 1, 1) - timedelta(days=1) if q == 4 else date(y, 3 * q + 1, 1) - timedelta(days=1)


def read_csv(path):
    with open(path, encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    out = []
    for r in rows:
        if not (r.get('composite') or '').strip():
            continue  # warm-up or incomplete quarter
        q = r['quarter'].strip()
        rec = {'quarter': q, 'date': (r.get('') or r.get('date') or q_start(q).isoformat()).strip()[:10]}
        for k in FIELDS:
            try:
                v = float(r.get(k, ''))
            except ValueError:
                fail(f'{q}: {k} is not a number')
            if not math.isfinite(v) or v < -0.05 or v > 100.05:
                fail(f'{q}: {k} = {v} is outside 0-100')
            rec[k] = round(min(max(v, 0.0), 100.0), 1)
        if rec['date'] != q_start(q).isoformat():
            fail(f'{q}: date {rec["date"]} does not match the quarter')
        out.append(rec)
    if len(out) < 2:
        fail('fewer than 2 scored quarters in the CSV')
    for a, b in zip(out, out[1:]):
        if next_label(a['quarter']) != b['quarter']:
            fail(f'quarters not consecutive: {a["quarter"]} then {b["quarter"]}')
    return out


def read_js_history(js):
    m = re.search(r'history: \[(.*?)\n  \],', js, re.S)
    if not m:
        fail('could not find history array in ffai-data.js')
    rows = re.findall(r'\["([^"]+)",([\d.]+),([\d.]+),([\d.]+),([\d.]+)\]', m.group(1))
    return [{'quarter': r[0], **{k: float(v) for k, v in zip(FIELDS, r[1:])}} for r in rows]


def set_field(js, key, value_js):
    # value is either a double-quoted string (may contain commas) or a bare token
    pat = re.compile(r'^(  ' + re.escape(key) + r':\s*)("(?:[^"\\\n]|\\.)*"|[^,\n"]*)(,)', re.M)
    if len(pat.findall(js)) != 1:
        fail(f'ffai-data.js: expected exactly one "{key}:" line')
    return pat.sub(lambda m: m.group(1) + value_js + m.group(3), js)


def check_js(js, expect):
    """Parse the new ffai-data.js with node (present on GitHub runners) and
    confirm the values the page will read. Refuse if node is missing."""
    import subprocess, tempfile
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f:
        f.write(js + '\nprocess.stdout.write(JSON.stringify(FFAI));\n')
        tmp = f.name
    try:
        out = subprocess.run(['node', tmp], capture_output=True, text=True, timeout=30)
    except FileNotFoundError:
        fail('node is not installed, cannot check ffai-data.js')
    finally:
        os.unlink(tmp)
    if out.returncode != 0:
        fail('new ffai-data.js does not parse: ' + out.stderr.strip().splitlines()[-1])
    got = json.loads(out.stdout)
    for k, v in expect.items():
        if got.get(k) != v:
            fail(f'ffai-data.js check: {k} is {got.get(k)!r}, expected {v!r}')


def sub1(text, pattern, repl, what):
    new, n = re.subn(pattern, repl, text, count=1)
    if n != 1:
        fail(f'could not update {what}')
    return new


def draw_og(path, cur):
    from PIL import Image, ImageDraw, ImageFont
    try:
        import matplotlib
        fd = os.path.join(matplotlib.get_data_path(), 'fonts', 'ttf')
    except Exception:
        fd = '/usr/share/fonts/truetype/dejavu'
    def font(name, size):
        return ImageFont.truetype(os.path.join(fd, name), size)
    BG, GRN, INK, ORANGE, GREY, SUB = '#f5f5f0', '#2d6a2e', '#1a1a1a', '#d97218', '#999999', '#777777'
    im = Image.new('RGB', (1200, 630), BG)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 1199, 6], fill=GRN)
    d.rectangle([0, 623, 1199, 629], fill=GRN)
    d.text((60, 52), 'FFAI v3.0', font=font('DejaVuSansMono-Bold.ttf', 26), fill=GRN)
    c = cur['composite']
    big = font('DejaVuSans-Bold.ttf', 70)
    d.text((60, 108), f'{c:.1f}', font=big, fill=colour(c))
    sw = d.textlength(f'{c:.1f}', font=big)
    d.text((60 + sw + 40, 140), regime(c), font=font('DejaVuSans-Bold.ttf', 34), fill=colour(c))
    d.rectangle([60, 210, 560, 213], fill=ORANGE)
    t = font('DejaVuSans-Bold.ttf', 34)
    d.text((60, 234), 'U.S. Agricultural Financial', font=t, fill=INK)
    d.text((60, 279), 'Conditions Index', font=t, fill=INK)
    q, y = parse_q(cur['quarter'])
    d.text((60, 342), f'Q{q} {y}  |  Internally tested  |  {cur["count"]} Quarters',
           font=font('DejaVuSans.ttf', 20), fill=SUB)
    lab, val = font('DejaVuSans.ttf', 20), font('DejaVuSans-Bold.ttf', 34)
    for i, k in enumerate(('grain', 'dairy', 'livestock')):
        x = 60 + 200 * i
        d.text((x, 403), k.upper(), font=lab, fill=GREY)
        d.text((x, 432), f'{cur[k]:.1f}', font=val, fill=colour(cur[k]))
    d.text((60, 562), 'farmers1st.com', font=font('DejaVuSansMono-Bold.ttf', 26), fill=GRN)
    d.text((400, 567), f'Chetek, WI  |  {cur["published"].strftime("%B %Y")}',
           font=font('DejaVuSans.ttf', 20), fill=GREY)
    im.save(path, optimize=True)


def main():
    args = sys.argv[1:]
    today = datetime.now(timezone.utc).date()
    if '--today' in args:
        i = args.index('--today'); today = date.fromisoformat(args[i + 1]); del args[i:i + 2]
    if len(args) != 1:
        print(__doc__); sys.exit(2)
    rows = read_csv(args[0])

    js_path = os.path.join(ROOT, 'ffai-data.js')
    js = open(js_path, encoding='utf-8').read()
    old = read_js_history(js)
    if len(rows) < len(old):
        fail(f'engine has {len(rows)} quarters, site has {len(old)}; history would shrink')

    oldmap = {r['quarter']: r for r in old}
    revised = [(r['quarter'], k, oldmap[r['quarter']][k], r[k]) for r in rows if r['quarter'] in oldmap
               for k in FIELDS if abs(oldmap[r['quarter']][k] - r[k]) >= 0.05]
    new_q = [r['quarter'] for r in rows if r['quarter'] not in oldmap]
    last, prev = rows[-1], rows[-2]

    md = [f'### FFAI engine output: latest scored quarter {last["quarter"]}', '',
          '| Quarter | Composite | Grain | Dairy | Livestock |', '|---|---|---|---|---|']
    for r in rows[-3:]:
        md.append(f'| {r["quarter"]} | {r["composite"]} {regime(r["composite"])} | {r["grain"]} | {r["dairy"]} | {r["livestock"]} |')
    md += ['', f'New quarters: {", ".join(new_q) or "none"}',
           f'Revised past values: {len(revised)}']
    for q, k, a, b in revised[:40]:
        md.append(f'- {q} {k}: {a} -> {b}')
    if len(revised) > 40:
        md.append(f'- ... and {len(revised) - 40} more')

    if not new_q and not revised:
        md.append('\nNothing new. Site files left unchanged.')
        print('\n'.join(md)); summary('\n'.join(md)); return

    # ---- ffai-data.js ----
    q, y = parse_q(last['quarter'])
    nxt = next_label(last['quarter'])
    due = quarter_end(nxt) + timedelta(days=21)
    js = set_field(js, 'quarter', f'"{last["quarter"]}"')
    js = set_field(js, 'date', f'"Q{q} {y}"')
    js = set_field(js, 'updated', f'"{today.strftime("%B")} {today.day}, {today.year}"')
    js = set_field(js, 'publishedISO', f'"{today.isoformat()}"')
    js = set_field(js, 'nextUpdate', f'"{due.strftime("%b").upper()} \'{due.year % 100:02d}"')
    js = set_field(js, 'composite', f'{last["composite"]}')
    js = set_field(js, 'prevComp', f'{prev["composite"]}')
    js = set_field(js, 'regime', f'"{regime(last["composite"])}"')
    for k, pk in (('grain', 'prevGrain'), ('dairy', 'prevDairy'), ('livestock', 'prevLivestock')):
        js = set_field(js, k, f'{last[k]}')
        js = set_field(js, pk, f'{prev[k]}')
    hist = ',\n'.join(f'    ["{r["quarter"]}",{r["composite"]},{r["grain"]},{r["dairy"]},{r["livestock"]}]' for r in rows)
    js = re.sub(r'(history: \[\n)(.*?)(\n  \],)', lambda m: m.group(1) + hist + m.group(3), js, count=1, flags=re.S)
    if read_js_history(js) != [{'quarter': r['quarter'], **{k: r[k] for k in FIELDS}} for r in rows]:
        fail('history did not round-trip in ffai-data.js')
    check_js(js, {'quarter': last['quarter'], 'composite': last['composite'], 'prevComp': prev['composite'],
                  'grain': last['grain'], 'dairy': last['dairy'], 'livestock': last['livestock']})
    open(js_path, 'w', encoding='utf-8').write(js)

    # ---- api/v3 ----
    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    apid = os.path.join(ROOT, 'api', 'v3')
    current = {
        'ffai_version': '3.0', 'generated': now, 'quarter': last['quarter'], 'date': last['date'],
        'composite': last['composite'], 'regime': regime(last['composite']),
        'sub_indexes': {k: last[k] for k in ('grain', 'dairy', 'livestock')},
        'outlook': None, 'outlook_note': OUTLOOK_NOTE,
        'previous': {'quarter': prev['quarter'], **{k: prev[k] for k in FIELDS}, 'outlook': None},
        'regimes': {**{k: regime(last[k]) for k in ('grain', 'dairy', 'livestock')}, 'outlook': None},
        'regime_thresholds': {'STRONG': '70-100', 'FAVORABLE': '55-70', 'GUARDED': '40-55', 'STRESSED': '0-40'},
        'next_update': f'{due.year}-{due.month:02d}',
        'source': 'https://farmers1st.com', 'api_docs': 'https://farmers1st.com/api/', 'license': 'CC BY 4.0',
    }
    history = {
        'ffai_version': '3.0', 'generated': now, 'count': len(rows), 'frequency': 'quarterly',
        'start': rows[0]['quarter'], 'end': last['quarter'],
        'fields': ['quarter', 'date', 'composite', 'grain', 'dairy', 'livestock'],
        'quarters': [{k: r[k] for k in ('quarter', 'date') + FIELDS} for r in rows],
        'source': 'https://farmers1st.com', 'api_docs': 'https://farmers1st.com/api/', 'license': 'CC BY 4.0',
    }
    for name, obj in (('current.json', current), ('history.json', history)):
        with open(os.path.join(apid, name), 'w', encoding='utf-8') as f:
            json.dump(obj, f, indent=2); f.write('\n')

    # ---- index.html meta ----
    ip = os.path.join(ROOT, 'index.html')
    html = open(ip, encoding='utf-8').read()
    c, g, dy, lv = last['composite'], last['grain'], last['dairy'], last['livestock']
    html = sub1(html, r'<meta name="description" content="FFAI Q\d \d{4}: [^"]*">',
                f'<meta name="description" content="FFAI Q{q} {y}: {c} {regime(c)}. Grain {g}, Dairy {dy}, Livestock {lv}. '
                f'Free quarterly farm index plus crop insurance in WI &amp; MN. Call 715-797-2428.">', 'meta description')
    html = sub1(html, r'<meta property="og:title" content="FFAI [^"]*">',
                f'<meta property="og:title" content="FFAI {c} {regime(c)} — Farmers First Ag Index | Q{q} {y}">', 'og:title')
    html = sub1(html, r'<meta name="twitter:title" content="FFAI [^"]*">',
                f'<meta name="twitter:title" content="FFAI {c} {regime(c)}">', 'twitter:title')
    open(ip, 'w', encoding='utf-8').write(html)

    # ---- share image ----
    draw_og(os.path.join(ROOT, 'og-share.png'),
            {**last, 'count': len(rows), 'published': today})

    md.append(f'\nWrote ffai-data.js, api/v3/current.json, api/v3/history.json, index.html meta, og-share.png. '
              f'Commentary on the page stays labelled for its own quarter until it is rewritten.')
    print('\n'.join(md)); summary('\n'.join(md))


if __name__ == '__main__':
    main()

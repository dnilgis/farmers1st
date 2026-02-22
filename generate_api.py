#!/usr/bin/env python3
"""
Generate FFAI API JSON files from ffai_v3_engine.py output.
Run after the engine, copies JSON into api/v3/ for deployment.

Usage:
    python generate_api.py ffai_v3_historical.csv
    python generate_api.py  (defaults to ffai_v3_historical.csv)
"""
import csv, json, sys, os
from datetime import datetime

def main():
    fname = sys.argv[1] if len(sys.argv) > 1 else 'ffai_v3_historical.csv'
    outdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'api', 'v3')
    os.makedirs(outdir, exist_ok=True)

    with open(fname, 'r') as f:
        rows = list(csv.DictReader(f))

    now = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')

    # ── Parse rows ──
    quarters = []
    for row in rows:
        comp = row.get('composite', '')
        if not comp:
            continue
        q = {
            'quarter': row.get('quarter', ''),
            'date': row.get('date', ''),
            'composite': round(float(comp), 1),
            'grain': round(float(row.get('grain', 0)), 1),
            'dairy': round(float(row.get('dairy', 0)), 1),
            'livestock': round(float(row.get('livestock', 0)), 1),
        }
        quarters.append(q)

    last = quarters[-1]
    prev = quarters[-2] if len(quarters) > 1 else {}

    def regime(v):
        if v >= 70: return 'STRONG'
        if v >= 55: return 'FAVORABLE'
        if v >= 40: return 'GUARDED'
        return 'STRESSED'

    # ── current.json ──
    current = {
        'ffai_version': '3.0',
        'generated': now,
        'quarter': last['quarter'],
        'date': last['date'],
        'composite': last['composite'],
        'regime': regime(last['composite']),
        'sub_indexes': {
            'grain': last['grain'],
            'dairy': last['dairy'],
            'livestock': last['livestock'],
        },
        'outlook': round(float(rows[-1].get('outlook', 0)), 1) if rows[-1].get('outlook') else None,
        'previous': {
            'quarter': prev.get('quarter', ''),
            'composite': prev.get('composite', 0),
            'grain': prev.get('grain', 0),
            'dairy': prev.get('dairy', 0),
            'livestock': prev.get('livestock', 0),
            'outlook': round(float(rows[-2].get('outlook', 0)), 1) if len(rows) > 1 and rows[-2].get('outlook') else None,
        },
        'regimes': {
            'grain': regime(last['grain']),
            'dairy': regime(last['dairy']),
            'livestock': regime(last['livestock']),
            'outlook': regime(round(float(rows[-1].get('outlook', 0)), 1)) if rows[-1].get('outlook') else None,
        },
        'regime_thresholds': {
            'STRONG': '70-100',
            'FAVORABLE': '55-70',
            'GUARDED': '40-55',
            'STRESSED': '0-40',
        },
        'next_update': '',  # Fill manually or compute
        'source': 'https://farmers1st.com',
        'api_docs': 'https://farmers1st.com/api/',
        'license': 'CC BY 4.0',
    }

    with open(os.path.join(outdir, 'current.json'), 'w') as f:
        json.dump(current, f, indent=2)
    print(f'  api/v3/current.json  ({last["quarter"]} = {last["composite"]} {regime(last["composite"])})')

    # ── history.json ──
    history = {
        'ffai_version': '3.0',
        'generated': now,
        'count': len(quarters),
        'frequency': 'quarterly',
        'start': quarters[0]['quarter'],
        'end': quarters[-1]['quarter'],
        'fields': ['quarter', 'date', 'composite', 'grain', 'dairy', 'livestock'],
        'quarters': quarters,
        'source': 'https://farmers1st.com',
        'api_docs': 'https://farmers1st.com/api/',
        'license': 'CC BY 4.0',
    }

    with open(os.path.join(outdir, 'history.json'), 'w') as f:
        json.dump(history, f, indent=2)
    print(f'  api/v3/history.json  ({len(quarters)} quarters)')

    # ── meta.json stays static (model doesn't change) ──
    print(f'  api/v3/meta.json     (static — edit manually if model changes)')
    print()
    print('Done. Copy api/ folder to your site root.')

if __name__ == '__main__':
    main()

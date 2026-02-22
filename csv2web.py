#!/usr/bin/env python3
"""
Convert ffai_v3_historical.csv → JavaScript history array for ffai-data.js
Run after ffai_v3_engine.py, paste output into ffai-data.js history array.
"""
import csv, sys

def main():
    fname = sys.argv[1] if len(sys.argv) > 1 else 'ffai_v3_historical.csv'
    
    print("  // Paste this into ffai-data.js → history array")
    print("  history: [")
    
    with open(fname, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    for i, row in enumerate(rows):
        q = row.get('quarter', '')
        comp = row.get('composite', '')
        grain = row.get('grain', '')
        dairy = row.get('dairy', '')
        live = row.get('livestock', '')
        
        if not comp or comp == '':
            continue
        
        def fmt(v):
            if v == '' or v is None:
                return 'null'
            try:
                return str(round(float(v), 1))
            except:
                return 'null'
        
        comma = ',' if i < len(rows) - 1 else ''
        print(f'    ["{q}",{fmt(comp)},{fmt(grain)},{fmt(dairy)},{fmt(live)}]{comma}')
    
    print("  ],")
    print()
    
    # Also print current quarter values
    last = rows[-1]
    prev = rows[-2] if len(rows) > 1 else {}
    print("  // Current quarter values:")
    print(f"  composite:  {fmt(last.get('composite',''))},")
    print(f"  prevComp:   {fmt(prev.get('composite',''))},")
    print(f"  grain:      {fmt(last.get('grain',''))},")
    print(f"  dairy:      {fmt(last.get('dairy',''))},")
    print(f"  livestock:  {fmt(last.get('livestock',''))},")
    print(f"  outlook:    {fmt(last.get('outlook',''))},")
    print(f"  prevGrain:      {fmt(prev.get('grain',''))},")
    print(f"  prevDairy:      {fmt(prev.get('dairy',''))},")
    print(f"  prevLivestock:  {fmt(prev.get('livestock',''))},")
    print(f"  prevOutlook:    {fmt(prev.get('outlook',''))},")

def fmt(v):
    if v == '' or v is None:
        return 'null'
    try:
        return str(round(float(v), 1))
    except:
        return 'null'

if __name__ == '__main__':
    main()

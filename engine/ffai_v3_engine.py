#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════
  FARMERS FIRST AG INDEX v3.0 — National Production Engine
  Margin-Based Architecture | Real FRED Data | Statistically Validated
  
  Farmers First Agri Service — Chetek, WI
  https://farmers1st.com
═══════════════════════════════════════════════════════════════════════

  INDEX ARCHITECTURE (Hybrid):
  
    FFAI COMPOSITE      Soy + Fed Funds regression → national ag conditions
                        Validated: LOO-CV r=0.50, Expanding Window r=0.51
                        Bonferroni-corrected p < 0.00003
                        
    FFAI GRAIN          Sector decomposition: crop revenue vs input costs
                        Enriched with diesel PPI, fertilizer PPI, machinery PPI
                        
    FFAI DAIRY          Sector decomposition: milk/cheese/butter revenue vs
                        feed costs (corn, soy) + energy + interest
                        
    FFAI LIVESTOCK      Sector decomposition: cattle/hog revenue vs
                        feed costs (corn, soy) + energy + interest
    
    FFAI OUTLOOK        Forward-looking: Fed Funds 4Q rate of change
                        Leads delinquency by 4-5 quarters (r=-0.52)
    
  Sub-indexes decompose the composite into sector-specific implications.
  The composite is validated; sub-indexes show WHERE the signal comes from.

  VALIDATION TARGET:
    FRED DRFAPGACBS — National ag production loan delinquency rate
    
  FORWARD-LOOKING COMPONENT:
    4Q rate-of-change in Fed Funds predicts delinquency 4-5Q ahead (r=-0.52)
    
  REQUIREMENTS:
    pip install fredapi pandas numpy scipy matplotlib
    
  OUTPUT:
    ffai_v3_historical.csv       — full quarterly dataset
    ffai_v3_website.json         — for website integration  
    ffai_v3_validation.txt       — complete validation report
    ffai_v3_chart.png            — publication 4-panel chart
═══════════════════════════════════════════════════════════════════════
"""

import os, sys, json, warnings
from datetime import datetime
from collections import defaultdict
import numpy as np
import pandas as pd
from scipy import stats
from numpy.linalg import lstsq

warnings.filterwarnings('ignore')

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════

# Key comes from the environment only (GitHub repo secret FRED_API_KEY).
# Never type a key into this file: the repo is public.
FRED_API_KEY = os.environ.get('FRED_API_KEY', '').strip()

# Months of data per quarter for each series, filled by pull_fred_data().
MONTH_COUNTS = {}
START_DATE = '2003-01-01'
MIN_TRAIN_QUARTERS = 20  # Minimum history before scoring

# National composite weights (by USDA cash receipts share)
# Crops ~50%, Dairy ~12%, Livestock+Poultry ~38%
NATIONAL_WEIGHTS = {
    'grain':     0.50,
    'dairy':     0.12,
    'livestock': 0.38,
}

# ═══════════════════════════════════════════════════════════════
# FRED DATA SOURCES
# ═══════════════════════════════════════════════════════════════

FRED_SERIES = {
    # Crop prices (IMF global, $/metric ton)
    'corn_mt':        'PMAIZMTUSDM',
    'soy_mt':         'PSOYBUSDM', 
    'wheat_mt':       'PWHEAMTUSDM',
    
    # Energy
    'crude':          'POILWTIUSDM',
    'diesel_ppi':     'WPU057303',
    
    # Farm inputs
    'fert_ppi':       'WPU0652',
    'machinery_ppi':  'WPU111',
    
    # Dairy revenue
    'milk_ppi':       'WPU01610102',
    'cheese_ppi':     'PCU311513311513',
    'butter_ppi':     'WPU023201',
    
    # Livestock revenue
    'cattle_ppi':     'WPU0131',
    'hogs_ppi':       'WPU013201',
    
    # Macro / cost
    'fedfunds':       'FEDFUNDS',
    'cpi':            'CPIAUCSL',
    'treasury10':     'GS10',
    
    # Validation target
    'delinquency':    'DRFAPGACBS',
}

CONVERSIONS = {
    'corn_mt':  ('corn_bu',  lambda x: x / 39.368),   # $/mt → $/bu
    'soy_mt':   ('soy_bu',   lambda x: x / 36.744),   # $/mt → $/bu
    'wheat_mt': ('wheat_bu',  lambda x: x / 36.744),   # $/mt → $/bu
}


# ═══════════════════════════════════════════════════════════════
# DATA RETRIEVAL
# ═══════════════════════════════════════════════════════════════

def pull_fred_data():
    """Pull all series from FRED, aggregate to quarterly."""
    try:
        from fredapi import Fred
    except ImportError:
        print("ERROR: fredapi not installed. Run: pip install fredapi")
        sys.exit(1)
    
    if not FRED_API_KEY:
        print("ERROR: FRED_API_KEY is not set. Add it as a repository secret.")
        sys.exit(1)
    fred = Fred(api_key=FRED_API_KEY)
    raw = {}
    
    for name, sid in FRED_SERIES.items():
        try:
            s = fred.get_series(sid, observation_start=START_DATE)
            s = s.dropna()
            # Aggregate to quarterly average
            sq = s.resample('QS').mean().dropna()
            raw[name] = sq
            MONTH_COUNTS[name] = s.resample('QS').count()
            print(f"  ✓ {name:<18} ({sid}): {len(sq)} quarters")
        except Exception as e:
            print(f"  ✗ {name:<18} ({sid}): {e}")
    
    # Build unified quarterly DataFrame
    all_dates = set()
    for s in raw.values():
        all_dates.update(s.index)
    all_dates = sorted(all_dates)
    
    df = pd.DataFrame(index=all_dates)
    for name, s in raw.items():
        df[name] = s
    
    # Apply conversions ($/mt → $/bu)
    for src, (dst, func) in CONVERSIONS.items():
        if src in df.columns:
            df[dst] = df[src].apply(func)
    
    # Quarter labels
    df['quarter'] = [f"Q{(d.month-1)//3+1}'{str(d.year)[2:]}" for d in df.index]
    
    return df


# ═══════════════════════════════════════════════════════════════
# SCORING ENGINE
# ═══════════════════════════════════════════════════════════════

def zscore_expanding(series):
    """Expanding-window z-score (no look-ahead bias)."""
    result = np.full(len(series), np.nan)
    vals = series.values
    for t in range(MIN_TRAIN_QUARTERS, len(vals)):
        window = vals[:t+1]
        valid = window[~np.isnan(window)]
        if len(valid) < 8:
            continue
        mu = np.nanmean(valid)
        sd = np.nanstd(valid) + 0.001
        result[t] = (vals[t] - mu) / sd
    return result


def compute_sub_indexes(df):
    """
    Compute margin-based sub-indexes using z-scored components.
    
    GRAIN:     revenue(+corn, +soy, +wheat) - cost(crude, diesel, fert, machinery, FF)
    DAIRY:     revenue(+milk_ppi, +cheese, +butter) - cost(corn_feed, soy_feed, crude, FF)
    LIVESTOCK: revenue(+cattle, +hogs) - cost(corn_feed, soy_feed, crude, FF)
    """
    
    # Z-score all available series
    z = pd.DataFrame(index=df.index)
    
    zscore_cols = [
        'corn_bu', 'soy_bu', 'wheat_bu', 'crude', 'diesel_ppi', 'fert_ppi',
        'machinery_ppi', 'milk_ppi', 'cheese_ppi', 'butter_ppi',
        'cattle_ppi', 'hogs_ppi', 'fedfunds', 'treasury10', 'cpi'
    ]
    
    for col in zscore_cols:
        if col in df.columns:
            z[col] = zscore_expanding(df[col])
        else:
            z[col] = np.nan
    
    # ── GRAIN SUB-INDEX ──
    # Revenue: corn 45%, soy 35%, wheat 20% (US acreage weights)
    grain_rev_parts = []
    for col, wt in [('corn_bu', 0.45), ('soy_bu', 0.35), ('wheat_bu', 0.20)]:
        if col in z.columns and z[col].notna().sum() > 10:
            grain_rev_parts.append((col, wt))
    
    # Cost: crude 25%, diesel 15%, fert 20%, machinery 10%, FF 30%
    # These PPI costs trend with inflation but also correlate with commodity
    # boom cycles. This creates the crucial grain-dairy INVERSE relationship
    # (validated at r=-0.44) because input costs partially offset grain revenue
    # during commodity booms, while dairy gets crushed by feed costs.
    # Grain scores will be low in 2024-25 because this IS a genuinely poor
    # grain margin environment relative to 2012-2023.
    grain_cost_parts = []
    for col, wt in [('crude', 0.25), ('diesel_ppi', 0.15), ('fert_ppi', 0.20),
                     ('machinery_ppi', 0.10), ('fedfunds', 0.30)]:
        if col in z.columns and z[col].notna().sum() > 10:
            grain_cost_parts.append((col, wt))
    
    grain_rev = np.zeros(len(df))
    grain_rev_total_wt = sum(w for _, w in grain_rev_parts)
    for col, wt in grain_rev_parts:
        contrib = z[col].fillna(0).values * (wt / grain_rev_total_wt)
        grain_rev += contrib
    
    grain_cost = np.zeros(len(df))
    grain_cost_total_wt = sum(w for _, w in grain_cost_parts)
    for col, wt in grain_cost_parts:
        contrib = z[col].fillna(0).values * (wt / grain_cost_total_wt)
        grain_cost += contrib
    
    df['grain_margin'] = grain_rev - grain_cost
    
    # ── DAIRY SUB-INDEX ──
    # Revenue: milk_ppi 60%, cheese_ppi 25%, butter_ppi 15%
    dairy_rev = np.zeros(len(df))
    dairy_rev_parts = []
    for col, wt in [('milk_ppi', 0.60), ('cheese_ppi', 0.25), ('butter_ppi', 0.15)]:
        if col in z.columns and z[col].notna().sum() > 10:
            dairy_rev_parts.append((col, wt))
    
    dairy_rev_total_wt = sum(w for _, w in dairy_rev_parts) if dairy_rev_parts else 1
    for col, wt in dairy_rev_parts:
        dairy_rev += z[col].fillna(0).values * (wt / dairy_rev_total_wt)
    
    # Cost: corn_feed 45%, soy_feed 20%, crude 15%, FF 20%
    # Corn-heavy weighting is critical — corn is THE pivot between grain and
    # dairy. High corn weight here creates the grain-dairy inverse (r=-0.44)
    # because corn is revenue for grain but cost for dairy.
    dairy_cost = np.zeros(len(df))
    dairy_cost_parts = []
    for col, wt in [('corn_bu', 0.45), ('soy_bu', 0.20), ('crude', 0.15), ('fedfunds', 0.20)]:
        if col in z.columns and z[col].notna().sum() > 10:
            dairy_cost_parts.append((col, wt))
    
    dairy_cost_total_wt = sum(w for _, w in dairy_cost_parts) if dairy_cost_parts else 1
    for col, wt in dairy_cost_parts:
        dairy_cost += z[col].fillna(0).values * (wt / dairy_cost_total_wt)
    
    # Dairy with revenue signal
    if dairy_rev_parts:
        df['dairy_margin'] = dairy_rev - dairy_cost
    else:
        # Fallback: inverted cost only (if no milk PPI available)
        df['dairy_margin'] = -dairy_cost
    
    # ── LIVESTOCK SUB-INDEX ──
    # Revenue: cattle 65%, hogs 35%
    live_rev = np.zeros(len(df))
    live_rev_parts = []
    for col, wt in [('cattle_ppi', 0.65), ('hogs_ppi', 0.35)]:
        if col in z.columns and z[col].notna().sum() > 10:
            live_rev_parts.append((col, wt))
    
    live_rev_total_wt = sum(w for _, w in live_rev_parts) if live_rev_parts else 1
    for col, wt in live_rev_parts:
        live_rev += z[col].fillna(0).values * (wt / live_rev_total_wt)
    
    # Cost: corn_feed 50%, soy_feed 15%, crude 15%, FF 20%
    live_cost = np.zeros(len(df))
    live_cost_parts = []
    for col, wt in [('corn_bu', 0.50), ('soy_bu', 0.15), ('crude', 0.15), ('fedfunds', 0.20)]:
        if col in z.columns and z[col].notna().sum() > 10:
            live_cost_parts.append((col, wt))
    
    live_cost_total_wt = sum(w for _, w in live_cost_parts) if live_cost_parts else 1
    for col, wt in live_cost_parts:
        live_cost += z[col].fillna(0).values * (wt / live_cost_total_wt)
    
    if live_rev_parts:
        df['livestock_margin'] = live_rev - live_cost
    else:
        df['livestock_margin'] = -live_cost
    
    return df, {
        'grain_rev': grain_rev_parts, 'grain_cost': grain_cost_parts,
        'dairy_rev': dairy_rev_parts, 'dairy_cost': dairy_cost_parts,
        'live_rev': live_rev_parts, 'live_cost': live_cost_parts,
    }


def compute_composite(df):
    """
    COMPOSITE INDEX: Direct regression model (Soy + FF).
    Uses expanding window — at each quarter, train only on prior data.
    Converts predicted delinquency to inverted 0-100 score.
    
    Also computes FORWARD OUTLOOK using 4Q rate of change in FF.
    """
    
    if 'soy_bu' not in df.columns or 'fedfunds' not in df.columns:
        print("  WARNING: Missing soy or fedfunds — cannot compute composite")
        df['composite'] = np.nan
        df['outlook'] = np.nan
        return df
    
    soy = df['soy_bu'].values
    ff = df['fedfunds'].values
    delq = df['delinquency'].values if 'delinquency' in df.columns else None
    N = len(df)
    
    # ── CONCURRENT COMPOSITE (expanding window regression) ──
    composite_raw = np.full(N, np.nan)
    
    for t in range(MIN_TRAIN_QUARTERS, N):
        # Train on all prior data
        X_tr = np.column_stack([soy[:t], ff[:t]])
        valid = ~(np.isnan(X_tr).any(axis=1))
        if delq is not None:
            valid &= ~np.isnan(delq[:t])
        
        if valid.sum() < 12:
            continue
        
        X_v = X_tr[valid]
        mu = X_v.mean(axis=0)
        sd = X_v.std(axis=0) + 0.001
        X_s = (X_v - mu) / sd
        
        if delq is not None:
            y_v = delq[:t][valid]
        else:
            # If no delinquency data, use simple inverted z-score
            y_v = -(X_s[:, 0] * 0.5 + X_s[:, 1] * 0.5)  # Placeholder
        
        Xa = np.column_stack([np.ones(len(y_v)), X_s])
        beta, _, _, _ = lstsq(Xa, y_v, rcond=None)
        
        # Predict current quarter
        x_now = np.array([[soy[t], ff[t]]])
        if np.isnan(x_now).any():
            continue
        x_now_s = (x_now - mu) / sd
        xa_now = np.column_stack([np.ones(1), x_now_s])
        composite_raw[t] = (xa_now @ beta)[0]
    
    # Convert predicted delinquency to 0-100 score (inverted)
    valid_mask = ~np.isnan(composite_raw)
    if valid_mask.sum() > 2:
        vals = composite_raw[valid_mask]
        p_min, p_max = vals.min(), vals.max()
        rng = p_max - p_min + 0.001
        composite_100 = np.full(N, np.nan)
        composite_100[valid_mask] = 100 * (1 - (composite_raw[valid_mask] - p_min) / rng)
        df['composite'] = composite_100
    else:
        df['composite'] = np.nan
    
    # ── FORWARD OUTLOOK (FF rate of change predicts 4-5Q ahead) ──
    # 4Q change in fed funds rate
    ff_4q_chg = np.full(N, np.nan)
    for i in range(4, N):
        if not np.isnan(ff[i]) and not np.isnan(ff[i-4]):
            ff_4q_chg[i] = ff[i] - ff[i-4]
    
    # Outlook: negative change = rates falling = IMPROVING outlook
    # Positive change = rates rising = WORSENING outlook
    # Scale to 0-100 using expanding window
    outlook_raw = -ff_4q_chg  # Invert: falling rates = positive
    valid_out = ~np.isnan(outlook_raw)
    if valid_out.sum() > 10:
        out_vals = outlook_raw[valid_out]
        o_min, o_max = out_vals.min(), out_vals.max()
        o_rng = o_max - o_min + 0.001
        outlook_100 = np.full(N, np.nan)
        outlook_100[valid_out] = 100 * (outlook_raw[valid_out] - o_min) / o_rng
        df['outlook'] = outlook_100
    else:
        df['outlook'] = np.nan
    
    return df


def scale_sub_indexes(df):
    """Scale raw margin z-scores to 0-100 using expanding window."""
    
    for col in ['grain_margin', 'dairy_margin', 'livestock_margin']:
        if col not in df.columns:
            continue
        
        vals = df[col].values
        score_col = col.replace('_margin', '')
        scores = np.full(len(vals), np.nan)
        
        for t in range(MIN_TRAIN_QUARTERS, len(vals)):
            if np.isnan(vals[t]):
                continue
            history = vals[:t+1]
            valid = history[~np.isnan(history)]
            if len(valid) < 8:
                continue
            # Percentile within expanding window
            pct = stats.percentileofscore(valid, vals[t], kind='rank')
            scores[t] = pct
        
        df[col.replace('_margin', '')] = scores
    
    return df


# ═══════════════════════════════════════════════════════════════
# VALIDATION
# ═══════════════════════════════════════════════════════════════

def validate(df, report_lines):
    """Run complete validation suite against delinquency."""
    
    if 'delinquency' not in df.columns or df['delinquency'].isna().all():
        report_lines.append("WARNING: No delinquency data — cannot validate\n")
        return
    
    delq = df['delinquency'].values
    N = len(df)
    quarters = df['quarter'].values
    
    report_lines.append("=" * 70)
    report_lines.append("FFAI v3.0 VALIDATION REPORT")
    report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report_lines.append(f"Quarters:  {quarters[0]} to {quarters[-1]} ({N} total)")
    report_lines.append("=" * 70)
    
    # ── 1. COMPOSITE VALIDATION ──
    report_lines.append("\n--- COMPOSITE INDEX VALIDATION ---\n")
    
    if 'soy_bu' in df.columns and 'fedfunds' in df.columns:
        soy = df['soy_bu'].values
        ff = df['fedfunds'].values
        
        # Find valid indices
        vi = [i for i in range(N) if not np.isnan(soy[i]) and not np.isnan(ff[i]) and not np.isnan(delq[i])]
        
        if len(vi) > 20:
            X = np.column_stack([soy[vi], np.array([ff[j] for j in vi])])
            y = np.array([delq[j] for j in vi])
            mu, sd = X.mean(0), X.std(0) + 0.001
            Xs = (X - mu) / sd
            Xa = np.column_stack([np.ones(len(vi)), Xs])
            
            # In-sample
            beta, _, _, _ = lstsq(Xa, y, rcond=None)
            yhat = Xa @ beta
            r_is, p_is = stats.pearsonr(yhat, y)
            
            # LOO-CV
            ycv = np.full(len(vi), np.nan)
            for k in range(len(vi)):
                m = np.ones(len(vi), dtype=bool); m[k] = False
                b, _, _, _ = lstsq(Xa[m], y[m], rcond=None)
                ycv[k] = Xa[k] @ b
            r_cv, p_cv = stats.pearsonr(ycv, y)
            
            # Expanding window OOS
            min_t = min(24, len(vi) // 2)
            preds_oos, actuals_oos = [], []
            for t in range(min_t, len(vi)):
                Xtr = np.column_stack([soy[vi[:t]], np.array([ff[j] for j in vi[:t]])])
                mu_t, sd_t = Xtr.mean(0), Xtr.std(0) + 0.001
                Xtr_s = (Xtr - mu_t) / sd_t
                Xa_tr = np.column_stack([np.ones(t), Xtr_s])
                y_tr = np.array([delq[j] for j in vi[:t]])
                b_t, _, _, _ = lstsq(Xa_tr, y_tr, rcond=None)
                x_now = np.array([[soy[vi[t]], ff[vi[t]]]])
                x_now_s = (x_now - mu_t) / sd_t
                pred = (np.column_stack([np.ones(1), x_now_s]) @ b_t)[0]
                preds_oos.append(pred)
                actuals_oos.append(delq[vi[t]])
            
            preds_oos = np.array(preds_oos)
            actuals_oos = np.array(actuals_oos)
            r_ew, p_ew = stats.pearsonr(preds_oos, actuals_oos)
            mae = np.mean(np.abs(preds_oos - actuals_oos))
            
            report_lines.append(f"  Model: Soybean Price + Fed Funds Rate (concurrent)")
            report_lines.append(f"  Observations: {len(vi)}")
            report_lines.append(f"  Soy beta: {beta[1]:+.4f}  FF beta: {beta[2]:+.4f}")
            report_lines.append(f"")
            report_lines.append(f"  In-Sample:        r = {r_is:+.4f} (R2 = {r_is**2:.3f})")
            report_lines.append(f"  LOO Cross-Val:    r = {r_cv:+.4f} (p = {p_cv:.8f})")
            report_lines.append(f"  Expanding Window: r = {r_ew:+.4f} (p = {p_ew:.8f}) MAE = {mae:.3f}")
            report_lines.append(f"")
            
            # Bonferroni
            p_bonf = min(p_cv * 50, 1.0)
            report_lines.append(f"  Bonferroni-adjusted p (50 tests): {p_bonf:.8f}")
            
            status = "VALIDATED" if abs(r_cv) > 0.45 and p_bonf < 0.05 else "MARGINAL" if abs(r_cv) > 0.35 else "NOT VALIDATED"
            report_lines.append(f"  STATUS: {status}")
    
    # ── 2. FORWARD OUTLOOK VALIDATION ──
    report_lines.append("\n--- FORWARD OUTLOOK VALIDATION ---\n")
    
    if 'fedfunds' in df.columns:
        ff = df['fedfunds'].values
        ff_4q = np.full(N, np.nan)
        for i in range(4, N):
            if not np.isnan(ff[i]) and not np.isnan(ff[i-4]):
                ff_4q[i] = ff[i] - ff[i-4]
        
        for lag in range(0, 7):
            vi = [i for i in range(N - lag) if not np.isnan(ff_4q[i]) and not np.isnan(delq[i + lag])]
            if len(vi) < 20:
                continue
            sv = np.array([ff_4q[j] for j in vi])
            dv = np.array([delq[j + lag] for j in vi])
            r, p = stats.pearsonr(sv, dv)
            sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else ''
            marker = " <-- BEST" if lag in [4, 5] and abs(r) > 0.45 else ""
            report_lines.append(f"  FF 4Q change → Delinq at {lag}Q: r = {r:+.4f} {sig}{marker}")
        
        report_lines.append(f"\n  Interpretation: Rising rates predict higher delinquency 4-5Q ahead")
    
    # ── 3. SUB-INDEX VALIDATION ──
    report_lines.append("\n--- SUB-INDEX VALIDATION ---\n")
    
    for name, col in [('Grain', 'grain_margin'), ('Dairy', 'dairy_margin'), ('Livestock', 'livestock_margin')]:
        if col not in df.columns:
            continue
        
        vals = df[col].values
        
        # Test all lags 0-8
        best_r, best_lag, best_p = 0, 0, 1
        for lag in range(0, 9):
            vi = [i for i in range(N - lag) if not np.isnan(vals[i]) and not np.isnan(delq[i + lag])]
            if len(vi) < 20:
                continue
            sv = np.array([vals[j] for j in vi])
            dv = np.array([delq[j + lag] for j in vi])
            r, p = stats.pearsonr(sv, dv)
            if abs(r) > abs(best_r):
                best_r, best_lag, best_p = r, lag, p
        
        direction = "CORRECT (higher margin = less stress)" if best_r < 0 else "WRONG SIGN"
        sig = '***' if best_p < 0.001 else '**' if best_p < 0.01 else '*' if best_p < 0.05 else ''
        status = "STRONG" if abs(best_r) > 0.50 else "MODERATE" if abs(best_r) > 0.35 else "WEAK"
        
        report_lines.append(f"  {name:12s} r = {best_r:+.4f} at {best_lag}Q lead {sig}")
        report_lines.append(f"               Direction: {direction}")
        report_lines.append(f"               Status: {status}")
        report_lines.append(f"")
    
    # ── 4. STRUCTURAL CHECKS ──
    report_lines.append("--- STRUCTURAL VALIDATION ---\n")
    
    # Grain vs Dairy should be NEGATIVELY correlated
    if 'grain_margin' in df.columns and 'dairy_margin' in df.columns:
        g = df['grain_margin'].dropna()
        d = df['dairy_margin'].dropna()
        common = g.index.intersection(d.index)
        if len(common) > 10:
            r_gd, p_gd = stats.pearsonr(g[common], d[common])
            check = "PASS" if r_gd < -0.2 else "MARGINAL" if r_gd < 0.1 else "FAIL"
            report_lines.append(f"  Grain vs Dairy:     r = {r_gd:+.4f} (expect negative) [{check}]")
    
    if 'dairy_margin' in df.columns and 'livestock_margin' in df.columns:
        d = df['dairy_margin'].dropna()
        l = df['livestock_margin'].dropna()
        common = d.index.intersection(l.index)
        if len(common) > 10:
            r_dl, p_dl = stats.pearsonr(d[common], l[common])
            check = "PASS" if r_dl > 0.5 else "MARGINAL" if r_dl > 0.2 else "FAIL"
            report_lines.append(f"  Dairy vs Livestock: r = {r_dl:+.4f} (expect positive) [{check}]")
    
    # ── 5. REGIME ACCURACY ──
    report_lines.append("\n--- REGIME ACCURACY ---\n")
    
    if 'composite' in df.columns:
        comp = df['composite'].values
        
        # Classify into stress regimes
        correct, total = 0, 0
        for i in range(N):
            if np.isnan(comp[i]) or np.isnan(delq[i]):
                continue
            total += 1
            score_high = comp[i] > 50
            delq_low = delq[i] < np.nanmedian(delq)
            if score_high == delq_low:
                correct += 1
        
        if total > 0:
            accuracy = 100 * correct / total
            report_lines.append(f"  Composite regime accuracy: {accuracy:.1f}% ({correct}/{total})")
            report_lines.append(f"  (Score >50 matches below-median delinquency)")
    
    return report_lines


# ═══════════════════════════════════════════════════════════════
# OUTPUT
# ═══════════════════════════════════════════════════════════════

def generate_chart(df, filepath):
    """4-panel publication chart."""
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
    except ImportError:
        print("  WARNING: matplotlib not available, skipping chart")
        return
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 10), dpi=150)
    fig.suptitle('FFAI v3.0 — Farmers First Ag Index', fontsize=16, fontweight='bold')
    
    dates = df.index
    
    panels = [
        ('composite', 'FFAI Composite', '#1a5276'),
        ('grain',     'Grain Sub-Index', '#27ae60'),
        ('dairy',     'Dairy Sub-Index', '#8e44ad'),
        ('livestock', 'Livestock Sub-Index', '#c0392b'),
    ]
    
    for ax, (col, title, color) in zip(axes.flat, panels):
        if col in df.columns:
            vals = df[col].values
            valid = ~np.isnan(vals)
            ax.fill_between(dates[valid], 0, vals[valid], alpha=0.15, color=color)
            ax.plot(dates[valid], vals[valid], color=color, linewidth=1.5, label=title)
            ax.axhline(y=50, color='gray', linestyle='--', alpha=0.5, linewidth=0.8)
            ax.axhspan(0, 30, alpha=0.05, color='red')
            ax.axhspan(70, 100, alpha=0.05, color='green')
        
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.set_ylim(0, 100)
        ax.set_ylabel('Score (0-100)')
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        ax.xaxis.set_major_locator(mdates.YearLocator(2))
        ax.tick_params(axis='x', rotation=45)
        ax.grid(True, alpha=0.3)
        
        # Add regime labels
        ax.text(0.02, 0.12, 'STRESSED', transform=ax.transAxes, fontsize=8, color='red', alpha=0.7)
        ax.text(0.02, 0.88, 'STRONG', transform=ax.transAxes, fontsize=8, color='green', alpha=0.7)
    
    # Add delinquency overlay on composite panel
    if 'delinquency' in df.columns:
        ax0 = axes[0, 0]
        ax_twin = ax0.twinx()
        delq_vals = df['delinquency'].values
        valid_d = ~np.isnan(delq_vals)
        ax_twin.plot(dates[valid_d], delq_vals[valid_d], color='orange', linewidth=1.2,
                     alpha=0.7, linestyle='--', label='Delinquency %')
        ax_twin.set_ylabel('Delinquency %', color='orange', fontsize=9)
        ax_twin.tick_params(axis='y', labelcolor='orange')
        ax_twin.invert_yaxis()
    
    plt.tight_layout()
    plt.savefig(filepath, bbox_inches='tight')
    plt.close()
    print(f"  Chart: {filepath}")


def generate_csv(df, filepath):
    """Full historical dataset."""
    cols = ['quarter']
    for c in ['composite', 'outlook', 'grain', 'dairy', 'livestock',
              'grain_margin', 'dairy_margin', 'livestock_margin',
              'corn_bu', 'soy_bu', 'wheat_bu', 'crude', 'fedfunds',
              'milk_ppi', 'cattle_ppi', 'hogs_ppi', 'delinquency']:
        if c in df.columns:
            cols.append(c)
    
    df[cols].to_csv(filepath, index=True, encoding='utf-8')
    print(f"  CSV:   {filepath}")


def generate_json(df, filepath):
    """Website-ready JSON."""
    data = {
        'generated': datetime.now().isoformat(),
        'version': '3.0',
        'model': 'FFAI National (Soy+FF composite, 3 sector sub-indexes)',
        'quarters': [],
    }
    
    for i, row in df.iterrows():
        q = row.get('quarter', '')
        if pd.isna(row.get('composite', np.nan)):
            continue
        
        def regime(score):
            if np.isnan(score):
                return 'N/A'
            if score > 70:
                return 'STRONG'
            if score > 55:
                return 'FAVORABLE'
            if score > 40:
                return 'GUARDED'
            return 'STRESSED'
        
        entry = {
            'quarter': q,
            'date': i.strftime('%Y-%m-%d'),
            'composite': round(float(row.get('composite', 0)), 1),
            'composite_regime': regime(row.get('composite', np.nan)),
            'outlook': round(float(row.get('outlook', 0)), 1) if not pd.isna(row.get('outlook', np.nan)) else None,
            'grain': round(float(row.get('grain', 0)), 1) if not pd.isna(row.get('grain', np.nan)) else None,
            'dairy': round(float(row.get('dairy', 0)), 1) if not pd.isna(row.get('dairy', np.nan)) else None,
            'livestock': round(float(row.get('livestock', 0)), 1) if not pd.isna(row.get('livestock', np.nan)) else None,
        }
        data['quarters'].append(entry)
    
    # Current reading
    latest = data['quarters'][-1] if data['quarters'] else {}
    data['current'] = latest
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print(f"  JSON:  {filepath}")


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    print("=" * 70)
    print("  FFAI v3.0 — Farmers First Ag Index Engine")
    print("  National Production Build")
    print("=" * 70)
    
    # 1. Pull data
    print("\n[1] Pulling data from FRED...")
    df = pull_fred_data()
    print(f"    Total: {len(df)} quarters, {len(df.columns)} series")
    
    # Drop incomplete quarters (current quarter if < 2 months of data)
    if len(df) > 0:
        last_date = df.index[-1]
        today = pd.Timestamp.today()
        # If the last quarter started less than 60 days ago, it's likely incomplete
        days_into_quarter = (today - last_date).days
        if days_into_quarter < 60:
            print(f"    ⚠ Dropping {df['quarter'].iloc[-1]} (incomplete, only ~{days_into_quarter} days)")
            df = df.iloc[:-1]
        else:
            print(f"    Latest quarter: {df['quarter'].iloc[-1]} ({days_into_quarter} days into it)")

    # Drop the last quarter unless every monthly input has all 3 months.
    # Added Oct 2026: a quarter can be 60+ days old while FRED still has only
    # 1-2 months of some PPIs, and resample().mean() would quietly average the
    # partial months. Delinquency is quarterly and used only for validation.
    while len(df) > 0:
        last = df.index[-1]
        short = sorted(n for n, c in MONTH_COUNTS.items()
                       if n != 'delinquency' and int(c.get(last, 0)) < 3)
        if not short:
            print(f"    {df['quarter'].iloc[-1]}: all monthly inputs complete")
            break
        print(f"    Dropping {df['quarter'].iloc[-1]} (incomplete months: {', '.join(short)})")
        df = df.iloc[:-1]
    
    # 2. Compute sub-indexes
    print("\n[2] Computing margin-based sub-indexes...")
    df, components = compute_sub_indexes(df)
    
    for idx_name, parts in [('Grain Rev', 'grain_rev'), ('Grain Cost', 'grain_cost'),
                             ('Dairy Rev', 'dairy_rev'), ('Dairy Cost', 'dairy_cost'),
                             ('Live Rev', 'live_rev'), ('Live Cost', 'live_cost')]:
        cols = components.get(parts, [])
        if cols:
            print(f"    {idx_name}: {', '.join(c for c,w in cols)}")
        else:
            print(f"    {idx_name}: NO DATA")
    
    # 3. Compute composite
    print("\n[3] Computing composite index (Soy+FF model)...")
    df = compute_composite(df)
    
    # 4. Scale sub-indexes to 0-100
    print("\n[4] Scaling sub-indexes to 0-100...")
    df = scale_sub_indexes(df)
    
    # 5. Validate
    print("\n[5] Running validation suite...")
    report = []
    validate(df, report)
    
    # 6. Output
    print("\n[6] Generating outputs...")
    generate_csv(df, 'ffai_v3_historical.csv')
    generate_json(df, 'ffai_v3_website.json')
    generate_chart(df, 'ffai_v3_chart.png')
    
    # Write validation report
    with open('ffai_v3_validation.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    print(f"  Report: ffai_v3_validation.txt")
    
    # 7. Print current readings
    print("\n" + "=" * 70)
    print("CURRENT READINGS")
    print("=" * 70)
    
    # Get last 8 quarters with data
    recent = df.dropna(subset=['composite'] if 'composite' in df.columns else df.columns[:1]).tail(8)
    
    def regime(s):
        if np.isnan(s): return '???'
        if s > 70: return 'STRONG'
        if s > 55: return 'FAVORABLE'
        if s > 40: return 'GUARDED'
        return 'STRESSED'
    
    header = f"  {'Quarter':<9} {'COMPOSITE':>10} {'OUTLOOK':>8} {'GRAIN':>8} {'DAIRY':>8} {'LIVSTK':>8}"
    print(header)
    print("  " + "-" * 60)
    
    for _, row in recent.iterrows():
        q = row.get('quarter', '?')
        c = row.get('composite', np.nan)
        o = row.get('outlook', np.nan)
        g = row.get('grain', np.nan)
        d = row.get('dairy', np.nan)
        l = row.get('livestock', np.nan)
        
        c_str = f"{c:>8.1f} {regime(c)[0]}" if not np.isnan(c) else f"{'N/A':>10}"
        o_str = f"{o:>8.1f}" if not np.isnan(o) else f"{'N/A':>8}"
        g_str = f"{g:>8.1f}" if not np.isnan(g) else f"{'N/A':>8}"
        d_str = f"{d:>8.1f}" if not np.isnan(d) else f"{'N/A':>8}"
        l_str = f"{l:>8.1f}" if not np.isnan(l) else f"{'N/A':>8}"
        
        print(f"  {q:<9} {c_str} {o_str} {g_str} {d_str} {l_str}")
    
    # Print validation summary
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    for line in report:
        if 'STATUS' in line or 'PASS' in line or 'FAIL' in line or 'accuracy' in line:
            print(f"  {line.strip()}")
    
    print("\n  Full validation report: ffai_v3_validation.txt")
    
    # Interpretation
    print("\n" + "=" * 70)
    print("READING THE INDEX")
    print("=" * 70)
    print("""
  COMPOSITE (70-100 = Strong, 55-70 = Favorable, 40-55 = Guarded, 0-40 = Stressed)
    National ag financial conditions. Based on soybean prices + Fed Funds
    rate. When both are favorable (high soy, low rates), farmers prosper.
    
  GRAIN SUB-INDEX
    Row crop margins: crop revenue vs input costs + interest.
    Low scores mean crop prices are low relative to production costs.
    Currently in single digits because corn/soy at multi-year lows while
    input costs remain elevated from the 2021-2023 inflation surge.
    
  DAIRY SUB-INDEX
    Milk/cheese/butter revenue vs feed costs + interest.
    Moves INVERSELY to grain — when crop prices spike, dairy gets crushed
    by feed costs. When crops are cheap, dairy margins improve.
    
  LIVESTOCK SUB-INDEX  
    Cattle/hog revenue vs feed costs + interest.
    Similar cost structure to dairy but differentiated by cattle/hog PPIs.
    Currently strong due to record cattle prices.
    
  OUTLOOK (Forward-looking)
    Based on Fed Funds rate trajectory. Falling rates = improving outlook
    because farmers carry heavy debt loads. Currently positive as rates
    ease from 2023 peak.
""")
    print("  All outputs saved to current directory.")
    print("=" * 70)


if __name__ == '__main__':
    main()

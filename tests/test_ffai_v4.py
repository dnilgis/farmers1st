"""Selftests for the FFAI v4 engine, publish and stress tools, with hand-worked answers.

    python3 -m unittest discover -s tests -v

Needs pandas, numpy and scipy. Uses no network: the probe CSV on disk stands in for NASS
and synthetic series stand in for FRED.
"""
import importlib.util, json, math, os, sys, tempfile, unittest
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROBE = os.path.join(ROOT, 'engine', 'v4probe', 'nass_national_indexes.csv')


def load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, rel))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod


E = load('ffai_v4', 'engine/ffai_v4.py')
P = load('ffai_v4_publish', 'tools/ffai_v4_publish.py')
S = load('ffai_v4_stress', 'tools/ffai_v4_stress.py')


class Engine(unittest.TestCase):
    def test_pct_in_counts_ties_at_or_below(self):
        base = pd.Series([1.0, 2.0, 2.0, 3.0])
        self.assertEqual(E.pct_in(base, 2.0), 75.0)   # 3 of 4 at or below
        self.assertEqual(E.pct_in(base, 0.5), 0.0)
        self.assertEqual(E.pct_in(base, 9.0), 100.0)
        self.assertTrue(math.isnan(E.pct_in(base, float('nan'))))

    def test_regime_lines(self):
        self.assertEqual([E.regime(v) for v in (39.9, 40, 54.9, 55, 69.9, 70)],
                         ['STRESSED', 'GUARDED', 'GUARDED', 'FAVORABLE', 'FAVORABLE', 'STRONG'])

    def test_missing_values_never_become_nan_in_json(self):
        s = pd.Series([100.0, float('nan'), 110.0])
        self.assertIsNone(E.pct_change(s, 1, 0))
        self.assertEqual(E.pct_change(s, 2, 0), 10.0)
        self.assertIsNone(E.pct_change(s, 2, -9))      # off the end
        self.assertIsNone(E.fin(float('nan')))
        self.assertEqual(E.fin(1.234, 2), 1.23)

    def test_quarter_needs_all_three_months(self):
        idx = pd.date_range('2020-01-01', periods=6, freq='MS')
        m = pd.Series([1, 2, 3, 4, np.nan, 6], index=idx, dtype=float)
        q = E.to_quarters(m)
        self.assertEqual(q.iloc[0], 2.0)
        self.assertTrue(np.isnan(q.iloc[1]))

    def test_eff_n_matches_hand_formula(self):
        rng = np.random.default_rng(1)
        x = pd.Series(rng.normal(size=40)); y = x + pd.Series(rng.normal(size=40))
        r, n, ne, p = E.eff_n_p(x, y)
        r1, r2 = x.autocorr(1), y.autocorr(1)
        self.assertAlmostEqual(ne, min(40 * (1 - r1 * r2) / (1 + r1 * r2), 40), places=9)
        self.assertGreater(r, 0); self.assertLess(p, 0.01)

    def test_offline_build_reproduces_q2_2026(self):
        # Fixed fixture: the probe CSV on disk and the Q2 2026 numbers published from it.
        # (Not compared with engine/v4/, which moves on as USDA revises its data.)
        names = sorted({x for p in E.SECTORS.values() for x in p})
        q = E.to_quarters(E.nass_monthly(names, None, PROBE))
        q = q[q[names].notna().all(axis=1)]
        sc = E.score(q)
        t = pd.Timestamp('2026-04-01')
        self.assertEqual(E.qlabel(sc.index[-1]), "Q2'26")
        got = {s: (round(sc.loc[t, f'{s}_ratio'], 1), sc.loc[t, f'{s}_A']) for s in E.SECTORS}
        self.assertEqual(got, {'all': (84.5, 11.0), 'crops': (73.4, 0.0), 'livestock': (113.9, 94.0), 'dairy': (60.2, 0.0)})
        self.assertEqual(len(sc), 126)

    def test_validate_writes_annual_table(self):
        names = sorted({x for p in E.SECTORS.values() for x in p})
        q = E.to_quarters(E.nass_monthly(names, None, PROBE))
        q = q[q[names].notna().all(axis=1)]
        sc = E.score(q)
        s = np.log(sc['all_ratio']); ann = s.groupby(s.index.year).mean()
        yrs = pd.to_datetime([f'{y}-01-01' for y in range(1990, 2026)])
        # Synthetic income that moves with the ratio, so T1 must pass.
        base = pd.Series([ann.get(y, ann.iloc[0]) for y in range(1990, 2026)], index=yrs)
        nfi = 100 * np.exp(3 * (base - base.iloc[0])) + 50
        fr = {'nfi': nfi, 'subsidies': pd.Series(10.0, index=yrs), 'cpi': pd.Series(np.linspace(100, 200, 36), index=yrs),
              'delinquency': pd.Series(dtype=float)}
        with tempfile.TemporaryDirectory() as d:
            old, E.OUT = E.OUT, d
            try:
                winner, validated, res = E.validate(sc, fr, [])
            finally:
                E.OUT = old
            a = pd.read_csv(os.path.join(d, 'ffai_v4_annual.csv'), index_col=0)
        self.assertEqual(winner, 'A'); self.assertTrue(validated)
        self.assertIn('A_dlog', a.columns); self.assertIn('real_nfi_dlog', a.columns)
        self.assertEqual(res['detail']['A']['T1']['n_years'], 30)


class Publish(unittest.TestCase):
    def test_to_reach_hand_worked(self):
        base = [float(v) for v in range(1, 101)]          # 100 base quarters, ratio 1..100
        out = {t['regime']: t for t in P.to_reach(base, 50.0)}
        self.assertEqual(out['GUARDED']['ratio'], 40.0)   # 40 of 100 at or below 40
        self.assertTrue(out['GUARDED']['reached']); self.assertEqual(out['GUARDED']['move_pct'], -20.0)
        self.assertEqual(out['FAVORABLE']['ratio'], 55.0); self.assertEqual(out['FAVORABLE']['move_pct'], 10.0)
        self.assertEqual(out['STRONG']['ratio'], 70.0); self.assertFalse(out['STRONG']['reached'])

    def test_to_reach_agrees_with_engine_score(self):
        base = sorted(round(v, 1) for v in np.random.default_rng(3).normal(100, 10, 100))
        for t in P.to_reach(base, 90.0):
            self.assertGreaterEqual(E.pct_in(pd.Series(base), t['ratio'] * (1 + 1e-12)), t['score'])
            self.assertLess(E.pct_in(pd.Series(base), t['ratio'] * (1 - 1e-9)), t['score'])

    def test_fisher_ci_hand_worked(self):
        # atanh(.75) = 0.9730, se = 1/sqrt(26.3) = 0.1950 -> tanh(0.5908), tanh(1.3552)
        self.assertEqual(P.fisher_ci(0.75, 29.3), [0.53, 0.88])
        self.assertIsNone(P.fisher_ci(0.5, 3))

    def test_usda_check_and_revisions(self):
        rows = [{'quarter': "Q1'95", 'all_ratio': '100.4', 'usda_ratio': '100'},
                {'quarter': "Q2'95", 'all_ratio': '98.2', 'usda_ratio': '100'}]
        gap, q = P.usda_check(rows)
        self.assertAlmostEqual(gap, 1.8); self.assertEqual(q, "Q2'95")
        self.assertIsNone(P.usda_check([{'quarter': "Q1'95", 'all_ratio': '1'}]))
        old = [{'quarter': "Q1'95", 'ratio': 100.0, 'score': 50.0}]
        self.assertEqual(P.revisions(old, [{'quarter': "Q1'95", 'all': 100.0, 'all_score': 50.0}]), [])
        self.assertEqual(len(P.revisions(old, [{'quarter': "Q1'95", 'all': 101.0, 'all_score': 50.0}])), 1)

    def test_multiple_tests_holm(self):
        tests = {'A': {'T1': True, 'T2': True, 'T3': True}, 'B': {'T1': True, 'T2': False, 'T3': False}}
        det = {c: {'T1': {'p_one_sided': 0.001}, 'T2': {'p_one_sided': 0.03}, 'T3': {'test_years': 10}} for c in 'AB'}
        txt = P.multiple_tests(tests, det)
        self.assertIn('6 tests ran', txt); self.assertIn('4 passed', txt)
        self.assertIn('Not every', txt)   # 0.03 is not below 0.05/2 at the third step
        for c in 'AB':
            det[c]['T2']['p_one_sided'] = 0.004
        self.assertIn('All correlation tests', P.multiple_tests(tests, det))

    def test_published_files_agree(self):
        cur = json.load(open(os.path.join(ROOT, 'api', 'v4', 'current.json')))
        hist = json.load(open(os.path.join(ROOT, 'api', 'v4', 'history.json')))
        self.assertEqual(cur['quarter'], hist['end'])
        self.assertEqual(cur['score'], hist['quarters'][-1]['score'])
        self.assertEqual(cur['ratio'], hist['quarters'][-1]['ratio'])
        summ = json.load(open(os.path.join(ROOT, 'engine', 'v4', 'ffai_v4_summary.json')))
        self.assertEqual(cur['quarter'], summ['quarter'])
        self.assertEqual(cur['score'], summ['sectors']['all']['score'])
        csvp = os.path.join(ROOT, 'api', 'v4', 'history.csv')
        if os.path.exists(csvp):
            c = pd.read_csv(csvp)
            self.assertEqual(len(c), hist['count'])
            self.assertEqual(float(c['score'].iloc[-1]), cur['score'])


class Stress(unittest.TestCase):
    def test_holm(self):
        self.assertEqual(S.holm([0.01, 0.04, 0.03]), [True, False, False])   # 0.01<0.0167; 0.03>0.025 stops
        self.assertEqual(S.holm([0.001, 0.002]), [True, True])

    def test_seasonal_factors_recover_pattern(self):
        idx = pd.date_range('2000-01-01', periods=80, freq='QS')
        pat = {1: -0.02, 2: 0.03, 3: 0.01, 4: -0.02}
        s = pd.Series([100 * math.exp(pat[t.quarter]) for t in idx], index=idx)
        f = S.seasonal_factors(s)
        for k, v in pat.items():
            self.assertAlmostEqual(f[k][0], 100 * v, places=6)

    def test_partial_quarter_exact_when_flat(self):
        idx = pd.date_range('2000-01-01', periods=24, freq='MS')
        r, p = pd.Series(120.0, index=idx), pd.Series(100.0, index=idx)
        err, part, full = S.partial_quarter_error(r, p, 1)
        self.assertEqual(float(err.abs().max()), 0.0)
        self.assertEqual(float(full.iloc[0]), 120.0)

    def test_part2_without_key_says_so(self):
        md = []
        S.part2(None, None, None, md, '')
        self.assertTrue(any('not re-run' in x for x in md))


if __name__ == '__main__':
    unittest.main()

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
        # The pre-Oct 2026 labels, still published as label_legacy.
        self.assertEqual([E.regime_legacy(v) for v in (39.9, 40, 54.9, 55, 69.9, 70)],
                         ['STRESSED', 'GUARDED', 'GUARDED', 'FAVORABLE', 'FAVORABLE', 'STRONG'])

    def test_label_lines_are_the_base_quartiles(self):
        self.assertEqual([E.regime(v) for v in (0, 24.9, 25, 49.9, 50, 74.9, 75, 100)],
                         ['LOW', 'LOW', 'BELOW MIDDLE', 'BELOW MIDDLE', 'ABOVE MIDDLE', 'ABOVE MIDDLE', 'HIGH', 'HIGH'])
        for v in (None, float('nan'), 'x'):
            self.assertIsNone(E.regime(v)); self.assertIsNone(E.regime_legacy(v))
        self.assertIs(E.L, P.L)   # publish and engine share one definition

    def test_nass_parse_accepts_only_the_12_month_names(self):
        rows = [{'year': '2020', 'reference_period_desc': 'MAR', 'Value': '101.5'},
                {'year': '2020', 'reference_period_desc': 'MARKETING YEAR', 'Value': '999'},
                {'year': '2020', 'reference_period_desc': 'MARCH', 'Value': '998'},
                {'year': '2020', 'reference_period_desc': 'YEAR', 'Value': '997'},
                {'year': '2020', 'reference_period_desc': 'DEC', 'Value': '1,234'},
                {'year': '2020', 'reference_period_desc': 'JAN', 'Value': '(NA)'}]
        self.assertEqual(E.parse_monthly(rows, 'x'), {pd.Timestamp(2020, 3, 1): 101.5, pd.Timestamp(2020, 12, 1): 1234.0})

    def test_nass_parse_fails_on_duplicate_months_that_disagree(self):
        same = [{'year': '2020', 'reference_period_desc': 'MAR', 'Value': '101.5'}] * 2
        self.assertEqual(E.parse_monthly(same, 'x'), {pd.Timestamp(2020, 3, 1): 101.5})
        clash = same[:1] + [{'year': '2020', 'reference_period_desc': 'MAR', 'Value': '101.6'}]
        with self.assertRaisesRegex(RuntimeError, 'two different values'):
            E.parse_monthly(clash, 'x')
        with tempfile.TemporaryDirectory() as d:
            f = os.path.join(d, 'p.csv')
            pd.DataFrame({'series': ['S', 'S'], 'group': 'g', 'freq': 'MONTHLY', 'date': '2020-03-01', 'value': [1.0, 2.0]}).to_csv(f, index=False)
            with self.assertRaisesRegex(RuntimeError, 'two different values'):
                E.nass_monthly(['S'], None, f)

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
        out = {t['label']: t for t in P.to_reach(base, 40.0)}
        self.assertEqual(list(out), ['BELOW MIDDLE', 'ABOVE MIDDLE', 'HIGH'])
        self.assertEqual(out['BELOW MIDDLE']['ratio'], 25.0)   # 25 of 100 at or below 25
        self.assertTrue(out['BELOW MIDDLE']['reached']); self.assertEqual(out['BELOW MIDDLE']['move_pct'], -37.5)
        self.assertEqual(out['ABOVE MIDDLE']['ratio'], 50.0); self.assertEqual(out['ABOVE MIDDLE']['move_pct'], 25.0)
        self.assertFalse(out['ABOVE MIDDLE']['reached'])
        self.assertEqual(out['HIGH']['ratio'], 75.0); self.assertFalse(out['HIGH']['reached'])
        self.assertEqual(out['HIGH']['move_pct'], 87.5)
        self.assertTrue(all(t['regime'] == t['label'] for t in out.values()))

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


    def test_published_labels_and_real_time_flags(self):
        cur = json.load(open(os.path.join(ROOT, 'api', 'v4', 'current.json')))
        hist = json.load(open(os.path.join(ROOT, 'api', 'v4', 'history.json')))
        self.assertEqual(cur['label'], P.L.label(cur['score'])); self.assertEqual(cur['regime'], cur['label'])
        self.assertEqual(cur['label_legacy'], P.L.label_legacy(cur['score'])); self.assertEqual(cur['label_vs'], '1995-2019')
        for k, v in cur['sectors'].items():
            self.assertEqual(v['label'], P.L.label(v['score']), k)
        self.assertIn('label', hist['fields']); self.assertIn('real_time', hist['fields'])
        for h in hist['quarters']:
            self.assertEqual(h['label'], P.L.label(h['score']), h['quarter'])
            self.assertIs(h['real_time'], P.qkey(h['quarter']) >= P.qkey(P.FIRST_LIVE), h['quarter'])
            if P.parse_q(h['quarter'])[1] <= 2019:
                self.assertFalse(h['real_time'])
        ya = cur['year_ago']
        self.assertEqual(P.qkey(cur['quarter']) - P.qkey(ya['quarter']), 4)
        self.assertAlmostEqual(cur['ratio_change_vs_year_ago_pct'], 100 * (cur['ratio'] / ya['ratio'] - 1), delta=0.15)

    def test_page_and_badge_hold_no_label_lines(self):
        # The label is computed once, in publish; the page and badge only read it.
        import re
        for rel in ('index.html', 'api/v4/badge.js'):
            txt = open(os.path.join(ROOT, rel), encoding='utf-8').read()
            if rel.endswith('.html'):   # code only; the methodology text may name the old labels
                txt = '\n'.join(re.findall(r'<script>(.*?)</script>', txt, re.S))
                self.assertIn('D4.headline', txt)
            for pat in ('>=70', '>=55', '>=40', '>= 70', '>= 55', '>= 40', '>=75', '>=25', '>= 75', '>= 25', 'STRESSED', 'FAVORABLE'):
                self.assertNotIn(pat, txt, f'{rel} contains {pat!r}')

    def test_v3_files_are_marked_retired(self):
        for f in ('current.json', 'history.json', 'meta.json'):
            d = json.load(open(os.path.join(ROOT, 'api', 'v3', f)))
            self.assertEqual(d.get('status'), 'retired', f)
            self.assertEqual(d.get('superseded_by'), '/api/v4/current.json', f)
            self.assertTrue(d.get('retired_note'), f)


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

    def test_track_record_keeps_misses(self):
        dA = pd.Series({2001: math.log(1.10), 2002: math.log(0.95), 2003: math.log(1.02)})
        real = pd.Series({2000: 100.0, 2001: 120.0, 2002: 132.0, 2003: 132.0})
        yr = pd.Series({2001: 80.0, 2002: 30.0, 2003: 10.0})
        t = S.track_record(dA, real, yr)
        self.assertEqual(list(t.year), [2001, 2002, 2003])
        self.assertEqual(list(t.ratio_change_pct), [10.0, -5.0, 2.0])
        self.assertEqual(list(t.real_nfi_change_pct), [20.0, 10.0, 0.0])
        self.assertEqual(list(t.same_direction), [True, False, None])   # 2002 is a miss; 2003 income flat
        self.assertEqual(list(t.label), ['HIGH', 'BELOW MIDDLE', 'LOW'])

    def test_part2_without_key_says_so(self):
        md = []
        S.part2(None, None, None, md, '')
        self.assertTrue(any('not re-run' in x for x in md))


if __name__ == '__main__':
    unittest.main()

# FFAI v4 audit (Oct 17, 2026)

Branch `fx/ffai-audit`. Scope: `engine/ffai_v4.py`, `engine/v4/*`, `tools/ffai_v4_publish.py`, `ffai-v4.js`, `index.html`, `api/v4/*`, `api/v3/*`, the workflow. Standard: the AGSIST honest-numbers rules.

**What could and could not be re-run.** The sandbox cannot reach NASS or FRED. The NASS side was rebuilt from `engine/v4probe/nass_national_indexes.csv` (to Aug 2026). It matches the committed engine CSV exactly: 126 quarters, ratio gap 0.000, score gap 0.0. No net farm income, subsidy or CPI data is on disk, so **T1 to T3 could not be re-run** and no income-side sensitivity in this file is measured. `tools/ffai_v4_stress.py` (workflow mode `stress`) runs all of those checks when it has FRED. The NASS-only results are in `engine/stress/stress_report_offline_2026-10-17.md`.

Severity: HIGH = a reader is misled today. MEDIUM = a claim is weaker than the page implies, or a failure mode can publish something wrong. LOW = hygiene.

---

## HIGH

### H1. The headline label has never been tested, and it has read STRESSED in every quarter since 2020
- The validation tests **year-over-year changes** in the log ratio. The 0-100 level and the four labels were never tested (meta.json says so). But the headline is the label.
- Score A, all farms: **26 of 26 quarters from Q1 2020 to Q2 2026 are STRESSED**. The yearly average peaked at 29 in 2022, a year when USDA put net farm income at a record in nominal dollars (check this against `ffai_v4_annual.csv` after a stress run). Crops are also 26 of 26. Dairy is 25 of 26.
- The cause is built in. The ratio fell 1.20 points a year over the 1995-2019 base, so a fixed-base percentile sinks over time. Under A, the label measures how far we are from 1995-2019, not how farms are doing.
- Candidate B passed the same three tests (3 of 3) and now reads **75 STRONG**. The two candidates give different labels in 49 of 86 quarters, and 17 of those are opposite ends (one STRESSED, the other STRONG). Tests on changes cannot tell which label is right.
- The base period alone moves today's score from 11 to 45. Using 1995-2019 gives 11, 2000-2019 gives 14, 2010-2019 gives 28, 2005-2024 gives 22 and 2016-2025 gives 45.
- The page does say "Read STRESSED as low against 1995-2019, not low income", but only in the methodology, far below the headline. The headline, og:title, the badge and the meta description all lead with "11 STRESSED".
- **Fix (Sig decides):** use labels that describe the price position, which is all that was measured. For example, LOW / BELOW MIDDLE / ABOVE MIDDLE / HIGH "vs 1995-2019". Or lead with the ratio and its change from a year earlier, and keep the label secondary. Then run `stress` mode and publish its table of real net farm income in years under each label before using any label that sounds like income.

### H2. The v3 endpoints contradict v4 for the same quarter
- `api/v3/current.json` says Q2 2026 is **69.7 FAVORABLE**. v4 says **11 STRESSED** for the same quarter. Any site that embedded the v3 badge was still showing "70 FAVORABLE", with no date and no sign it was retired. That breaks rule 8 (two files must never disagree in front of a reader).
- **Fixed:** `api/v3/badge.js` now shows a retirement notice and a link, with no score.
- **Still open (Sig decides):** add `"status": "retired"` and `"superseded_by": "/api/v4/current.json"` to `api/v3/current.json`. The site promised v3 would stay "unchanged", so this is your call.

## MEDIUM

### M1. Pre-registration: the timing holds, but the choices were made after looking at the data
- **Verified from GitHub's own run record.** Run 6 was the first and only v4 validation run. It started 2026-10-07 01:14:23Z on head `157df58`, which already contains `163cc4b` (the tests, committed 01:13:25Z). The only change to the tests afterwards was `HEADLINE_METHOD='A'`, which is the tie rule applied.
- **The forking paths came before that.** Run 3 (00:30Z) tested v3-style scores against farm loan delinquency, and they failed. Runs 4 and 5 pulled the full NASS ratio history before the candidates were written. The target then moved from delinquency to net farm income. v4 itself shows r = -0.03 against delinquency. The 1995-2019 base, the 40-quarter window and the 2005 start for B were all set with the ratio's history in view. Income history is common knowledge.
- **The tests were also close to certain to pass.** Net farm income is receipts minus expenses, priced with the same USDA prices. "Pre-registered" is true, but it tells a reader little. The page already says "partly by construction". Keep that sentence next to every claim that it was tested.
- `engine/v4/ffai_v4_summary.json` detail was parsed by hand from run 6's report, with p stored as 0.0. That was disclosed in `b50c876`. The next engine run rewrites it.

### M2. T3 does not show forecasting skill
- The "out of sample" test predicts this year's income change from **this year's** full-year ratio. That ratio is complete only in late January of the next year. By then USDA has already published its own estimate. The benchmark that matters, USDA's own forecast, was not tested.
- The "same change as last year" baseline is a straw man: its RMSE is 0.320, worse than "no change" at 0.221. Beating it shows little.
- A cut error to 0.78x of "no change" over 20 years, and B to 0.67x over 10 years. Neither has a significance test. Ten years is an anecdote.
- **Fix:** keep the "not a forecast" wording. If a forecast claim is ever wanted, add a T4 that compares against USDA's December forecast, using ALFRED vintages.

### M3. Statistics (from the published results; not re-run)

| Test | r | n / eff. n | 95% range (Fisher, eff. n) |
|---|---|---|---|
| A, T1 | 0.75 | 30 / 29.3 | 0.53 to 0.88 |
| A, T2 | 0.84 | 30 / 29.8 | 0.69 to 0.92 |
| B, T1 | 0.70 | 20 / 19.6 | 0.37 to 0.87 |
| B, T2 | 0.78 | 20 / 19.7 | 0.51 to 0.91 |

- Autocorrelation is not a problem here. The lag-1 autocorrelation of the yearly change in the log ratio is -0.10, so eff. n is close to n, and the samples do not overlap.
- One-sided p was pre-registered. All p < 0.001, so all four correlation tests survive a Holm correction for 6 tests.
- Correlating yearly changes is a sound way to avoid a shared trend. It is not evidence for the level or the labels (see H1).
- Not measured here (needs FRED): other start years, dropping 2020-2022 (CFAP years; T2 partly covers this), dropping 2025 (a USDA forecast inside the test), no deflator, and USDA's own CPI series. All of these are coded in `stress` mode.

### M4. Revisions and vintages
- **Net farm income** comes from today's FRED vintage, and the latest year is a forecast. `stress` mode re-runs T1 on income as first published by March 31 of the following year (ALFRED), if ALFRED holds vintages for the series.
- **NASS indexes** have been rebased and reweighted over the years, and Quick Stats keeps no vintages. Every published number assumes today's weights. This cannot be tested from Quick Stats. Start archiving each pull (see R4).
- **1995-2019 published scores are in-sample.** Ranked only against quarters already out at the time, they differ by 21.3 points on average, and the label differs in **40 of 80** quarters (2000-2019). The methodology says so, but the chart and `history.json` do not mark those quarters.
- **Fix:** add a `real_time` flag or a real-time score column to the history, and shade those quarters on the chart.

### M5. Seasonality inflates quarter-to-quarter moves
- The quarterly ratio is seasonal. Against the trend, all farms run Q1 -1.2%, Q2 +1.7%, Q3 +1.1%, Q4 -1.4% (standard errors 0.3 to 0.5). Dairy runs Q2 -4.0% and Q4 +5.2%.
- So "up 11 from 0 in Q1'26" is partly the season. Against the same quarter a year earlier, the score is **down 13** (24 in Q2'25).
- The mean all-farms score by quarter of year (1995-2019) runs from 46 to 55.
- **Fixed:** the year-ago line under the score, plus a methodology note.
- **Sig decides:** whether to seasonally adjust, or make the year-ago comparison the main one.

### M6. The labels sit on a knife edge
- A ±5% move in prices received sends the all-farms score from 11 to 1 or 16. Livestock goes from 94 to 85 or 100.
- The median quarter-to-quarter move is 6 points and the 90th percentile is 20. The all-farms label changed 29 times in 126 quarters, and livestock 43 times.
- "What would move the score" (built) makes this visible: all farms needs +15.4% to reach GUARDED, crops +29.7%, dairy +56.2%.

### M7. Update workflow failure modes
1. **Fixed.** A driver or farm-gate price USDA had not published became NaN, then "NaN%" on the page. The engine now writes null, refuses NaN in the summary, and the page shows "not published".
2. **Fixed.** Nothing checked that the series were parsed correctly. Publish now refuses if the all-farms ratio drifts more than 1.5 points from USDA's own published ratio in any quarter. Today the mean gap is -0.03 and the largest is 0.83 (Q1'13), so "within about one point" holds.
3. **Fixed.** Revisions to past quarters were silent. They are now listed in the run summary.
4. **Fixed.** No selftests ran in CI. 17 tests now run before preview, publish and stress, and they caught a real bug in the new threshold code before it shipped.
5. **Fixed.** If T1 ever fails on revised data, the footer says NOT VALIDATED, but the hero still said "Tested before launch". The hero now follows the flag.
6. **Open.** `reference_period_desc[:3]` would read "MARKETING YEAR" as March if a non-monthly row ever slipped past `freq_desc=MONTHLY`. Duplicate rows for the same month overwrite each other silently. In the probe, 21,239 duplicate keys are all identical. **Fix:** accept only the 12 month names exactly, and fail on duplicates that disagree.
7. **Open.** A FRED outage blocks the whole publish, because the engine raises before writing anything. That is safe, but the NASS numbers wait on FRED. Acceptable. Note it in the runbook.
8. **Open.** `engine/v4/ffai_v4_report.md` still had the title "(website unchanged)". Fixed in the engine; the file updates on the next run.

## LOW

- **L1.** The regime lines are copied in four places: engine, publish, page JS and badge. The chart shading is computed in the page. Rule 9 says compute in the pipeline: have publish write the label, and have the page and badge read it.
- **L2.** Dairy's 0 is not mainly a cattle-price artifact, as the page implies. Against production items, PITW or PPITW, dairy also scores 0. Only against feed alone does it score 26. **Fix:** compute and show these alternatives (the stress tool already does).
- **L3.** USDA has not updated the seed index since January 2025 (it was not updated in January 2026), and the wage index has been frozen since April 2025. Both sit inside PPITW. If those costs rose, the ratio is slightly overstated. The methodology now mentions seed.
- **L4.** The 1990-94 gap is handled correctly: USDA reported costs in only 4 months a year, so those years are excluded. As a sensitivity test, yearly changes could reach back to 1991 using the 4-month means.
- **L5.** Copy that is written by hand will go stale: "1.2 points a year", "wage index not changed since April 2025", and the seasonality numbers. The dairy numbers now come from data. The stress report prints the rest so they can be checked each quarter.
- **L6.** The badge showed no quarter or base period. Fixed: every size now shows "Q2'26 vs 1995-2019".

---

## Enhancements: what passed honest-numbers

| Idea | Verdict | Status |
|---|---|---|
| "What would move it" table | Plain arithmetic on the base; tested against the engine's own scoring | **Built** (page, `current.json.to_reach`) |
| Ranges for r | Fisher z with eff. n | **Built** (page, meta) |
| Year-ago comparison | Removes the seasonal swing | **Built** |
| CSV download, stable API | Same records as history.json | **Built** (`api/v4/history.csv`, stability note) |
| Badge | Missing quarter; v3 contradicted v4 | **Fixed** |
| Public track record (each year's ratio change vs income change; income under each label) | The data now exists: the engine writes `ffai_v4_annual.csv`, and stress mode builds the label table | **Plumbing built**; publish on the page only after a real run (R1) |
| Monthly nowcast | Two months predict the full quarter's ratio within 0.6% typically (90% within 1.7%), same label 90% of the time. But this uses revised data, and the first print of the latest month is preliminary | **Not built.** Archive first prints for 4+ quarters, then show "months so far", labelled experimental, ratio only (R4) |
| Confidence bands on the score | The score is a fixed transform of published data, so a band would be invented. Revision risk is real but unmeasured | **Rejected** |
| State or regional version | The NASS prices-paid indexes in the probe are national only, so there is no state ratio | **Rejected** for now |
| Plain-language explainer | Seasonality note added; a farmer-facing "what it means for you" needs Sig's voice | **Sig** |

## Recommended, not built
- **R1.** Run the workflow in `stress` mode, then publish the track-record table (yearly ratio change vs real income change, all years, misses included) next to the validation table.
- **R2.** Rename the labels, or demote them (H1).
- **R3.** Mark the in-sample quarters in the chart and API (M4).
- **R4.** Commit each NASS pull to `engine/v4/vintages/` (small CSVs) so revision and nowcast error can be measured from first prints.
- **R5.** Tighten the NASS parse (M7.6). Keep the regime lines in one place (L1).
- **R6.** Add the v3 JSON status field (H2).

---

## Applied (Oct 17, 2026, Sig approved)

- **H1 / R2.** Labels are now LOW / BELOW MIDDLE / ABOVE MIDDLE / HIGH, split at the 1995-2019 quartiles (25 / 50 / 75), always shown with "vs 1995-2019". The headline leads with the ratio and its change from the same quarter a year earlier; the score and label are secondary. Old labels stay in the API as `label_legacy` (version 4.1, documented in the stability note).
- **L1.** The label lines live only in `engine/ffai_v4_labels.py`. Publish writes the label into the JSON; the page and badge read it. A selftest fails if label lines reappear in the page scripts or badge.
- **M5.** The year-ago quarter is the main comparison in the hero, sector tiles, What Moved, farm-gate prices, badge, metadata and commentary. Quarter-to-quarter is secondary and marked partly seasonal.
- **H2 / R6.** `api/v3/current.json`, `history.json`, `meta.json` and `engine/ffai_v3_website.json` carry `status: retired`, `superseded_by` and `retired_note`.
- **M4 / R3.** `real_time` in history.json and history.csv (true from Q2'26, the v4 launch). The chart greys the in-sample 1995-2019 quarters, with a legend.
- **M7.6 / R5.** The NASS parse accepts only the 12 month names and stops on duplicate months that disagree (selftests for both).
- **L2.** Dairy against feed, production items, PITW and PPITW is computed by the engine and shown in the methodology.
- **R1.** Stress run 39001256902 (branch fx/ffai-audit): `engine/stress/stress_report_run_39001256902.md`. Track record: same direction in 24 of 30 years (1996-2025); now on the page with every miss shown. In the 11 LOW years, real net farm income was above its 1995-2019 median in 6. The ALFRED vintage check failed (HTTP 400); the stress tool now skips years ALFRED refuses.

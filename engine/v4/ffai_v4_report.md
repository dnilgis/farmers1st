# FFAI v4 build report (website unchanged)

- NASS data: Jan 1908 to Aug 2026; complete quarters Q1'95 to Q2'26 (126)
- USDA published ratio vs ours, last quarter: USDA 84.7, ours 84.5
- FRED: net farm income 1967-2025, subsidies 1960-2025

## Pre-registered validation (annual, year-over-year changes)

Measures use the all-farms ratio. A = log ratio; B = log(ratio / previous 40-quarter average). Annual value = mean of the year's 4 quarters (years with all 4 only).

| Cand. | Test | Result | Sample | p | Verdict |
|---|---|---|---|---|---|
| A | corr with change in real net farm income | r = +0.75 | n = 30 years, effective n = 29.3 | one-sided p = 0.000 | PASS |
| A | corr with change in real market income (NFI minus federal ag subsidies) | r = +0.84 | n = 30 years, effective n = 29.8 | one-sided p = 0.000 | PASS |
| A | out-of-sample error, change in log real NFI | model 0.173 vs no-change 0.221 vs last-year 0.320 | 20 test years | | PASS |
| B | corr with change in real net farm income | r = +0.70 | n = 20 years, effective n = 19.6 | one-sided p = 0.000 | PASS |
| B | corr with change in real market income (NFI minus federal ag subsidies) | r = +0.78 | n = 20 years, effective n = 19.7 | one-sided p = 0.000 | PASS |
| B | out-of-sample error, change in log real NFI | model 0.135 vs no-change 0.202 vs last-year 0.252 | 10 test years | | PASS |

Tests passed: A 3/3, B 3/3. Headline uses **A** (validated against real net farm income).
- Reference only: quarterly change in A vs change in national ag loan delinquency: r = -0.03 (n = 125). No claim made.
- Reference only: quarterly change in B vs change in national ag loan delinquency: r = -0.06 (n = 85). No claim made.

## Latest quarter: Q2'26

| Sector | Ratio (2011 = 100) | A (level pct) | B (vs decade pct) | Headline score | Regime |
|---|---|---|---|---|---|
| all | 84.5 | 11.0 | 75.0 | 11.0 | STRESSED |
| crops | 73.4 | 0.0 | 53.3 | 0.0 | STRESSED |
| livestock | 113.9 | 94.0 | 100.0 | 94.0 | STRONG |
| dairy | 60.2 | 0.0 | 10.0 | 0.0 | STRESSED |

## What moved (quarter average, % change)

| Item | vs last quarter | vs a year ago |
|---|---|---|
| Prices: feed grains | +4.4% | -4.8% |
| Prices: oilseeds | +6.7% | +8.6% |
| Prices: food grains | +1.1% | -3.7% |
| Prices: livestock | +5.5% | +14.1% |
| Prices: dairy | +13.9% | -0.9% |
| Costs: feed | +4.5% | +2.7% |
| Costs: fuel | +30.8% | +37.5% |
| Costs: fertilizer | +12.9% | +23.1% |
| Costs: chemicals | +0.8% | -5.6% |
| Costs: seed | +0.0% | +0.0% |
| Costs: interest | +0.0% | -0.8% |
| Costs: wages | +0.0% | +0.0% |
| Costs: cash rent | +0.0% | +3.9% |
| Costs: machinery | +0.3% | +1.4% |

## Farm-gate prices (USDA, quarter average)

| Item | Q2'25 | Q1'26 | Q2'26 |
|---|---|---|---|
| Corn ($/bu) | 4.58 | 4.17 | 4.36 |
| Soybeans ($/bu) | 10.33 | 10.67 | 11.37 |
| Wheat ($/bu) | 5.49 | 5.25 | 5.76 |
| Milk ($/cwt) | 21.27 | 18.50 | 21.07 |
| Steers & heifers ($/cwt) | 221.00 | 238.67 | 253.00 |
| Hogs ($/cwt) | 70.20 | 65.60 | 68.57 |
| Alfalfa hay ($/ton) | 182.67 | 164.67 | 194.67 |

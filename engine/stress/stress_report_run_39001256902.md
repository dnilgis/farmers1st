<!-- Workflow run 39001256902 (stress mode, ref fx/ffai-audit, head 879f578), Oct 17 2026. Copied from the job log: the artifact download is blocked from the audit sandbox. Part 1 is identical to a local rebuild from the probe CSV. -->
# FFAI v4 stress test (publishes nothing)

NASS data Jan 1990 to Aug 2026; complete quarters Q1'95 to Q2'26 (126).

## Part 1: USDA NASS only

- Rebuild vs committed engine CSV: 126 quarters in common; largest ratio gap 0.000, largest score gap 0.0.
- All-farms ratio minus USDA published ratio (USDA rounds to whole numbers): mean -0.03, largest 0.83 (Q1'13), over 125 quarters.

### Latest quarter (Q2'26) under other base periods (score A)

| Base | All | Crops | Livestock | Dairy |
|---|---|---|---|---|
| 1995-2019 (published) | 11 | 0 | 94 | 0 |
| 2000-2019 | 14 | 0 | 92 | 0 |
| 2010-2019 | 28 | 0 | 95 | 0 |
| 1995-2025 | 15 | 6 | 94 | 0 |
| 2005-2024 | 22 | 4 | 98 | 0 |
| 2016-2025 | 45 | 18 | 98 | 0 |

Trend in the all-farms ratio over the base: -1.20 points a year.

### How often each label has been true (quarters)

| Sector | Score | Whole history | 2020 on |
|---|---|---|---|
| all | A | LOW 46, BELOW MIDDLE 29, ABOVE MIDDLE 25, HIGH 26 | LOW 22, BELOW MIDDLE 4, ABOVE MIDDLE 0, HIGH 0 |
| all | B | LOW 16, BELOW MIDDLE 21, ABOVE MIDDLE 16, HIGH 33 | LOW 2, BELOW MIDDLE 6, ABOVE MIDDLE 1, HIGH 17 |
| crops | A | LOW 44, BELOW MIDDLE 31, ABOVE MIDDLE 25, HIGH 26 | LOW 20, BELOW MIDDLE 6, ABOVE MIDDLE 0, HIGH 0 |
| crops | B | LOW 16, BELOW MIDDLE 24, ABOVE MIDDLE 21, HIGH 25 | LOW 2, BELOW MIDDLE 9, ABOVE MIDDLE 6, HIGH 9 |
| livestock | A | LOW 37, BELOW MIDDLE 28, ABOVE MIDDLE 28, HIGH 33 | LOW 13, BELOW MIDDLE 3, ABOVE MIDDLE 3, HIGH 7 |
| livestock | B | LOW 20, BELOW MIDDLE 22, ABOVE MIDDLE 17, HIGH 27 | LOW 6, BELOW MIDDLE 7, ABOVE MIDDLE 2, HIGH 11 |
| dairy | A | LOW 44, BELOW MIDDLE 30, ABOVE MIDDLE 26, HIGH 26 | LOW 20, BELOW MIDDLE 5, ABOVE MIDDLE 1, HIGH 0 |
| dairy | B | LOW 21, BELOW MIDDLE 22, ABOVE MIDDLE 18, HIGH 25 | LOW 7, BELOW MIDDLE 7, ABOVE MIDDLE 3, HIGH 9 |

All-farms score A, yearly average: 1995 94, 1996 98, 1997 90, 1998 83, 1999 67, 2000 54, 2001 63, 2002 45, 2003 66, 2004 82, 2005 53, 2006 34, 2007 72, 2008 59, 2009 23, 2010 36, 2011 50, 2012 52, 2013 51, 2014 34, 2015 18, 2016 10, 2017 15, 2018 7, 2019 6, 2020 2, 2021 13, 2022 29, 2023 14, 2024 14, 2025 18, 2026 6

### Published scores vs what a reader saw at the time (2000-2019)

Published scores rank 1995-2019 quarters against the whole period, later years included. Ranked only against quarters already published (from 1995), the score differs by 21.3 points on average (published minus real time +21.3); the label differs in 48 of 80 quarters. From 2020 on the base is entirely in the past, so those scores are real time.

### The two pre-registered candidates

Both passed all three tests. Their labels differ in 62 of 86 quarters; in 13 one says LOW and the other HIGH. Latest: A 11 LOW, B 75 HIGH. The tests checked changes, not levels, so they cannot say which label is right.

### Seasonality (mean % above or below the trend, by quarter, with standard error)

| Sector | Q1 | Q2 | Q3 | Q4 |
|---|---|---|---|---|
| all | -1.2 (0.3) | +1.7 (0.4) | +1.1 (0.3) | -1.4 (0.5) |
| crops | -1.9 (0.4) | +2.7 (0.4) | +1.7 (0.4) | -2.4 (0.5) |
| livestock | -0.5 (0.4) | +1.9 (0.5) | +0.5 (0.5) | -1.9 (0.6) |
| dairy | -2.2 (0.8) | -4.0 (1.1) | +1.0 (1.0) | +5.2 (0.7) |

Mean all-farms score by quarter of year, 1995-2019: Q1 49, Q2 55, Q3 53, Q4 46

### Shock each side of the latest quarter by 5%

| Sector | Now | Received +5% | Received -5% | Paid +5% | Paid -5% |
|---|---|---|---|---|---|
| all | 11 | 16 | 1 | 1 | 16 |
| crops | 0 | 9 | 0 | 0 | 9 |
| livestock | 94 | 100 | 85 | 87 | 100 |
| dairy | 0 | 0 | 0 | 0 | 0 |

### Dairy score under other USDA cost indexes (latest quarter)

| Cost index | Ratio | Score |
|---|---|---|
| Animal sector (published) | 60.2 | 0 |
| Feed only | 93.4 | 26 |
| Production items | 63.7 | 0 |
| Production items, interest, taxes, wages (PITW) | 63.3 | 0 |
| Everything farms pay (PPITW) | 64.1 | 0 |

### A monthly reading between quarters? (all farms)

- First 1 month(s) of the quarter vs the full quarter: typical error 1.3%, 90% of errors within 3.9%, same label 87% of 126 quarters.
- First 2 month(s) of the quarter vs the full quarter: typical error 0.6%, 90% of errors within 1.7%, same label 95% of 126 quarters.
- These use today's revised USDA data. The latest month is preliminary when first published, so a real-time monthly reading would miss by more. Not validated against farm income; experimental only.

## Part 2: against net farm income (FRED)

| Candidate | Variant | T1 r (95% range), n / eff. n, p | T2 r | T3 model vs no change vs last year (test years) |
|---|---|---|---|---|
| A | as published (CPI-U) | +0.75 (0.54 to 0.88), 30 / 29.3, 1e-06 | +0.84 | 0.173 vs 0.221 vs 0.320 (20) |
| A | start 2000 | +0.74 (0.50 to 0.88), 26 / 25.5, 8e-06 | +0.83 | 0.159 vs 0.220 vs 0.320 (16) |
| A | start 2005 | +0.72 (0.42 to 0.88), 21 / 20.9, 0.0001 | +0.81 | 0.133 vs 0.196 vs 0.247 (11) |
| A | without 2020-2022 | +0.76 (0.52 to 0.89), 27 / 25.4, 5e-06 | +0.82 | 0.173 vs 0.217 vs 0.328 (17) |
| A | without 2025 (USDA forecast) | +0.75 (0.53 to 0.88), 29 / 28.4, 2e-06 | +0.84 | 0.177 vs 0.224 vs 0.319 (19) |
| A | no deflator | +0.77 (0.56 to 0.88), 30 / 29.4, 5e-07 | +0.84 | 0.170 vs 0.229 vs 0.325 (20) |
| A | USDA CPI series as deflator | +0.75 (0.54 to 0.88), 30 / 29.3, 1e-06 | +0.84 | 0.173 vs 0.221 vs 0.320 (20) |
| B | as published (CPI-U) | +0.70 (0.36 to 0.87), 20 / 19.6, 0.0004 | +0.78 | 0.135 vs 0.202 vs 0.252 (10) |
| B | start 2000 | +0.70 (0.36 to 0.87), 20 / 19.6, 0.0004 | +0.78 | 0.135 vs 0.202 vs 0.252 (10) |
| B | start 2005 | +0.70 (0.36 to 0.87), 20 / 19.6, 0.0004 | +0.78 | 0.135 vs 0.202 vs 0.252 (10) |
| B | without 2020-2022 | +0.67 (0.26 to 0.88), 17 / 15.6, 0.002 | +0.71 | 0.121 vs 0.182 vs 0.245 (7) |
| B | without 2025 (USDA forecast) | +0.69 (0.34 to 0.87), 19 / 18.7, 0.0006 | +0.79 | 0.139 vs 0.206 vs 0.240 (9) |
| B | no deflator | +0.72 (0.41 to 0.88), 20 / 19.7, 0.0002 | +0.79 | 0.130 vs 0.214 vs 0.257 (10) |
| B | USDA CPI series as deflator | +0.70 (0.36 to 0.87), 20 / 19.6, 0.0004 | +0.78 | 0.135 vs 0.202 vs 0.252 (10) |

Holm correction over the 4 published correlation tests: 4 of 4 still below 0.05.

### Track record: yearly change in the all-farms ratio vs real net farm income (1996-2025)

Same direction in 24 of 30 years. Every year is listed, misses included. Real = deflated by CPI-U (annual average). The latest year of net farm income (2025) is a USDA forecast.

| Year | Ratio change | Real net farm income change | Same direction? | Label (yearly average score, vs 1995-2019) |
|---|---|---|---|---|
| 1996 | +4.5% | +44.0% | yes | HIGH (98) |
| 1997 | -7.2% | -14.9% | yes | HIGH (90) |
| 1998 | -2.5% | -9.6% | yes | HIGH (83) |
| 1999 | -5.3% | -1.0% | yes | ABOVE MIDDLE (67) |
| 2000 | -3.3% | +2.8% | MISS | ABOVE MIDDLE (54) |
| 2001 | +3.2% | +5.3% | yes | ABOVE MIDDLE (63) |
| 2002 | -4.8% | -30.1% | yes | BELOW MIDDLE (45) |
| 2003 | +5.2% | +52.8% | yes | ABOVE MIDDLE (66) |
| 2004 | +5.8% | +39.6% | yes | HIGH (82) |
| 2005 | -8.7% | -12.8% | yes | ABOVE MIDDLE (53) |
| 2006 | -4.8% | -29.4% | yes | BELOW MIDDLE (34) |
| 2007 | +10.4% | +18.5% | yes | ABOVE MIDDLE (72) |
| 2008 | -3.5% | +7.3% | MISS | ABOVE MIDDLE (59) |
| 2009 | -9.5% | -20.0% | yes | LOW (23) |
| 2010 | +4.4% | +22.0% | yes | BELOW MIDDLE (36) |
| 2011 | +3.8% | +42.8% | yes | ABOVE MIDDLE (50) |
| 2012 | +0.1% | -16.8% | MISS | ABOVE MIDDLE (52) |
| 2013 | -0.4% | +26.5% | MISS | ABOVE MIDDLE (51) |
| 2014 | -3.7% | -26.6% | yes | BELOW MIDDLE (34) |
| 2015 | -6.6% | -11.6% | yes | LOW (18) |
| 2016 | -5.5% | -24.6% | yes | LOW (10) |
| 2017 | +3.1% | +18.0% | yes | LOW (15) |
| 2018 | -5.4% | +5.3% | MISS | LOW (7) |
| 2019 | -0.7% | -2.3% | yes | LOW (6) |
| 2020 | -2.3% | +21.1% | MISS | LOW (2) |
| 2021 | +8.6% | +41.4% | yes | LOW (13) |
| 2022 | +8.6% | +15.2% | yes | BELOW MIDDLE (29) |
| 2023 | -7.4% | -22.4% | yes | LOW (14) |
| 2024 | -0.5% | -15.8% | yes | LOW (14) |
| 2025 | +2.7% | +18.1% | yes | LOW (18) |

### Real net farm income in years under each label (all farms, yearly average score A)

| Label | Years | Real NFI above its 1995-2019 middle value | Mean change in log real NFI same year | next year |
|---|---|---|---|---|
| LOW | 11 | 6 of 11 | -0.014 | +0.078 |
| BELOW MIDDLE | 5 | 3 of 5 | -0.135 | +0.115 |
| ABOVE MIDDLE | 10 | 7 of 10 | +0.100 | -0.070 |
| HIGH | 5 | 2 of 5 | +0.026 | -0.009 |

Years overlap and the labels trend with the base, so these are descriptions, not tests.

Vintage check not run: HTTP Error 400: Bad Request


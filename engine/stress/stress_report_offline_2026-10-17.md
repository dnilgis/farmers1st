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
| all | A | STRESSED 65, GUARDED 15, FAVORABLE 15, STRONG 31 | STRESSED 26, GUARDED 0, FAVORABLE 0, STRONG 0 |
| all | B | STRESSED 29, GUARDED 11, FAVORABLE 10, STRONG 36 | STRESSED 6, GUARDED 2, FAVORABLE 1, STRONG 17 |
| crops | A | STRESSED 65, GUARDED 15, FAVORABLE 15, STRONG 31 | STRESSED 26, GUARDED 0, FAVORABLE 0, STRONG 0 |
| crops | B | STRESSED 27, GUARDED 18, FAVORABLE 13, STRONG 28 | STRESSED 4, GUARDED 9, FAVORABLE 4, STRONG 9 |
| livestock | A | STRESSED 53, GUARDED 17, FAVORABLE 17, STRONG 39 | STRESSED 14, GUARDED 2, FAVORABLE 2, STRONG 8 |
| livestock | B | STRESSED 36, GUARDED 9, FAVORABLE 9, STRONG 32 | STRESSED 13, GUARDED 0, FAVORABLE 0, STRONG 13 |
| dairy | A | STRESSED 64, GUARDED 16, FAVORABLE 15, STRONG 31 | STRESSED 25, GUARDED 1, FAVORABLE 0, STRONG 0 |
| dairy | B | STRESSED 34, GUARDED 12, FAVORABLE 10, STRONG 30 | STRESSED 11, GUARDED 3, FAVORABLE 1, STRONG 11 |

All-farms score A, yearly average: 1995 94, 1996 98, 1997 90, 1998 83, 1999 67, 2000 54, 2001 63, 2002 45, 2003 66, 2004 82, 2005 53, 2006 34, 2007 72, 2008 59, 2009 23, 2010 36, 2011 50, 2012 52, 2013 51, 2014 34, 2015 18, 2016 10, 2017 15, 2018 7, 2019 6, 2020 2, 2021 13, 2022 29, 2023 14, 2024 14, 2025 18, 2026 6

### Published scores vs what a reader saw at the time (2000-2019)

Published scores rank 1995-2019 quarters against the whole period, later years included. Ranked only against quarters already published (from 1995), the score differs by 21.3 points on average (published minus real time +21.3); the label differs in 40 of 80 quarters. From 2020 on the base is entirely in the past, so those scores are real time.

### The two pre-registered candidates

Both passed all three tests. Their labels differ in 49 of 86 quarters; in 17 one says STRESSED and the other STRONG. Latest: A 11 STRESSED, B 75 STRONG. The tests checked changes, not levels, so they cannot say which label is right.

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
| Production items, interest, taxes, wages | 63.3 | 0 |
| Everything farms pay (PPITW) | 64.1 | 0 |

### A monthly reading between quarters? (all farms)

- First 1 month(s) of the quarter vs the full quarter: typical error 1.3%, 90% of errors within 3.9%, same label 83% of 126 quarters.
- First 2 month(s) of the quarter vs the full quarter: typical error 0.6%, 90% of errors within 1.7%, same label 90% of 126 quarters.
- These use today's revised USDA data. The latest month is preliminary when first published, so a real-time monthly reading would miss by more. Not validated against farm income; experimental only.

## Part 2: against net farm income (FRED)

FRED_API_KEY not set, so the income tests were not re-run here. Run the workflow in stress mode to get them.


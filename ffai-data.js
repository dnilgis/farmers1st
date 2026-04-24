// ===============================================================
// FFAI v3.0 DATA -- QUARTERLY INDEX + EDITORIAL CONTENT
// ===============================================================
//
// HOW TO UPDATE:
//   1. Run: python ffai_v3_engine.py   (generates CSV + JSON)
//   2. Copy latest scores into "current" section below
//   3. Append new quarter to "history" array
//   4. Update editorial sections (headline, signals, actions)
//   5. Commit -> push -> site updates
//
// COMPLIANCE NOTE (Apr 2026):
//   - All deadlines must be current at time of publish
//   - Do not attribute subsidy changes to unverified legislation
//   - Advisory language must not be absolute ("non-negotiable" etc.)
//   - See CHANGES.md for full audit trail
// ===============================================================

var FFAI = {

  // -- Current Quarter (paste from engine output) ---------------
  quarter:  "Q1'26",
  date:     "Q1 2026",
  updated:  "April 24, 2026",
  nextUpdate: "JUL '26",

  composite:  67.3,
  prevComp:   67.9,
  regime:     "FAVORABLE",

  grain:       9.7,
  dairy:      10.8,
  livestock:  92.5,
  outlook:    60.6,

  prevGrain:      9.8,
  prevDairy:     51.1,
  prevLivestock: 94.6,
  prevOutlook:   61.4,

  // -- Quarterly History (from ffai_v3_engine.py CSV) -----------
  // Format: [label, composite, grain, dairy, livestock]
  history: [
    ["Q1'08",55.1,100.0,4.8,4.8],
    ["Q2'08",49.5,95.5,4.5,9.1],
    ["Q3'08",54.0,91.3,13.0,100.0],
    ["Q4'08",19.1,87.5,100.0,12.5],
    ["Q1'09",21.8,96.0,12.0,12.0],
    ["Q2'09",31.1,96.2,3.8,15.4],
    ["Q3'09",24.8,85.2,18.5,11.1],
    ["Q4'09",18.3,82.1,25.0,10.7],
    ["Q1'10",9.9,75.9,27.6,100.0],
    ["Q2'10",6.6,70.0,30.0,100.0],
    ["Q3'10",4.0,87.1,96.8,96.8],
    ["Q4'10",5.8,96.9,25.0,87.5],
    ["Q1'11",5.7,100.0,21.2,97.0],
    ["Q2'11",2.7,97.1,94.1,97.1],
    ["Q3'11",3.1,88.6,100.0,97.1],
    ["Q4'11",0.1,72.2,94.4,97.2],
    ["Q1'12",5.2,75.7,18.9,97.3],
    ["Q2'12",13.8,78.9,15.8,86.8],
    ["Q3'12",26.5,100.0,17.9,79.5],
    ["Q4'12",20.9,85.0,97.5,80.0],
    ["Q1'13",22.3,80.5,34.1,80.5],
    ["Q2'13",26.1,73.8,88.1,81.0],
    ["Q3'13",25.4,55.8,88.4,93.0],
    ["Q4'13",22.4,52.3,100.0,97.7],
    ["Q1'14",27.5,53.3,100.0,100.0],
    ["Q2'14",37.2,56.5,97.8,100.0],
    ["Q3'14",18.7,2.1,100.0,100.0],
    ["Q4'14",12.3,4.2,97.9,97.9],
    ["Q1'15",14.8,53.1,87.8,91.8],
    ["Q2'15",16.5,46.0,88.0,92.0],
    ["Q3'15",18.6,47.1,90.2,90.2],
    ["Q4'15",18.8,46.2,92.3,67.3],
    ["Q1'16",24.1,52.8,84.9,69.8],
    ["Q2'16",33.4,61.1,70.4,63.0],
    ["Q3'16",32.9,43.6,89.1,61.8],
    ["Q4'16",33.6,5.4,89.3,51.8],
    ["Q1'17",37.6,43.9,89.5,59.6],
    ["Q2'17",37.3,3.4,82.8,65.5],
    ["Q3'17",40.6,3.4,89.8,62.7],
    ["Q4'17",41.6,1.7,85.0,53.3],
    ["Q1'18",45.4,3.3,62.3,55.7],
    ["Q2'18",47.8,3.2,64.5,48.4],
    ["Q3'18",43.9,1.6,66.7,47.6],
    ["Q4'18",48.0,3.1,70.3,45.3],
    ["Q1'19",50.7,4.6,67.7,52.3],
    ["Q2'19",48.8,4.5,77.3,57.6],
    ["Q3'19",46.5,7.5,88.1,47.8],
    ["Q4'19",42.2,11.8,94.1,47.1],
    ["Q1'20",37.0,20.3,85.5,55.1],
    ["Q2'20",23.0,70.0,67.1,58.6],
    ["Q3'20",26.1,64.8,93.0,46.5],
    ["Q4'20",34.2,81.9,84.7,52.8],
    ["Q1'21",44.7,89.0,12.3,11.0],
    ["Q2'21",49.0,91.9,12.2,58.1],
    ["Q3'21",43.4,76.0,16.0,64.0],
    ["Q4'21",39.4,63.2,65.8,52.6],
    ["Q1'22",53.5,75.3,85.7,11.7],
    ["Q2'22",67.0,71.8,84.6,11.5],
    ["Q3'22",76.1,46.8,75.9,64.6],
    ["Q4'22",87.8,16.2,73.8,11.2],
    ["Q1'23",99.8,19.8,19.8,13.6],
    ["Q2'23",99.9,14.6,11.0,69.5],
    ["Q3'23",100.0,1.2,19.3,85.5],
    ["Q4'23",95.4,1.2,59.5,65.5],
    ["Q1'24",89.6,1.2,57.6,72.9],
    ["Q2'24",88.1,2.3,75.6,95.3],
    ["Q3'24",80.8,1.1,95.4,95.4],
    ["Q4'24",72.1,4.5,94.3,86.4],
    ["Q1'25",70.3,6.7,83.1,94.4],
    ["Q2'25",70.9,7.8,70.0,97.8],
    ["Q3'25",69.3,2.2,72.5,100.0],
    ["Q4'25",67.9,9.8,51.1,94.6],
    ["Q1'26",67.3,9.7,10.8,92.5]
  ],

  // -- USDA Outlook Flash Bar -----------------------------------
  // COMPLIANCE: Keep current. Remove dated FBA/deadline references each update cycle.
  outlookFlash: 'Q1\u002726 UPDATE \u2014 DAIRY COLLAPSES TO 10.8 STRESSED \u00B7 Composite 67.3 FAVORABLE \u00B7 Grain 9.7 flat \u00B7 Livestock 92.5 STRONG \u00B7 Fed Funds 3.64% \u00B7 Crude $91/bbl \u00B7 Raw milk PPI crashed to 127 \u00B7 July 15 acreage reporting next',

  // -- Editorial: Report ----------------------------------------
  headline: "Dairy Hit the Wall. Everything Else Held.",
  intro: [
    "FFAI composite at <strong>67.3 FAVORABLE</strong> \u2014 down 0.6 from Q4. National ag conditions still decent but the dairy sub-index just collapsed. <strong>10.8 STRESSED</strong> \u2014 down 40 points in one quarter. The Jan Class III $14.59 we flagged in February is now fully visible in the data.",
    "<strong>Grain at 9.7 STRESSED</strong> \u2014 flat, still stuck at breakeven. Soybeans jumped to $427/mt on the quarter but crude oil surged to $91/bbl, pushing diesel PPI to 439. Input costs ate the revenue gain. <strong>Livestock at 92.5 STRONG</strong> \u2014 cattle PPI at 370.7, near all-time highs. <strong>Outlook at 60.6 FAVORABLE</strong> \u2014 Fed holding at 3.64%, easing from 2023 peak."
  ],

  signals: [
    ["Dairy Collapse",              "BEARISH",        "a", "Sub-index crashed from 51.1 to 10.8 in one quarter \u2014 largest single-quarter drop in FFAI history. Raw milk PPI fell to 127 (was 150). Cheese PPI down to 205. Dairy margin went negative (-0.46 z-scores). Recovery depends on herd contraction accelerating."],
    ["Crude Oil Spike",             "BEARISH GRAIN",  "a", "WTI crude surged to $91/bbl in Q1 (was $60 in Q4). Diesel PPI jumped to 439. This crushes grain margins through energy and transportation costs. If crude sustains above $80, grain sub-index stays pinned."],
    ["Soybean Strength",            "BULLISH",        "g", "Soybeans at $427/mt ($11.60/bu equiv) \u2014 up from $380 range. Biofuel demand (45Z, RFS) driving crush. But SCOTUS tariff ruling clouds China trade. Domestic crush is the real story now."],
    ["Cattle Supply Crunch",        "BULLISH",        "g", "Cattle PPI at 370.7, near all-time highs. Herd 86.2M, lowest since 1951. COF placements -5%. Livestock margin at 1.86 z-scores above mean. Watch consumer pushback above $9.50/lb retail."],
    ["Rate Trajectory",             "FAVORABLE",      "g", "Fed Funds at 3.64%, down from 5.33 peak. 10Y Treasury at 4.25%. Each quarter of cuts helps farmer debt service 4-5 quarters out. Outlook sub-index at 60.6 reflects continued easing."],
    ["Drought Watch",               "WATCH",          "a", "62% Midwest drought entering planting. SWE lowest since 1986. If persists into pollination, grain sub-index could move sharply higher on supply shock."]
  ],

  // COMPLIANCE NOTE on actions:
  // - Do not use absolute advisory language ("non-negotiable", "must", etc.)
  // - Do not reference deadlines that have passed
  // - Subsidy changes: cite RMA bulletin numbers, not bill names, unless bill is fully enacted and verifiable
  // - General market info is not advice specific to any producer's situation
  actions: [
    ["Dairy DRP: highest priority right now",
     "Sub-index at 10.8 \u2014 margins negative. 85-90% coverage on 60-70% of quarterly milk production. Match Class III/IV. Call us to evaluate your specific DRP structure for Q2-Q3. This is the most important insurance decision for dairy operations right now."],

    ["Protect grain downside",
     "Grain at 9.7 STRESSED. Crude oil at $91 is compressing margins further. RP at higher coverage levels. 2026 RMA subsidy schedule increased ECO/SCO subsidies \u2014 call us for current rates. COP $917/ac corn."],

    ["Don\u2019t cap bean upside",
     "Soybeans strengthening on biofuel demand despite SCOTUS uncertainty. 45Z, E15, RFS are the catalysts. Domestic crush at record. Expect headline volatility but trend is up."],

    ["Cattle: lock some revenue on strength",
     "Livestock at 92.5 but crude oil spike adds input cost pressure. LRP sets floor, keeps upside. COF confirms tight supply. Consider locking Q3-Q4 revenue."],

    ["Watch crude oil trajectory",
     "WTI at $91 changes the math on everything \u2014 diesel, fertilizer, transportation. If sustains above $80, grain margins compress further. Factor energy costs into forward contracting decisions."],

    ["July 15: acreage reporting deadline",
     "Report all planted acres by July 15 to maintain crop insurance coverage. Late or inaccurate reporting can void your policy. Call us if you have questions about reporting requirements."],

    ["Next FFAI update: July 2026",
     "Q2\u201926 data. Will show whether dairy bottoms or deepens, and whether crude oil spike persists. Run ffai_data_check.py after July 20."]
  ],

  closingLine: "Dairy hit the wall. Everything else held.",
  closingSub: "Protect the downside. The data is clear. Market information above is general in nature \u2014 contact us for guidance specific to your operation."
};

// ===============================================================
// FFAI v3.0 DATA -- QUARTERLY INDEX + EDITORIAL CONTENT
// ===============================================================
//
// HOW TO UPDATE (browser only, since Oct 2026):
//   1. GitHub > Actions > "FFAI quarterly update" > Run workflow > preview
//      (runs engine/ffai_v3_engine.py, shows the new scores, changes nothing)
//   2. Same, with publish: writes the numbers below, api/v3, meta tags and
//      og-share.png, and commits. Numbers come only from the engine.
//   3. Commentary (headline, intro, signals, actions) is written by hand.
//      When it is rewritten for the new quarter, set editorialQuarter to it.
//
// COMPLIANCE NOTE (Apr 2026):
//   - All deadlines must be current at time of publish (checked Oct 6, 2026)
//   - No superlatives ("largest ever", "lowest since") unless computed from history
//   - Do not attribute subsidy changes to unverified legislation
//   - Advisory language must not be absolute ("non-negotiable" etc.)
//   - See CHANGES.md for full audit trail
// ===============================================================

var FFAI = {

  // -- Current Quarter (paste from engine output) ---------------
  quarter:  "Q2'26",
  date:     "Q2 2026",
  updated:  "October 6, 2026",
  publishedISO: "2026-10-06",   // drives the "readings are old" banner (shows after 120 days)
  nextUpdate: "OCT '26",        // set to e.g. "JAN '27" when you publish

  composite:  69.7,
  prevComp:   67.4,
  regime:     "FAVORABLE",   // page now computes this from composite; keep for reference

  grain:       1.1,
  dairy:      50.0,
  livestock:  94.7,
  // Outlook withheld Oct 2026 (points the wrong way against its own test).
  outlook:    null,

  prevGrain:      9.7,
  prevDairy:     19.4,
  prevLivestock: 92.5,
  prevOutlook:   null,

  // Quarter the headline/intro/signals/actions below were written for.
  // When the scores move to a newer quarter, the page labels this commentary
  // as older and builds the flash bar from the numbers instead.
  editorialQuarter: "Q1'26",
  editorialPublished: "April 24, 2026",   // date the commentary below was written

  // -- Quarterly History (from ffai_v3_engine.py CSV) -----------
  // Format: [label, composite, grain, dairy, livestock]
  history: [
    ["Q1'08",55.2,100.0,4.8,4.8],
    ["Q2'08",49.6,95.5,4.5,9.1],
    ["Q3'08",54.1,91.3,13.0,100.0],
    ["Q4'08",19.1,87.5,100.0,12.5],
    ["Q1'09",21.8,96.0,12.0,12.0],
    ["Q2'09",31.2,96.2,3.8,15.4],
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
    ["Q2'12",13.9,78.9,15.8,86.8],
    ["Q3'12",26.5,100.0,17.9,79.5],
    ["Q4'12",20.9,85.0,97.5,80.0],
    ["Q1'13",22.3,80.5,34.1,80.5],
    ["Q2'13",26.1,73.8,88.1,81.0],
    ["Q3'13",25.4,55.8,88.4,93.0],
    ["Q4'13",22.5,52.3,100.0,97.7],
    ["Q1'14",27.5,53.3,100.0,100.0],
    ["Q2'14",37.3,56.5,97.8,100.0],
    ["Q3'14",18.7,2.1,100.0,100.0],
    ["Q4'14",12.3,4.2,97.9,97.9],
    ["Q1'15",14.8,53.1,87.8,91.8],
    ["Q2'15",16.5,46.0,88.0,92.0],
    ["Q3'15",18.6,47.1,90.2,90.2],
    ["Q4'15",18.8,46.2,92.3,67.3],
    ["Q1'16",24.1,52.8,84.9,69.8],
    ["Q2'16",33.4,61.1,70.4,63.0],
    ["Q3'16",32.9,43.6,89.1,61.8],
    ["Q4'16",33.7,5.4,89.3,51.8],
    ["Q1'17",37.6,43.9,89.5,59.6],
    ["Q2'17",37.3,3.4,82.8,65.5],
    ["Q3'17",40.6,3.4,89.8,62.7],
    ["Q4'17",41.6,1.7,85.0,53.3],
    ["Q1'18",45.4,3.3,62.3,55.7],
    ["Q2'18",47.9,3.2,64.5,48.4],
    ["Q3'18",44.0,1.6,66.7,47.6],
    ["Q4'18",48.1,3.1,70.3,45.3],
    ["Q1'19",50.7,4.6,67.7,52.3],
    ["Q2'19",48.9,4.5,77.3,57.6],
    ["Q3'19",46.6,7.5,88.1,47.8],
    ["Q4'19",42.3,11.8,94.1,47.1],
    ["Q1'20",37.1,20.3,85.5,55.1],
    ["Q2'20",23.0,70.0,67.1,58.6],
    ["Q3'20",26.1,64.8,93.0,46.5],
    ["Q4'20",34.2,81.9,84.7,52.8],
    ["Q1'21",44.8,89.0,12.3,11.0],
    ["Q2'21",49.1,91.9,12.2,58.1],
    ["Q3'21",43.5,76.0,16.0,64.0],
    ["Q4'21",39.4,63.2,65.8,52.6],
    ["Q1'22",53.6,75.3,85.7,11.7],
    ["Q2'22",67.1,71.8,84.6,11.5],
    ["Q3'22",76.2,46.8,75.9,64.6],
    ["Q4'22",87.9,16.2,73.8,11.2],
    ["Q1'23",99.9,19.8,19.8,13.6],
    ["Q2'23",99.9,14.6,11.0,69.5],
    ["Q3'23",100.0,1.2,19.3,85.5],
    ["Q4'23",95.4,1.2,59.5,65.5],
    ["Q1'24",89.6,1.2,57.6,72.9],
    ["Q2'24",88.2,2.3,75.6,95.3],
    ["Q3'24",80.8,1.1,95.4,95.4],
    ["Q4'24",72.1,4.5,94.3,86.4],
    ["Q1'25",70.3,6.7,83.1,94.4],
    ["Q2'25",71.0,7.8,70.0,97.8],
    ["Q3'25",69.3,2.2,72.5,100.0],
    ["Q4'25",67.9,9.8,51.1,94.6],
    ["Q1'26",67.4,9.7,19.4,92.5],
    ["Q2'26",69.7,1.1,50.0,94.7]
  ],

  // -- USDA Outlook Flash Bar -----------------------------------
  // COMPLIANCE: Keep current. Remove dated FBA/deadline references each update cycle.
  outlookFlash: 'Q1\u002726 FFAI \u2014 COMPOSITE 67.3 FAVORABLE \u00B7 Dairy 10.8 STRESSED \u00B7 Grain 9.7 STRESSED \u00B7 Livestock 92.5 STRONG \u00B7 Q2\u002726 update pending \u00B7 Next insurance deadline: Dec 1 PRF sales closing',

  // -- Editorial: Report ----------------------------------------
  headline: "Dairy Hit the Wall. Everything Else Held.",
  intro: [
    "FFAI composite at <strong>67.3 FAVORABLE</strong> \u2014 down 0.6 from Q4. National ag conditions still decent but the dairy sub-index just collapsed. <strong>10.8 STRESSED</strong> \u2014 down 40 points in one quarter. The Jan Class III $14.59 we flagged in February is now fully visible in the data.",
    "<strong>Grain at 9.7 STRESSED</strong> \u2014 flat, still stuck at breakeven. Soybeans jumped to $427/mt on the quarter but crude oil surged to $91/bbl, pushing diesel PPI to 439. Input costs ate the revenue gain. <strong>Livestock at 92.5 STRONG</strong> \u2014 cattle PPI at 370.7, near all-time highs."
  ],

  signals: [
    ["Dairy Collapse",              "BEARISH",        "a", "Sub-index fell from 51.1 to 10.8 in one quarter. Raw milk prices (producer price index) fell to 127 from 150, cheese to 205. The dairy margin measure dropped below its long-run average. Recovery depends on herd contraction."],
    ["Crude Oil Spike",             "BEARISH GRAIN",  "a", "WTI crude surged to $91/bbl in Q1 (was $60 in Q4). Diesel PPI jumped to 439. This crushes grain margins through energy and transportation costs. If crude sustains above $80, grain sub-index stays pinned."],
    ["Soybean Strength",            "BULLISH",        "g", "Soybeans at $427/mt ($11.60/bu equiv) \u2014 up from $380 range. Biofuel demand (45Z, RFS) driving crush. But SCOTUS tariff ruling clouds China trade. Domestic crush is the real story now."],
    ["Cattle Supply Crunch",        "BULLISH",        "g", "Cattle producer price index at 370.7, near all-time highs. Herd 86.2M, lowest since 1951. Cattle on Feed placements -5%. Livestock margin measure well above its long-run average. Watch consumer pushback above $9.50/lb retail."],
    ["Rate Trajectory",             "WATCH",          "a", "Fed Funds at 3.64%, down from the 5.33% peak. 10Y Treasury at 4.25%. Lower rates cut the cost of carrying debt. In our data, though, rate cuts have tended to come before higher farm loan delinquency, because the Fed cuts when the economy weakens."],
    ["Drought Watch",               "WATCH",          "a", "62% Midwest drought entering planting. SWE lowest since 1986. If it had persisted into pollination, a smaller crop would lift prices but cut yields. Coverage, not price, protects the bushels you lose."]
  ],

  // COMPLIANCE NOTE on actions:
  // - Do not use absolute advisory language ("non-negotiable", "must", etc.)
  // - Do not reference deadlines that have passed
  // - Subsidy changes: cite RMA bulletin numbers, not bill names, unless bill is fully enacted and verifiable
  // - General market info is not advice specific to any producer's situation
  actions: [
    ["Dairy DRP: highest priority right now",
     "Sub-index at 10.8 \u2014 margins negative. 85-90% coverage on 60-70% of quarterly milk production. Match Class III/IV. Call us to evaluate DRP for the quarters still open for purchase."],

    ["Protect grain downside",
     "Grain at 9.7 STRESSED. Crude oil at $91 is compressing margins further. RP at higher coverage levels. For 2026, SCO and ECO premiums are subsidized at 80%. COP $917/ac corn."],

    ["Don\u2019t cap bean upside",
     "Soybeans strengthening on biofuel demand despite SCOTUS uncertainty. 45Z, E15, RFS are the catalysts. Domestic crush at record. Expect headline volatility but trend is up."],

    ["Cattle: lock some revenue on strength",
     "Livestock at 92.5 but crude oil spike adds input cost pressure. LRP sets floor, keeps upside. COF confirms tight supply. Consider locking some revenue on strength."],

    ["Watch crude oil trajectory",
     "WTI at $91 changes the math on everything \u2014 diesel, fertilizer, transportation. If sustains above $80, grain margins compress further. Factor energy costs into forward contracting decisions."],

    ["Next insurance deadlines",
     "Dec 1: PRF sales closing. Dec 10: end of insurance period for corn and soybeans. Crop damage: notify us within 72 hours of finding it. Call us with questions."]
  ],

  closingLine: "Dairy hit the wall. Everything else held.",
  closingSub: "Protect the downside. The data is clear. Market information above is general in nature \u2014 contact us for guidance specific to your operation."
};

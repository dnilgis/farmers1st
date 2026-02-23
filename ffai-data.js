// ═══════════════════════════════════════════════════════════════
// FFAI v3.0 DATA — QUARTERLY INDEX + EDITORIAL CONTENT
// ═══════════════════════════════════════════════════════════════
//
// HOW TO UPDATE:
//   1. Run: python ffai_v3_engine.py   (generates CSV + JSON)
//   2. Copy latest scores into "current" section below
//   3. Append new quarter to "history" array
//   4. Update editorial sections (headline, signals, actions)
//   5. Commit → push → site updates
//
// ═══════════════════════════════════════════════════════════════

var FFAI = {

  // ── Current Quarter (paste from engine output) ──────────────
  quarter:  "Q4'25",
  date:     "Q4 2025",
  updated:  "February 23, 2026",
  nextUpdate: "APR '26",

  composite:  68.0,
  prevComp:   69.3,
  regime:     "FAVORABLE",

  grain:       9.8,
  dairy:      53.3,
  livestock:  94.6,
  outlook:    61.4,

  prevGrain:      2.2,
  prevDairy:     72.5,
  prevLivestock: 100.0,
  prevOutlook:   64.0,

  // ── Quarterly History (from ffai_v3_engine.py CSV) ───────────
  // Format: [label, composite, grain, dairy, livestock]
  history: [
    ["Q1'08",55.2,100.0,4.8,4.8],
    ["Q2'08",49.5,95.5,4.5,9.1],
    ["Q3'08",54.0,91.3,13.0,100.0],
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
    ["Q2'12",13.8,78.9,15.8,86.8],
    ["Q3'12",26.5,100.0,17.9,79.5],
    ["Q4'12",20.9,85.0,97.5,80.0],
    ["Q1'13",22.3,80.5,34.1,80.5],
    ["Q2'13",26.1,73.8,88.1,81.0],
    ["Q3'13",25.4,55.8,88.4,93.0],
    ["Q4'13",22.4,52.3,100.0,97.7],
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
    ["Q4'18",48.0,3.1,70.3,45.3],
    ["Q1'19",50.7,4.6,67.7,52.3],
    ["Q2'19",48.8,4.5,77.3,57.6],
    ["Q3'19",46.6,7.5,88.1,47.8],
    ["Q4'19",42.3,11.8,94.1,47.1],
    ["Q1'20",37.1,20.3,85.5,55.1],
    ["Q2'20",23.0,70.0,67.1,58.6],
    ["Q3'20",26.1,64.8,93.0,46.5],
    ["Q4'20",34.2,81.9,84.7,52.8],
    ["Q1'21",44.8,89.0,12.3,11.0],
    ["Q2'21",49.0,91.9,12.2,58.1],
    ["Q3'21",43.4,76.0,16.0,64.0],
    ["Q4'21",39.4,63.2,65.8,52.6],
    ["Q1'22",53.6,75.3,85.7,11.7],
    ["Q2'22",67.1,71.8,84.6,11.5],
    ["Q3'22",76.2,46.8,75.9,64.6],
    ["Q4'22",87.9,16.2,73.8,11.2],
    ["Q1'23",99.9,19.8,19.8,13.6],
    ["Q2'23",99.8,14.6,11.0,69.5],
    ["Q3'23",100.0,1.2,19.3,85.5],
    ["Q4'23",95.4,1.2,59.5,65.5],
    ["Q1'24",89.6,1.2,57.6,72.9],
    ["Q2'24",88.1,2.3,75.6,95.3],
    ["Q3'24",80.8,1.1,95.4,95.4],
    ["Q4'24",72.1,4.5,94.3,86.4],
    ["Q1'25",70.3,6.7,83.1,94.4],
    ["Q2'25",70.9,7.8,70.0,97.8],
    ["Q3'25",69.3,2.2,72.5,100.0],
    ["Q4'25",68.0,9.8,53.3,94.6]
  ],

  // ── USDA Outlook Flash Bar ──────────────────────────────────
  outlookFlash: 'SCOTUS TARIFF RULING FEB 20 \u2014 IEEPA TARIFFS STRUCK DOWN \u00B7 China soybean commitments in doubt \u00B7 10% Section 122 replacement \u00B7 FBA signup open \u00B7 USDA AOF 2/19: Corn 94M ac / $4.20 \u00B7 Beans 85M ac / $10.30 \u00B7 Cattle $240 \u00B7 Milk $18.95',

  // ── Editorial: Report ───────────────────────────────────────
  headline: "SCOTUS Changed the Game. The Farm Economy Didn\u2019t Blink.",
  intro: [
    "FFAI composite at <strong>68.0 FAVORABLE</strong> \u2014 national ag conditions decent but slipping from the 2023 peak. The Supreme Court struck down IEEPA tariffs Feb 20. China\u2019s 25M-ton soybean pledge is now leverage without a lever. Markets shrugged. The real story is still sector divergence.",
    "<strong>Grain at 9.8 STRESSED.</strong> Cost of production $917/ac. Most WI/MN corn at or below breakeven. <strong>Dairy in recession</strong> \u2014 Jan Class III actual $14.59, well below USDA\u2019s $16.65 forecast. <strong>Livestock at 94.6 STRONG</strong> \u2014 COF placements -5%, herd lowest since 1951, cash cattle $242-245. FBA signup open today."
  ],

  signals: [
    ["SCOTUS / Trade Policy",     "BEARISH BEANS",  "a", "IEEPA tariffs struck down Feb 20. China\u2019s 25M-ton purchase pledge loses enforcement. 10% Section 122 replacement. If China walks back 8M-ton additional buy (~294M bu), ending stocks exceed 400M bu. Biofuel policy (45Z, E15, RFS) now primary upside driver, not China."],
    ["Dollar / Export Demand",    "BULLISH CORN",   "g", "DXY down 13% to 98.7. Corn exports raised to record 3.3B bu. India-US deal opens new demand. Dollar weakness historically precedes 15-20% grain price improvement."],
    ["Dairy Recession",           "BEARISH",        "a", "Jan Class III actual $14.59/cwt. All-milk $18.95 vs COP $19.14. Most WI herds need $18-19 to break even. Culling up 3.2% YoY. Herd 9.540M. Recovery path H2 via supply correction."],
    ["Cattle Supply Crunch",      "BULLISH",        "g", "COF report 2/21: on-feed 11.5M (-2% YoY), placements -5% below trade estimates. Cash $242-245. Feeders $377. Herd 86.2M, lowest since 1951. MX border closed (screwworm). Demand strongest since 1983."],
    ["WASDE / Drought",           "TURNING",        "a", "Feb WASDE cut corn stocks 100M bu. 62% Midwest drought expanding. SWE lowest since 1986. If persists into planting, supply picture changes fast."],
    ["Equipment / Profitability", "BOTTOMING",      "g", "Deere ATH $593, called 2026 cycle bottom. Titan Machinery $14.30 still distressed. When TITN turns, sector confirmed."]
  ],

  actions: [
    ["Protect grain downside",                       "RP at higher coverage. OBBBA raised subsidies 65% to 80%. SCO/ECO more attractive. COP $917/ac corn. Most WI/MN at or below breakeven."],
    ["Beans: upside now = biofuel, not China",        "SCOTUS clouds trade leverage. 45Z, E15, RFS are the catalysts. Don\u2019t cap upside, but expect headline volatility."],
    ["Dairy DRP: non-negotiable",                     "85-90% on 60-70% quarterly milk. Match Class III/IV. DMC by Feb 26. Jan III was $14.59 \u2014 plan accordingly."],
    ["Cattle: manage the volatility",                 "LRP sets floor, keeps upside. COF confirms tight supply. Lock some Q3-Q4 revenue on strength. Watch consumer pushback above $9.50/lb retail."],
    ["FBA signup open today",                         "fsa.usda.gov/fba. Corn $44.36/ac, beans $30.88/ac, wheat $39.35/ac. Online payments by Feb 28. Deadline Apr 17."],
    ["Gov\u2019t payments = ~25% net income",         "Higher ref prices + ARC + better crop insurance subsidies. Factor FBA into spring cash flow now."],
    ["March 15 sales closing",                        "Maximize ECO/SCO under new OBBBA provisions. Call us to verify numbers before deadline."]
  ],

  closingLine: "SCOTUS changed the game. The farm economy didn\u2019t blink.",
  closingSub: "Protect downside. Price into rallies. Don\u2019t bet the farm on the timing."
};

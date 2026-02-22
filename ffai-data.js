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
  updated:  "February 22, 2026",
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
  outlookFlash: 'USDA AG OUTLOOK FORUM \u00B7 FEB 19 \u2014 Corn: 94M ac, 183 bpa, 15.76B bu, $4.20 avg \u00B7 Beans: 85M ac, 53 bpa, 4.45B bu, $10.30 avg \u00B7 Cattle: $240/cwt (+7%) \u00B7 All-milk: $18.95/cwt',

  // ── Editorial: Report ───────────────────────────────────────
  headline: "The Wind Changed Direction. The Tide Hasn\u2019t Turned Yet.",
  intro: [
    "FFAI composite at <strong>68.0 FAVORABLE</strong> \u2014 national ag conditions decent but slipping from the 2023 peak. Sub-indexes tell the real story: grain farmers in single-digit stress territory while cattle ranchers ride record prices.",
    "The validated model says conditions are above average nationally, but <strong>which farm you run matters more than the national number.</strong> Grain at 9.8 means row crop margins are at historic lows. Livestock at 94.6 means cattle producers haven\u2019t had it this good in decades."
  ],

  signals: [
    ["Dollar / Export Demand",    "BULLISH",       "g", "DXY down 13% to 98.7. Corn exports raised to record 3.3B bu. India-US deal opens new demand. 10% dollar drop historically precedes 15-20% grain price improvement."],
    ["Gold / Ag Commodities",     "BULLISH 12-24MO","g", "Gold $4,945, silver $85.65. Gap to grain prices widest on record. Gold ATH historically precedes ag commodity rallies 12-24 months out."],
    ["Baltic Dry / Trade Flow",   "CONSTRUCTIVE",  "a", "BDI 2,019, up 135% YoY. Panamax at 1,792. Sustained above 1,800 confirms grain trade acceleration."],
    ["Brazil-China / Export Share","WATCH",         "a", "Real 5.33/USD, record 180 MMT Brazil soy. Weakening USD narrows their advantage."],
    ["WASDE / Price Direction",   "TURNING",       "a", "Feb WASDE cut corn stocks 100M bu \u2014 bullish surprise. 39.2% US in drought. If persists into planting, supply picture changes fast."],
    ["Equipment / Profitability", "BOTTOMING",     "g", "Deere ATH $593, called 2026 cycle bottom. Titan Machinery $14.30 still distressed. When TITN turns, sector confirmed."]
  ],

  actions: [
    ["Hold patience on last 20-30% of 2025 crop",  "USDA cut stocks, record exports. Dollar weakening. Basis tightening. If no margin calls, data supports holding."],
    ["Lock input costs now",                         "Crude under $60. Nutrien and Mosaic near 52-week lows. Lock what you can while input prices are favorable."],
    ["Forward contract above $4.70 Dec corn",        "Layer 20-30% new crop at $4.70+ corn, $12+ Nov beans. Lock margins at today\u2019s reduced inputs."],
    ["Maximize crop insurance \u2014 March 15",      "ECO/SCO underutilized in Upper Midwest. Call us to verify numbers under new OBBBA provisions."],
    ["Watch the drought",                            "39% of US in drought. Nebraska D3 Extreme. SWE lowest since 1986. If extends to corn belt, grain sub-index moves."],
    ["Don\u2019t sell land",                         "Cropland $5,830/ac. Iowa appreciation slowed to 0.7%. Better entries in 18 months."],
    ["Government payments are temporary",            "$44.3B is ad hoc. Debt-to-asset 13.8% historically low. Use that runway."]
  ],

  closingLine: "The wind changed. The tide hasn\u2019t.",
  closingSub: "Position for the turn. Don\u2019t bet the farm on the timing."
};

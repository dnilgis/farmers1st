// ═══════════════════════════════════════════════════
// FFAI WEEKLY DATA — EDIT THIS FILE EVERY SUNDAY
// Everything below drives the website AND the email.
// Edit → commit → push → site updates instantly.
// Then open Google Sheet → Send Weekly Report.
// ═══════════════════════════════════════════════════

var FFAI = {

  // ── Current week ──
  date: "February 19, 2026",
  dateShort: "FEB 19, 2026",
  nextUpdate: "FEB 23",
  score: 53.6,
  prevScore: 48.0,      // last period's composite
  label: "GUARDED",     // STRESSED / GUARDED / FAVORABLE / STRONG

  // ── 10 Categories: [current, previous, tooltip] ──
  categories: {
    "Crops":   [32.4, 30.1, "Row Crops (20% weight) — Corn, soybeans, wheat, oats futures. Corn down 48% from highs. Soy basis tightening. Weakest FFAI category."],
    "Inputs":  [62.8, 60.2, "Input Costs (15% weight) — Crude, diesel, fertilizer, seed. Inverse-scored: lower costs = higher score. Crude under $60. Nutrien/Mosaic near 52-wk lows."],
    "Equip":   [61.5, 55.0, "Equipment & Supply (10% weight) — Deere, AGCO, CNHI, Titan Machinery. Deere ATH $593, called 2026 cycle bottom."],
    "Demand":  [58.4, 52.3, "Global Demand (10% weight) — Baltic Dry Index, competitor currencies, China imports. BDI up 135% YoY. Panamax at 1,792."],
    "Macro":   [58.6, 54.1, "Macro Environment (10% weight) — Fed funds rate, CPI, 10-year yield, DXY. Dollar down 13% to 98.7 — bullish for grain exports."],
    "USDA":    [52.8, 48.5, "USDA Supply (10% weight) — WASDE, ending stocks, crop progress, drought monitor. Feb WASDE cut corn stocks 100M bu. 39.2% US in drought."],
    "Metals":  [88.2, 82.0, "Metals & Inflation (7% weight) — Gold, silver, copper as inflation indicators. Gold $4,945. Gold ATH historically precedes ag rallies 12-24 months."],
    "Livstk":  [72.1, 70.8, "Livestock & Dairy (5% weight) — Live cattle, feeder cattle, lean hogs, Class III milk. Cattle near all-time highs."],
    "Trade":   [38.2, 36.0, "Grain Trade (8% weight) — ADM, Bunge, soybean crush margins, ethanol. Margins compressed. ADM restructuring."],
    "Struct":  [44.8, 43.5, "Farm Structure (5% weight) — Net farm income, debt-to-asset, land values, gov payments. Median farm income: -$1,498."]
  },

  // ── Historical quarterly data (append new quarters) ──
  history: [
    ["Q1'17",46],["Q2'17",44],["Q3'17",42],["Q4'17",44],
    ["Q1'18",43],["Q2'18",40],["Q3'18",38],["Q4'18",41],
    ["Q1'19",38],["Q2'19",36],["Q3'19",40],["Q4'19",39],
    ["Q1'20",42],["Q2'20",52],["Q3'20",58],["Q4'20",55],
    ["Q1'21",64],["Q2'21",72],["Q3'21",68],["Q4'21",70],
    ["Q1'22",74],["Q2'22",66],["Q3'22",58],["Q4'22",63],
    ["Q1'23",56],["Q2'23",52],["Q3'23",48],["Q4'23",51],
    ["Q1'24",47],["Q2'24",42],["Q3'24",40],["Q4'24",43],
    ["Q1'25",45],["Q2'25",47],["Q3'25",46],["Q4'25",48],
    ["Feb'26",53.6]
  ],

  // ── Weekly report content ──
  headline: "The Wind Changed Direction. The Tide Hasn't Turned Yet.",

  intro: [
    "FFAI at <strong>53.6</strong>, up from 48.0 last quarter — the strongest single-period move since 2020. Leading indicators improving across the board. Lagging indicators haven't caught up yet. Early-stage recovery or a false bottom. The data shows which signals to watch.",
    "S&P up 100%+ since October '22. Net farm income down 22%. <strong>Corn down 48% from highs.</strong> Median farm income: negative $1,498 from farming. Government payments $44.3B — highest since 2020 — masking the real picture. Gold nearly tripled to $4,945."
  ],

  // ── 6 Cycle signals: [title, rating, ratingType, description] ──
  // ratingType: "g" = green/bullish, "a" = amber/watch
  signals: [
    ["Dollar / Export Demand", "BULLISH", "g", "DXY down 13% to 98.7. Corn exports raised to record 3.3B bu. India-US deal opens new demand. 10% dollar drop historically precedes 15-20% grain price improvement, 12-18 months."],
    ["Gold / Ag Commodities", "BULLISH 12-24MO", "g", "Gold $4,945, silver $85.65. Gap to grain prices widest on record. Gold ATH historically precedes ag commodity rallies 12-24 months out."],
    ["Baltic Dry / Trade Flow", "CONSTRUCTIVE", "a", "BDI 2,019, up 135% YoY. Panamax at 1,792. Sustained above 1,800 confirms grain trade acceleration."],
    ["Brazil-China / Export Share", "WATCH", "a", "Real 5.33/USD, record 180 MMT Brazil soy. Weakening USD narrows their advantage. Yuan 7.25 = stable Chinese buying power."],
    ["WASDE / Price Direction", "TURNING", "a", "Feb WASDE cut corn stocks 100M bu — bullish surprise. 39.2% US in drought, expanding to D3 Extreme. If persists into planting, supply picture changes fast."],
    ["Equipment / Profitability", "BOTTOMING", "g", "Deere ATH $593, raised guidance, called 2026 cycle bottom. Titan Machinery $14.30 still distressed. When TITN turns, sector confirmed."]
  ],

  // ── 7 Action items: [title, description] ──
  actions: [
    ["Hold patience on last 20-30% of 2025 crop", "USDA cut stocks, record exports. Dollar weakening. Basis tightening. If no margin calls, data supports holding."],
    ["Lock input costs now", "Crude under $60. Nutrien and Mosaic near 52-week lows. Input score 62.8 is strongest FFAI category. Lock what you can."],
    ["Forward contract above $4.70 Dec corn", "Layer 20-30% new crop at $4.70+ corn, $12+ Nov beans. Lock margins at today's reduced inputs."],
    ["Maximize crop insurance — March 15 deadline", "ECO/SCO underutilized in Upper Midwest. Call us to verify numbers under new OBBBA provisions."],
    ["Watch the drought", "39% of US in drought. Nebraska D3 Extreme. SWE lowest since 1986. If extends to corn belt, FFAI moves through 60."],
    ["Don't sell land", "Cropland $5,830/ac. Iowa appreciation slowed to 0.7%. Farmer Mac prices diverging from surveys. Better entries in 18 months."],
    ["Government payments are temporary", "$44.3B is ad hoc. Debt-to-asset 13.8% historically low. Balance sheet stronger than income statement. Use that runway."]
  ],

  closingLine: "The wind changed. The tide hasn't.",
  closingSub: "Position for the turn. Don't bet the farm on the timing."
};

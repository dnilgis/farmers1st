// FFAI commentary. Written by hand each quarter; the publish button never edits this file.
// Every number must come from ffai-v4.js / engine/v4/ for the quarter in editorialQuarter.
// When the scores move to a newer quarter, the page labels this text as older
// and builds the flash bar from the numbers instead.
//
// COMPLIANCE:
// - No absolute advisory language ("non-negotiable", "must", etc.)
// - No deadlines that have passed
// - Subsidy changes: cite RMA bulletin numbers, not bill names, unless fully enacted and verifiable
// - No superlatives ("record", "lowest since") unless computed from the published history
// - General market information is not advice specific to any producer's situation
var FFAI_TEXT = {
  editorialQuarter: "Q2'26",
  editorialPublished: "October 7, 2026",

  outlookFlash: "Q2'26 FFAI v4 — 11 STRESSED · Crops 0 · Livestock 94 · Dairy 0 · Fuel prices paid +30.8%, Apr–Jun vs Jan–Mar average · Next insurance deadline: Dec 1 PRF sales closing",

  headline: "Prices Outran Costs. Still Low.",
  intro: [
    "All U.S. farms: <strong>11 STRESSED</strong> for Q2 2026 (April–June), up from 0 in Q1. Prices farms receive rose faster than what they pay, so the ratio of the two climbed to <strong>84.5</strong> (2011 = 100) from 79.2. Farm prices still buy 15.5% less of what farms pay for than in 2011. Against its own average of the previous 10 years (86.1), the ratio is only 1.9% lower, a smaller gap than the score against 1995–2019 suggests.",
    "<strong>Meat animal prices are the strongest against costs of any sector.</strong> The livestock ratio is 113.9 (score 94), close to Q3’25’s 119.0, the highest in this series, which starts in 1995. <strong>Crops (73.4) and dairy (60.2)</strong> both hit their lowest readings in the series in Q1 and recovered only part of the way. Both still score 0: lower than every quarter from 1995 to 2019.",
    "Averaged over April–June, fuel prices paid rose 30.8% from Q1 and fertilizer 12.9%. On the other side, dairy prices received rose 13.9%, oilseeds 6.7% and livestock 5.5%. At the farm gate, milk averaged $21.07/cwt (from $18.50), steers and heifers $253.00/cwt (from $238.67), corn $4.36/bu and soybeans $11.37/bu."
  ],

  signals: [
    ["Fuel and Fertilizer Spike", "BEARISH CROPS", "a", "April–June averages: fuel prices paid +30.8% from Q1 and +37.5% from a year ago; fertilizer +12.9% and +23.1%. Crop farms carry most of both. These are quarter averages; check current prices before you buy."],
    ["Crops Near the Bottom",     "STRESSED",      "a", "Crop ratio 73.4, up 13% from 64.7 in Q1, the lowest in the series. The score stays at 0 because 73.4 is still below every quarter from 1995 to 2019. Farm-gate corn $4.36/bu, soybeans $11.37/bu, wheat $5.76/bu for the quarter."],
    ["Dairy Off Its Low",         "STILL STRESSED","a", "Milk averaged $21.07/cwt, up from $18.50 in Q1. The dairy ratio rose to 60.2 from 54.0, the lowest in the series, but still sits below every quarter from 1995 to 2019. Part of that is the cost side: USDA has no dairy-only cost index, and the animal-farm index we use includes feeder cattle and replacement cows, which cost far more than they did. Against feed costs alone, dairy scores 26."],
    ["Cattle at the Top",         "STRONG",        "g", "Livestock ratio 113.9, score 94. Steers and heifers averaged $253.00/cwt, up from $221.00 a year earlier."],
    ["What This Index Tracks",    "METHOD",        "g", "Over 30 years, when this ratio rose or fell, inflation-adjusted USDA net farm income moved the same way that year (r = 0.75). That is a same-year link, not a forecast. A score of 11 means prices are low against costs compared with 1995–2019, not that income is low. It counts prices only: yields and government payments are not in it."]
  ],

  actions: [
    ["Crop damage: call within 72 hours",
     "Notice of loss is due within 72 hours of finding damage, and no later than 15 days after the end of the insurance period. Call us before you harvest or destroy a damaged field."],
    ["Dec 10: end of insurance period, corn and soybeans",
     "Unharvested acres are no longer covered after this date."],
    ["Dec 1: PRF sales closing for 2027",
     "Pasture, Rangeland, Forage coverage for hay and grazing acres. New sign-ups and changes close Dec 1."],
    ["Dairy: set coverage for 2027 milk",
     "Dairy Revenue Protection quarters from Jan–Mar 2027 onward can still be bought, up to five quarters out. Call us to look at your numbers."],
    ["Crops: plan the 2027 SCO/ECO stack",
     "With crop prices low against costs, area coverage above your policy matters more. For most 2027 crops SCO rises to 90% and ECO covers 90% to 95%, with an 80% premium subsidy. Sales closing is March 15."]
  ],

  closingLine: "Prices outran costs this quarter. Still low against 1995–2019.",
  closingSub: "Market information above is general in nature — contact us for guidance specific to your operation."
};

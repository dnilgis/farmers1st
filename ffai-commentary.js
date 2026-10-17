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

  outlookFlash: "Q2'26 FFAI v4: ratio 84.5, down 9.5% from Q2'25 · Score 11, LOW vs 1995-2019 · Fuel prices paid +37.5% vs a year earlier · Next insurance deadline: Dec 1 PRF sales closing",

  headline: "Down From a Year Ago. Still Low.",
  intro: [
    "All U.S. farms: the ratio of prices received to prices paid was <strong>84.5</strong> (2011 = 100) for Q2 2026 (April–June), <strong>down 9.5% from 93.4</strong> in Q2 2025. That scores 11 of 100, <strong>LOW vs 1995–2019</strong>, against 24 a year earlier. The ratio rose from 79.2 in Q1, but part of any spring rise is seasonal. Farm prices still buy 15.5% less of what farms pay for than in 2011. Against its own average of the previous 10 years (86.1), the ratio is only 1.9% lower, a smaller gap than the score against 1995–2019 suggests.",
    "<strong>Meat animal prices are the strongest against costs of any sector.</strong> The livestock ratio is 113.9 (score 94, HIGH vs 1995–2019), up 1.0% from a year earlier and close to Q3’25’s 119.0, the highest in this series, which starts in 1995. <strong>Crops (73.4, up 2.4% from a year earlier) and dairy (60.2, down 12.4%)</strong> both hit their lowest readings in the series in Q1 and recovered only part of the way. Both still score 0: lower than every quarter from 1995 to 2019.",
    "Against a year earlier, fuel prices paid rose 37.5% and fertilizer 23.1%. On the other side, meat animal prices received rose 14.1% and oilseeds 8.6%, while dairy prices slipped 0.9%. At the farm gate, milk averaged $21.07/cwt (from $21.27 a year earlier), steers and heifers $253.00/cwt (from $221.00), corn $4.36/bu (from $4.58) and soybeans $11.37/bu (from $10.33)."
  ],

  signals: [
    ["Fuel and Fertilizer Spike", "BEARISH CROPS", "a", "April–June averages: fuel prices paid +37.5% from a year ago and +30.8% from Q1; fertilizer +23.1% and +12.9%. Crop farms carry most of both. These are quarter averages; check current prices before you buy."],
    ["Crops Near the Bottom",     "LOW",           "a", "Crop ratio 73.4, up 2.4% from 71.6 a year earlier and up from 64.7 in Q1, the lowest in the series. The score stays at 0 because 73.4 is still below every quarter from 1995 to 2019. Farm-gate corn $4.36/bu, soybeans $11.37/bu, wheat $5.76/bu for the quarter."],
    ["Dairy Below a Year Ago",    "STILL LOW",     "a", "Milk averaged $21.07/cwt, against $21.27 a year earlier and $18.50 in Q1. The dairy ratio, 60.2, is down 12.4% from a year earlier; it rose from 54.0 in Q1, the lowest in the series, but still sits below every quarter from 1995 to 2019. USDA has no dairy-only cost index, and the animal-farm index we use includes feeder cattle and replacement cows. That is not the whole story: against USDA’s broader cost indexes dairy also scores 0, and only against feed costs alone does it score 26."],
    ["Cattle at the Top",         "HIGH",          "g", "Livestock ratio 113.9, score 94. Steers and heifers averaged $253.00/cwt, up from $221.00 a year earlier."],
    ["What This Index Tracks",    "METHOD",        "g", "Over 30 years, when this ratio rose or fell, inflation-adjusted USDA net farm income moved the same way that year in 24 of 30 years (r = 0.75). That is a same-year link, not a forecast. A score of 11 (LOW vs 1995–2019) means prices are low against costs compared with that period, not that income is low. It counts prices only: yields and government payments are not in it."]
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

  closingLine: "Down 9.5% from a year ago. LOW against 1995–2019.",
  closingSub: "Market information above is general in nature. Contact us for guidance specific to your operation."
};

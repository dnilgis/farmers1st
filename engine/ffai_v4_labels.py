"""
FFAI v4 labels: the one place the label lines live.

The score is the share of 1995-2019 quarters whose ratio was at or below this
quarter's (0-100). The label says only where the price ratio sits against that
base period, split at its quartiles:

    LOW           under 25   (in the bottom quarter of 1995-2019 quarters)
    BELOW MIDDLE  25 to 50
    ABOVE MIDDLE  50 to 75
    HIGH          75 and up  (in the top quarter)

It is a statement about prices received against prices paid, not about farm
income. Always show it with "vs 1995-2019".

Used by engine/ffai_v4.py, tools/ffai_v4_publish.py and tools/ffai_v4_stress.py.
The page and the badge read the label from the published JSON; they do not
compute it.

The labels before Oct 2026 (STRESSED / GUARDED / FAVORABLE / STRONG, lines at
40 / 55 / 70) are kept only as `label_legacy` in the API.
"""
import math

BASE_TEXT = '1995-2019'
LINES = (('BELOW MIDDLE', 25), ('ABOVE MIDDLE', 50), ('HIGH', 75))  # name, score where it starts
NAMES = ('LOW', 'BELOW MIDDLE', 'ABOVE MIDDLE', 'HIGH')
RANGES = {'LOW': '0-25', 'BELOW MIDDLE': '25-50', 'ABOVE MIDDLE': '50-75', 'HIGH': '75-100'}

LEGACY_LINES = (('GUARDED', 40), ('FAVORABLE', 55), ('STRONG', 70))
LEGACY_NAMES = ('STRESSED', 'GUARDED', 'FAVORABLE', 'STRONG')
LEGACY_RANGES = {'STRESSED': '0-40', 'GUARDED': '40-55', 'FAVORABLE': '55-70', 'STRONG': '70-100'}


def _pick(v, first, lines):
    if v is None:
        return None
    try:
        v = float(v)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(v):
        return None
    out = first
    for name, t in lines:
        if v >= t:
            out = name
    return out


def label(v):
    """LOW / BELOW MIDDLE / ABOVE MIDDLE / HIGH for a 0-100 score; None if missing."""
    return _pick(v, 'LOW', LINES)


def label_legacy(v):
    """The pre-Oct 2026 label, kept for API readers that still expect it."""
    return _pick(v, 'STRESSED', LEGACY_LINES)

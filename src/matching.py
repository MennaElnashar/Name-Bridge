"""Candidate generation. Similarity answers only: is this pair worth checking?"""
from itertools import combinations

import pandas as pd

from .normalization import aggressive_normalize, conservative_normalize

try:  # preferred backend
    from rapidfuzz import fuzz as _rf_fuzz
except ImportError:  # exercised in sandboxes without rapidfuzz
    _rf_fuzz = None

BACKEND = "rapidfuzz" if _rf_fuzz else "pure-python (Indel ratio, same definition as fuzz.ratio)"


def _indel_ratio(a: str, b: str) -> float:
    """Normalized Indel similarity x 100 (the definition behind rapidfuzz fuzz.ratio)."""
    if not a and not b:
        return 100.0
    if not a or not b:
        return 0.0
    prev = [0] * (len(b) + 1)
    for ca in a:
        cur = [0]
        for j, cb in enumerate(b, 1):
            cur.append(prev[j - 1] + 1 if ca == cb else max(prev[j], cur[j - 1]))
        prev = cur
    return 100.0 * 2 * prev[-1] / (len(a) + len(b))


def ratio(a: str, b: str) -> float:
    return _rf_fuzz.ratio(a, b) if _rf_fuzz else _indel_ratio(a, b)


def token_sort_ratio(a: str, b: str) -> float:
    a2, b2 = " ".join(sorted(a.split())), " ".join(sorted(b.split()))
    return ratio(a2, b2)


def name_similarity(name_a, name_b, mode: str = "aggressive") -> float:
    """mode: "aggressive" (default since Day 4) or "conservative" (Day 2 baseline)."""
    if mode == "aggressive":
        return ratio(aggressive_normalize(name_a), aggressive_normalize(name_b))
    return token_sort_ratio(conservative_normalize(name_a), conservative_normalize(name_b))


MAX_ROWS = 2000  # pairwise comparison is O(n^2); this is a prototype guard


def iter_record_pairs(df: pd.DataFrame):
    if len(df) > MAX_ROWS:
        raise ValueError(f"Prototype limit: {MAX_ROWS} rows (got {len(df)}).")
    rows = df.to_dict("records")
    for a, b in combinations(rows, 2):
        yield a, b

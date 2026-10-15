"""Evidence assessment. Compares identifiers; does not look at name spelling.

Free-text columns such as 'note' are deliberately never used as evidence."""
import re


def _text(v):
    v = "" if v is None else str(v)
    v = re.sub(r"\s+", " ", v).strip().casefold()
    return v or None


def compare_identifiers(rec_a: dict, rec_b: dict, unique_cols, soft_cols):
    """unique_cols: identifiers expected to be one-per-person (email, student id).
    soft_cols: context that can legitimately differ or repeat (organization)."""
    out = {"matching": [], "conflicting": [], "missing": [],
           "soft_matching": [], "soft_conflicting": [], "soft_missing": []}
    for cols, keys in ((unique_cols, ("matching", "conflicting", "missing")),
                       (soft_cols, ("soft_matching", "soft_conflicting", "soft_missing"))):
        for c in cols:
            va, vb = _text(rec_a.get(c)), _text(rec_b.get(c))
            if va is None or vb is None:
                out[keys[2]].append(c)
            elif va == vb:
                out[keys[0]].append(c)
            else:
                out[keys[1]].append(c)
    return out

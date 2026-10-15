"""Decision policy. Defaults to needs_review whenever evidence does not decide."""
from dataclasses import dataclass, field

LIKELY_MATCH, NEEDS_REVIEW, LIKELY_DIFFERENT = "likely_match", "needs_review", "likely_different"


@dataclass
class PolicyConfig:
    name_threshold: float = 80.0           # similarity needed to be a name-based candidate
    similarity_mode: str = "aggressive"    # Day 4 change; "conservative" was the Day 2 default
    unique_cols: list = field(default_factory=lambda: ["email", "student_id"])
    soft_cols: list = field(default_factory=lambda: ["org"])


def recommend(similarity: float, ev: dict, cfg: PolicyConfig):
    """Returns (recommendation or None if not a candidate, reason)."""
    similar = similarity >= cfg.name_threshold
    m, c = ev["matching"], ev["conflicting"]
    if not similar and not m:
        return None, "not a candidate"
    if m and c:
        return NEEDS_REVIEW, (f"identifiers disagree with each other (match: {', '.join(m)}; "
                              f"conflict: {', '.join(c)}); a person could share one and not the other")
    if similar:
        if m:
            return LIKELY_MATCH, f"similar names and matching {', '.join(m)} with no unique-identifier conflict"
        if c:
            return LIKELY_DIFFERENT, f"similar names but conflicting {', '.join(c)}"
        why = "name similarity alone does not establish identity"
        if ev["soft_conflicting"]:
            why += f"; {', '.join(ev['soft_conflicting'])} differs (may be a change, not a conflict)"
        if ev["missing"]:
            why += f"; missing: {', '.join(ev['missing'])}"
        return NEEDS_REVIEW, why
    return NEEDS_REVIEW, (f"names differ but {', '.join(m)} matches; investigate the discrepancy "
                          f"(shared or reused identifier?) before any merge")

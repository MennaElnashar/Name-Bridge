"""Glue: DataFrame in, candidate-pair DataFrame out. Original values are copied as-is."""
import pandas as pd

from .evidence import compare_identifiers
from .matching import iter_record_pairs, name_similarity
from .policy import PolicyConfig, recommend

PAIR_COLUMNS = ["record_id_a", "record_id_b", "name_a", "name_b", "similarity", "recommendation",
                "reason", "matching_ids", "conflicting_ids", "missing_ids", "soft_conflicts",
                "review_decision", "reviewer_note"]


def read_csv_preserving(path_or_buffer) -> pd.DataFrame:
    """dtype=str and no NA coercion, so names like 'Nan' or 'Null' survive unchanged."""
    return pd.read_csv(path_or_buffer, dtype=str, keep_default_na=False)


def names_to_frame(text: str) -> pd.DataFrame:
    names = [ln for ln in text.splitlines() if ln.strip()]
    return pd.DataFrame({"record_id": [str(i) for i in range(1, len(names) + 1)], "name": names})


def validate(df, name_col, id_cols=()):
    if name_col not in df.columns:
        raise ValueError(f"Name column '{name_col}' not found.")
    missing = [c for c in id_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Identifier column(s) not found: {missing}")
    if (df[name_col].astype(str).str.strip() == "").all():
        raise ValueError("All names are empty.")


def find_candidates(df, name_col="name", id_col="record_id", cfg=None) -> pd.DataFrame:
    cfg = cfg or PolicyConfig()
    cfg = PolicyConfig(cfg.name_threshold, cfg.similarity_mode,
                       [c for c in cfg.unique_cols if c in df.columns],
                       [c for c in cfg.soft_cols if c in df.columns])
    validate(df, name_col, cfg.unique_cols + cfg.soft_cols)
    df = df.copy()
    if id_col not in df.columns:
        df[id_col] = [str(i) for i in range(1, len(df) + 1)]
    out = []
    for a, b in iter_record_pairs(df):
        if not str(a[name_col]).strip() or not str(b[name_col]).strip():
            continue  # empty names are never compared
        sim = name_similarity(a[name_col], b[name_col], cfg.similarity_mode)
        ev = compare_identifiers(a, b, cfg.unique_cols, cfg.soft_cols)
        rec, reason = recommend(sim, ev, cfg)
        if rec is None:
            continue
        out.append({"record_id_a": a[id_col], "record_id_b": b[id_col],
                    "name_a": a[name_col], "name_b": b[name_col],
                    "similarity": round(sim, 1), "recommendation": rec, "reason": reason,
                    "matching_ids": ";".join(ev["matching"]), "conflicting_ids": ";".join(ev["conflicting"]),
                    "missing_ids": ";".join(ev["missing"]), "soft_conflicts": ";".join(ev["soft_conflicting"]),
                    "review_decision": "", "reviewer_note": ""})
    res = pd.DataFrame(out, columns=PAIR_COLUMNS)
    return res.sort_values(["recommendation", "similarity"], ascending=[True, False], kind="stable").reset_index(drop=True)

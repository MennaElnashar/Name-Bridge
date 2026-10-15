"""Reproducible evaluation. Run:  python -m src.evaluate
Compares three strategies on data/synthetic_names.csv against data/gold_pairs.csv."""
import json
import sys
from itertools import combinations
from pathlib import Path

import pandas as pd

from . import matching
from .pipeline import find_candidates, read_csv_preserving
from .policy import LIKELY_DIFFERENT, LIKELY_MATCH, NEEDS_REVIEW, PolicyConfig

ROOT = Path(__file__).resolve().parent.parent


def naive_name_only(df, threshold=80.0, mode="conservative"):
    """Strawman: name similarity alone decides. Used only to test hypothesis 1."""
    rows = []
    for a, b in combinations(df.to_dict("records"), 2):
        s = matching.name_similarity(a["name"], b["name"], mode)
        if s >= threshold:
            rows.append({"record_id_a": a["record_id"], "record_id_b": b["record_id"],
                         "name_a": a["name"], "name_b": b["name"],
                         "similarity": s, "recommendation": LIKELY_MATCH})
    return pd.DataFrame(rows, columns=["record_id_a", "record_id_b", "name_a", "name_b", "similarity", "recommendation"])


STRATEGIES = {
    "naive_name_only": lambda df: naive_name_only(df),
    "baseline_conservative": lambda df: find_candidates(df, cfg=PolicyConfig(similarity_mode="conservative")),
    "experimental_aggressive": lambda df: find_candidates(df, cfg=PolicyConfig(similarity_mode="aggressive")),
    "final_default_config": lambda df: find_candidates(df, cfg=PolicyConfig()),
}


def key(a, b):
    return tuple(sorted((str(a), str(b)), key=int))


def evaluate(df, gold, pairs):
    ent = dict(zip(df.record_id, df.entity_id))
    rec = {key(r.record_id_a, r.record_id_b): r.recommendation for r in pairs.itertuples()}
    g = {key(r.record_id_a, r.record_id_b): r.gold for r in gold.itertuples()}
    same = {key(a, b) for a, b in combinations(df.record_id, 2) if ent[a] == ent[b]}
    false_merges = sorted(k for k, v in rec.items() if v == LIKELY_MATCH and ent[k[0]] != ent[k[1]])
    false_splits = sorted(k for k, v in rec.items() if v == LIKELY_DIFFERENT and ent[k[0]] == ent[k[1]])
    not_surfaced = sorted(k for k in same if k not in rec)
    gold_review = [k for k, v in g.items() if v == NEEDS_REVIEW]
    return {
        "candidates": len(rec),
        "gold_pairs": len(g),
        "gold_agreement": sum(rec.get(k) == v for k, v in g.items()),
        "false_merges": [list(k) for k in false_merges],
        "false_splits": [list(k) for k in false_splits],
        "true_same_entity_pairs": len(same),
        "true_pairs_not_surfaced": [list(k) for k in not_surfaced],
        "gold_review_pairs": len(gold_review),
        "review_pairs_given_false_certainty": sorted([list(k) for k in gold_review if rec.get(k) in (LIKELY_MATCH, LIKELY_DIFFERENT)]),
        "review_pairs_not_surfaced": sorted([list(k) for k in gold_review if k not in rec]),
        "noise_candidates_not_in_gold": sorted([list(k) for k in rec if k not in g]),
        "disagreements_with_gold": sorted([[*k, rec.get(k, "not_surfaced"), v] for k, v in g.items() if rec.get(k) != v]),
    }


def name_preservation_ok(df, pairs):
    src = set(df.name)
    return bool(all(n in src for n in list(pairs.name_a) + list(pairs.name_b)))


def evaluate_hard():
    """Second, harder set written after the design was frozen. The policy was not tuned on it."""
    df = read_csv_preserving(ROOT / "data" / "hard_cases.csv")
    gold = read_csv_preserving(ROOT / "data" / "hard_gold_pairs.csv")
    results = {"similarity_backend": matching.BACKEND, "records": len(df)}
    for name in ("naive_name_only", "final_default_config"):
        pairs = STRATEGIES[name](df)
        m = evaluate(df, gold, pairs)
        m["names_preserved"] = name_preservation_ok(df, pairs)
        results[name] = m
    out = ROOT / "outputs" / "hard_results.json"
    out.write_text(json.dumps(results, indent=2))
    print("\n== HARD SET ==")
    for name in ("naive_name_only", "final_default_config"):
        m = results[name]
        print(f"{name}: candidates={m['candidates']} gold_agreement={m['gold_agreement']}/{m['gold_pairs']} "
              f"false_merges={m['false_merges']} false_splits={m['false_splits']} "
              f"true_not_surfaced={m['true_pairs_not_surfaced']} noise={len(m['noise_candidates_not_in_gold'])} "
              f"names_preserved={m['names_preserved']}")
        print("  disagreements:", m["disagreements_with_gold"])
    print("wrote", out)
    return results


def main():
    df = read_csv_preserving(ROOT / "data" / "synthetic_names.csv")
    gold = read_csv_preserving(ROOT / "data" / "gold_pairs.csv")
    results = {"similarity_backend": matching.BACKEND, "records": len(df)}
    for name, fn in STRATEGIES.items():
        pairs = fn(df)
        m = evaluate(df, gold, pairs)
        m["names_preserved"] = name_preservation_ok(df, pairs)
        results[name] = m
    out = ROOT / "outputs" / "eval_results.json"
    out.write_text(json.dumps(results, indent=2))
    for name in STRATEGIES:
        m = results[name]
        print(f"\n== {name} ==")
        print(f"candidates={m['candidates']}  gold_agreement={m['gold_agreement']}/{m['gold_pairs']}  "
              f"false_merges={len(m['false_merges'])}  false_splits={len(m['false_splits'])}  "
              f"true_not_surfaced={len(m['true_pairs_not_surfaced'])}/{m['true_same_entity_pairs']}  "
              f"review_given_false_certainty={len(m['review_pairs_given_false_certainty'])}/{m['gold_review_pairs']}  "
              f"noise={len(m['noise_candidates_not_in_gold'])}  names_preserved={m['names_preserved']}")
    print("\nbackend:", matching.BACKEND, "| wrote", out)
    hard = evaluate_hard()
    return results and hard


if __name__ == "__main__":
    sys.exit(0 if main() else 1)

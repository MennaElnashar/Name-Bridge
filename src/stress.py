"""Day 4 stress tests. Run:  python -m src.stress
1. Threshold sweep: does the aggressive result survive a different cut-off?
2. Homonym workload: 120 distinct people generated from common name parts, no identifiers.
   Every flagged pair is reviewer workload, so we count how much each strategy creates."""
import json
import random
from pathlib import Path

import pandas as pd

from . import matching
from .evaluate import ROOT, evaluate
from .pipeline import find_candidates, read_csv_preserving
from .policy import PolicyConfig

FIRST = ["Mohamed", "Muhammad", "Ahmed", "Ahmad", "Mahmoud", "Mostafa", "Mustafa", "Omar", "Amr", "Ali",
         "Hassan", "Hussein", "Khaled", "Karim", "Tarek", "Sherif", "Yousef", "Ibrahim", "Fatma", "Mona",
         "Noha", "Nour", "Salma", "Sara", "Hana", "Hanan", "Heba", "Dina", "Laila", "Mariam"]
LAST = ["Hassan", "Hasan", "Ali", "Aly", "Mahmoud", "Mansour", "Mansoor", "Salem", "Salim", "Kamal",
        "Kamel", "Farouk", "Farag", "Fouad", "Gaber", "Zaki", "Nasser", "Naser", "Said", "Sayed",
        "El Sayed", "Abdelrahman", "Abdel Rahman", "Samy", "Sami", "Adel", "Reda", "Rida", "Tarek", "Tariq"]


def sweep():
    df = read_csv_preserving(ROOT / "data" / "synthetic_names.csv")
    gold = read_csv_preserving(ROOT / "data" / "gold_pairs.csv")
    rows = []
    for mode in ("conservative", "aggressive"):
        for t in (70, 75, 80, 85, 90):
            m = evaluate(df, gold, find_candidates(df, cfg=PolicyConfig(name_threshold=t, similarity_mode=mode)))
            rows.append({"mode": mode, "threshold": t, "gold_agreement": m["gold_agreement"],
                         "false_merges": len(m["false_merges"]), "noise_not_in_gold": len(m["noise_candidates_not_in_gold"]),
                         "true_pairs_not_surfaced": len(m["true_pairs_not_surfaced"])})
    return rows


def homonym_workload(n=120, seed=7):
    rng = random.Random(seed)
    combos = [(f, l) for f in FIRST for l in LAST]
    chosen = rng.sample(combos, n)
    df = pd.DataFrame({"record_id": [str(i) for i in range(1, n + 1)], "name": [f"{f} {l}" for f, l in chosen]})
    total_pairs = n * (n - 1) // 2
    rows = []
    for mode in ("conservative", "aggressive"):
        res = find_candidates(df, cfg=PolicyConfig(similarity_mode=mode))
        rows.append({"mode": mode, "people": n, "pairs_compared": total_pairs, "flagged_for_review": len(res),
                     "flagged_per_100_people": round(100 * len(res) / n, 1)})
    return rows


def main():
    out = {"backend": matching.BACKEND, "threshold_sweep": sweep(), "homonym_workload": homonym_workload()}
    (ROOT / "outputs" / "stress_results.json").write_text(json.dumps(out, indent=2))
    print(pd.DataFrame(out["threshold_sweep"]).to_string(index=False))
    print()
    print(pd.DataFrame(out["homonym_workload"]).to_string(index=False))
    return out


if __name__ == "__main__":
    main()

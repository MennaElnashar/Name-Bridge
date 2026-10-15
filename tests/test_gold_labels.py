"""Audit of gold labels against ground-truth entity_id (labels are never given to the matcher)."""
import unittest
from pathlib import Path

from src.pipeline import read_csv_preserving

DATA = Path(__file__).resolve().parent.parent / "data"
# Ids reused by different people: the policy (and so the gold label) says likely_match, ground truth says different.
# Kept as a documented limitation, not hidden.
KNOWN_ID_REUSE = {("115", "116")}


class GoldLabelAudit(unittest.TestCase):
    def _check(self, data, gold, exceptions=()):
        df = read_csv_preserving(DATA / data)
        g = read_csv_preserving(DATA / gold)
        ent = dict(zip(df.record_id, df.entity_id))
        self.assertEqual(len(ent), len(df), "record_id must be unique")
        seen = set()
        for r in g.itertuples():
            self.assertIn(r.record_id_a, ent)
            self.assertIn(r.record_id_b, ent)
            k = tuple(sorted((r.record_id_a, r.record_id_b), key=int))
            self.assertNotIn(k, seen, f"duplicate gold pair {k}")
            seen.add(k)
            same = ent[r.record_id_a] == ent[r.record_id_b]
            if k in exceptions:
                continue
            if r.gold == "likely_match":
                self.assertTrue(same, f"{k} labelled likely_match but different entities")
            if r.gold == "likely_different":
                self.assertFalse(same, f"{k} labelled likely_different but same entity")
            self.assertIn(r.gold, {"likely_match", "needs_review", "likely_different"})

    def test_synthetic(self):
        self._check("synthetic_names.csv", "gold_pairs.csv")

    def test_hard(self):
        self._check("hard_cases.csv", "hard_gold_pairs.csv", KNOWN_ID_REUSE)

    def test_hard_exception_is_real(self):
        df = read_csv_preserving(DATA / "hard_cases.csv")
        ent = dict(zip(df.record_id, df.entity_id))
        for a, b in KNOWN_ID_REUSE:
            self.assertNotEqual(ent[a], ent[b])


if __name__ == "__main__":
    unittest.main()

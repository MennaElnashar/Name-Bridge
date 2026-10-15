"""The labelling sheet must be reproducible, must not leak answers, and the scorer must count correctly."""
import re
import unittest

import pandas as pd

from src import labelling


class LabellingSheet(unittest.TestCase):
    def test_reproducible_and_balanced(self):
        s1, k1 = labelling.build()
        s2, k2 = labelling.build()
        self.assertTrue(s1.equals(s2) and k1.equals(k2))
        self.assertEqual(len(s1), sum(labelling.QUOTA.values()))
        self.assertEqual(k1.policy.value_counts().to_dict(), labelling.QUOTA)

    def test_sheet_hides_answers_and_notes(self):
        sheet, _ = labelling.build()
        self.assertFalse([c for c in sheet.columns if re.search("policy|gold|entity|truth|note|recommend", c, re.I)])
        text = " ".join(sheet.astype(str).values.ravel())
        self.assertNotIn("confirmed", text)
        self.assertNotIn("merge them", text)
        self.assertTrue((sheet["Your answer"] == "").all())

    def test_score_counts(self):
        _, key = labelling.build()
        answers = pd.DataFrame({"Pair": key.pair, "Your answer": ""})
        pol_to_ans = {v: k for k, v in labelling.ANSWERS.items()}
        answers["Your answer"] = key.policy.map(pol_to_ans)
        res, _ = labelling.score(answers, key)
        self.assertEqual(res["pairs_answered"], len(key))
        self.assertEqual(res["agree_with_policy"], len(key))
        self.assertEqual(res["disagreements"], [])
        # flip the first answered pair to a different answer: exactly one disagreement
        first = answers.index[0]
        answers.loc[first, "Your answer"] = "Cannot tell" if answers.loc[first, "Your answer"] != "Cannot tell" else "Same person"
        res2, _ = labelling.score(answers, key)
        self.assertEqual(res2["agree_with_policy"], len(key) - 1)
        self.assertEqual(len(res2["disagreements"]), 1)

    def test_natural_wording_is_accepted(self):
        _, key = labelling.build()
        answers = pd.DataFrame({"Pair": key.pair[:3], "Your answer": ["same", " Different ", "Unsure"]})
        res, d = labelling.score(answers, key.iloc[:3])
        self.assertEqual(res["pairs_answered"], 3)
        self.assertEqual(list(d.human), ["likely_match", "likely_different", "needs_review"])

    def test_truth_column_read_from_file_as_text(self):
        # the real scoring path reads the key from CSV, where booleans arrive as the strings "True"/"False"
        _, key = labelling.build()
        key = key.astype(str)
        pol_to_ans = {v: k for k, v in labelling.ANSWERS.items()}
        answers = pd.DataFrame({"Pair": key.pair, "Your answer": key.policy.map(pol_to_ans)})
        res, _ = labelling.score(answers, key)
        expected = int(((key.policy == "likely_match") & (key.truth_same_person == "False")).sum())
        self.assertEqual(res["policy_match_where_truth_is_different_people"], expected)

    def test_blank_answers_are_ignored(self):
        _, key = labelling.build()
        res, _ = labelling.score(pd.DataFrame({"Pair": key.pair, "Your answer": ""}), key)
        self.assertEqual(res["pairs_answered"], 0)


if __name__ == "__main__":
    unittest.main()

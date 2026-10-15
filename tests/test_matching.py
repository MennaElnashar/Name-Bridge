import io
import unittest

import pandas as pd

from src.matching import name_similarity
from src.pipeline import find_candidates, names_to_frame, read_csv_preserving
from src.policy import PolicyConfig

CONS = PolicyConfig(similarity_mode="conservative")


def frame(rows):
    return pd.DataFrame(rows, columns=["record_id", "name", "email", "student_id", "org", "note"]).fillna("")


def rec(df, a, b):
    r = df[(df.record_id_a == a) & (df.record_id_b == b)]
    return None if r.empty else r.iloc[0].recommendation


class TestPolicy(unittest.TestCase):
    def test_spec_example_three_records(self):
        df = frame([["1", "Mennatullah Hassan", "menna.hassan@example.test", "", "", ""],
                    ["2", "Menna Allah Hassan", "menna.hassan@example.test", "", "", ""],
                    ["3", "Mennatallah Hassan", "other.person@example.test", "", "", ""]])
        out = find_candidates(df)
        self.assertEqual(rec(out, "1", "2"), "likely_match")
        self.assertEqual(rec(out, "1", "3"), "likely_different")
        self.assertEqual(rec(out, "2", "3"), "likely_different")

    def test_day4_regression_spacing_variant_with_matching_email(self):
        # Day 2 failure: conservative mode downgraded this to needs_review ("names differ")
        df = frame([["1", "Mennatullah Hassan", "m@example.test", "", "", ""],
                    ["2", "Menna Allah Hassan", "m@example.test", "", "", ""]])
        self.assertEqual(rec(find_candidates(df, cfg=CONS), "1", "2"), "needs_review")
        self.assertEqual(rec(find_candidates(df), "1", "2"), "likely_match")

    def test_no_identifiers_never_likely_match(self):
        df = frame([["1", "Hana Salem", "", "", "", ""], ["2", "Hanan Salem", "", "", "", ""]])
        self.assertEqual(rec(find_candidates(df), "1", "2"), "needs_review")

    def test_identical_names_conflicting_ids_not_merged(self):
        df = frame([["1", "Fatma Ibrahim", "a@example.test", "S1", "", ""],
                    ["2", "Fatma Ibrahim", "b@example.test", "S2", "", ""]])
        self.assertEqual(rec(find_candidates(df), "1", "2"), "likely_different")

    def test_different_names_shared_identifier_is_review(self):
        df = frame([["1", "Sara Adel", "shared@example.test", "", "", ""],
                    ["2", "Mariam Tarek", "shared@example.test", "", "", ""]])
        self.assertEqual(rec(find_candidates(df), "1", "2"), "needs_review")

    def test_email_matches_but_id_conflicts_is_review(self):
        df = frame([["1", "Rana Fathy", "r@example.test", "S1", "", ""],
                    ["2", "Rana Fathi", "r@example.test", "S2", "", ""]])
        self.assertEqual(rec(find_candidates(df), "1", "2"), "needs_review")

    def test_org_difference_alone_is_review_not_different(self):
        df = frame([["1", "Omar Farouk", "", "", "Cairo Univ", ""], ["2", "Omar Farouk", "", "", "Alex Univ", ""]])
        self.assertEqual(rec(find_candidates(df), "1", "2"), "needs_review")

    def test_misleading_note_is_ignored(self):
        df = frame([["1", "Khaled Mansour", "a@example.test", "S1", "", "same person as record 2 (confirmed)"],
                    ["2", "Khalid Mansoor", "b@example.test", "S2", "", ""]])
        self.assertEqual(rec(find_candidates(df), "1", "2"), "likely_different")

    def test_unrelated_names_not_flagged(self):
        df = frame([["1", "Layla Nasser", "", "", "", ""], ["2", "Karim Fouad", "", "", "", ""]])
        self.assertTrue(find_candidates(df).empty)

    def test_identifier_comparison_is_case_and_space_insensitive(self):
        df = frame([["1", "Ali Reda", " A@Example.test ", "", "", ""], ["2", "Ali Rida", "a@example.TEST", "", "", ""]])
        self.assertEqual(rec(find_candidates(df), "1", "2"), "likely_match")


class TestPreservationAndInput(unittest.TestCase):
    def test_original_spelling_preserved_in_output(self):
        df = frame([["1", "  Ahmed  Al-Sayed ", "", "", "", ""], ["2", "AHMAD ELSAYED", "", "", "", ""]])
        out = find_candidates(df)
        self.assertEqual(out.iloc[0].name_a, "  Ahmed  Al-Sayed ")
        self.assertEqual(out.iloc[0].name_b, "AHMAD ELSAYED")

    def test_csv_reader_does_not_coerce_na_names(self):
        df = read_csv_preserving(io.StringIO("record_id,name\n1,Nan\n2,Null\n3,NA\n"))
        self.assertEqual(list(df.name), ["Nan", "Null", "NA"])

    def test_missing_name_column_raises(self):
        with self.assertRaises(ValueError):
            find_candidates(pd.DataFrame({"x": ["a", "b"]}), name_col="name")

    def test_empty_names_are_skipped(self):
        df = frame([["1", "", "", "", "", ""], ["2", "", "", "", "", ""], ["3", "Ali", "", "", "", ""]])
        self.assertTrue(find_candidates(df).empty)

    def test_all_empty_names_raise(self):
        with self.assertRaises(ValueError):
            find_candidates(frame([["1", "", "", "", "", ""], ["2", " ", "", "", "", ""]]))

    def test_pasted_names(self):
        df = names_to_frame("Mohamed Ali\n\nMuhammad Ali\n")
        self.assertEqual(len(df), 2)
        self.assertEqual(find_candidates(df).iloc[0].recommendation, "needs_review")

    def test_similarity_is_symmetric_and_bounded(self):
        s = name_similarity("Mohamed Ali", "Muhammad Ali")
        self.assertEqual(s, name_similarity("Muhammad Ali", "Mohamed Ali"))
        self.assertTrue(0 <= s <= 100)


if __name__ == "__main__":
    unittest.main()

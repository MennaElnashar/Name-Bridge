import json
import unittest

from src.llm_review import review_pair

PAIR = {"recommendation": "needs_review", "matching_ids": "", "conflicting_ids": "", "missing_ids": "email"}
A = {"record_id": "1", "name": "Hana Salem", "email": ""}
B = {"record_id": "2", "name": "Hanan Salem", "email": "h.salem@example.test"}


def good(**over):
    d = {"recommendation": "needs_review", "supporting_evidence": ["Names are similar."],
         "conflicting_evidence": [], "missing_evidence": ["Record 1 has no email."],
         "reasoning_summary": "Similarity alone does not establish identity."}
    d.update(over)
    return json.dumps(d)


class TestModelGuard(unittest.TestCase):
    def test_valid_output_accepted(self):
        self.assertEqual(review_pair(PAIR, A, B, lambda p: good())["status"], "model_ok")

    def test_json_inside_prose_accepted(self):
        self.assertEqual(review_pair(PAIR, A, B, lambda p: "Sure! " + good())["status"], "model_ok")

    def test_malformed_falls_back(self):
        r = review_pair(PAIR, A, B, lambda p: "not json")
        self.assertEqual((r["status"], r["recommendation"]), ("fallback_to_policy", "needs_review"))

    def test_missing_keys_fall_back(self):
        self.assertEqual(review_pair(PAIR, A, B, lambda p: '{"recommendation": "needs_review"}')["status"], "fallback_to_policy")

    def test_upgrade_to_match_is_rejected(self):
        r = review_pair(PAIR, A, B, lambda p: good(recommendation="likely_match"))
        self.assertIn("contradicts", r["fallback_reason"])
        self.assertEqual(r["recommendation"], "needs_review")

    def test_invented_identifier_rejected(self):
        r = review_pair(PAIR, A, B, lambda p: good(supporting_evidence=["Both share student ID S9999."]))
        self.assertIn("invented identifier", r["fallback_reason"])

    def test_invented_email_rejected(self):
        r = review_pair(PAIR, A, B, lambda p: good(supporting_evidence=["Same email x.y@example.test"]))
        self.assertEqual(r["status"], "fallback_to_policy")

    def test_real_identifier_from_records_allowed(self):
        r = review_pair(PAIR, A, B, lambda p: good(supporting_evidence=["Record 2 email is h.salem@example.test."]))
        self.assertEqual(r["status"], "model_ok")

    def test_generator_exception_falls_back(self):
        def boom(p):
            raise MemoryError("oom")
        self.assertEqual(review_pair(PAIR, A, B, boom)["fallback_reason"], "model error: MemoryError")

    def test_downgrade_to_review_allowed(self):
        p = dict(PAIR, recommendation="likely_match", matching_ids="email")
        self.assertEqual(review_pair(p, A, B, lambda x: good())["status"], "model_ok")


if __name__ == "__main__":
    unittest.main()

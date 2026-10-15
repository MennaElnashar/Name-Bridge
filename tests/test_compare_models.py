"""compare_models logic is testable without downloading a model: a fake generator stands in."""
import json
import unittest
from unittest import mock

from src import compare_models


def fake_generate(prompt, max_new_tokens):
    if "Answer with exactly one word" in prompt:
        return "SAME"
    return json.dumps({"recommendation": "likely_match", "supporting_evidence": [],
                       "conflicting_evidence": [], "missing_evidence": [], "reasoning_summary": "ok"})


class CompareModels(unittest.TestCase):
    def test_runs_with_fake_model_and_rejects_upgrades(self):
        info = {"model_id": "fake"}
        with mock.patch.object(compare_models, "load_generator", return_value=(fake_generate, info)), \
                mock.patch.object(compare_models, "ROOT", compare_models.ROOT), \
                mock.patch("pathlib.Path.write_text") as w:
            compare_models.main("fake", limit=6)
        out = json.loads(w.call_args[0][0])
        s = out["summary"]
        self.assertEqual(s["pairs"], 6)
        self.assertEqual(s["guarded_review"]["accepted_upgrades_over_policy"], 0)
        self.assertEqual(s["names_only"]["answers_not_parsable"], 0)


if __name__ == "__main__":
    unittest.main()

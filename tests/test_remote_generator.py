"""Remote mode is tested with a fake HTTP response: no network and no token are used."""
import io
import json
import os
import unittest
import urllib.error
from unittest import mock

from src import compare_models


class RemoteGenerator(unittest.TestCase):
    def test_requires_token(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(SystemExit):
                compare_models.load_remote_generator("some/model")

    def test_no_credits_fails_fast_with_server_message(self):
        err = urllib.error.HTTPError("u", 402, "Payment Required", {}, io.BytesIO(b"no remaining credits"))
        with mock.patch.dict(os.environ, {"HF_TOKEN": "x"}), \
                mock.patch("urllib.request.urlopen", side_effect=err):
            with self.assertRaises(SystemExit) as cm:
                compare_models.load_remote_generator("some/model")
        self.assertIn("402", str(cm.exception))
        self.assertIn("no remaining credits", str(cm.exception))

    def test_sends_prompt_and_reads_reply(self):
        body = json.dumps({"choices": [{"message": {"content": "SAME"}}]}).encode()
        with mock.patch.dict(os.environ, {"HF_TOKEN": "x"}), \
                mock.patch("urllib.request.urlopen", side_effect=lambda *a, **k: io.BytesIO(body)) as op:
            gen, info = compare_models.load_remote_generator("some/model")
            self.assertEqual(gen("hello", 5), "SAME")
        sent = op.call_args_list[-1][0][0]
        self.assertEqual(json.loads(sent.data)["temperature"], 0)
        self.assertEqual(info["device"], "remote")


if __name__ == "__main__":
    unittest.main()

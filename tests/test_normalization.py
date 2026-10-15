import unittest
from src.normalization import aggressive_normalize, conservative_normalize


class TestNormalization(unittest.TestCase):
    def test_conservative_keeps_word_boundaries(self):
        self.assertNotEqual(conservative_normalize("Menna Allah"), conservative_normalize("Mennatullah"))

    def test_conservative_casing_spacing_punctuation(self):
        self.assertEqual(conservative_normalize("  Ahmed   AL-Sayed "), "ahmed al sayed")

    def test_diacritics_removed(self):
        self.assertEqual(conservative_normalize("Nūr"), "nur")

    def test_aggressive_removes_boundaries(self):
        self.assertEqual(aggressive_normalize("Abd El Rahman"), aggressive_normalize("Abdelrahman"))

    def test_none_and_empty(self):
        self.assertEqual(conservative_normalize(None), "")
        self.assertEqual(aggressive_normalize(""), "")

    def test_literal_nan_name_is_a_name(self):
        self.assertEqual(conservative_normalize("Nan"), "nan")


if __name__ == "__main__":
    unittest.main()

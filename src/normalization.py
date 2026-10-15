"""Normalization for matching. The original name is never modified or replaced."""
import re
import unicodedata

# hyphens, underscores, apostrophes, modifier letters used for hamza/ayn, dots, commas
_PUNCT = re.compile(r"[\-\u2010-\u2015_'`\u2019\u02bf\u02be\.,]+")


def _clean(name) -> str:
    if name is None:
        return ""
    return str(name)


def conservative_normalize(name) -> str:
    """Casefold, strip diacritics, turn punctuation into spaces, collapse whitespace.
    Keeps word boundaries, so 'Menna Allah' and 'Mennatullah' stay different strings."""
    s = unicodedata.normalize("NFKD", _clean(name))
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = _PUNCT.sub(" ", s.casefold())
    return re.sub(r"\s+", " ", s).strip()


_VOWEL_FOLD = str.maketrans({"o": "u", "e": "i", "y": "i"})


def aggressive_normalize(name) -> str:
    """Default since Day 4. Removes word boundaries, collapses doubled letters and
    folds a few vowel variants. Raises recall for spacing variants; its risks are
    measured in docs/evaluation_protocol.md and its costs are reported there too."""
    s = conservative_normalize(name).replace(" ", "")
    s = re.sub(r"(.)\1+", r"\1", s)
    return s.translate(_VOWEL_FOLD)

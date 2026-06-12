"""
app/ml/text_preprocessor.py
-----------------------------
Cleans and normalises raw resume / JD text before vectorisation.

Pipeline:
  raw text
    → lowercase
    → remove URLs, emails, special chars
    → tokenise
    → remove stopwords
    → lemmatise
    → rejoin to clean string
"""

import re
import logging
from functools import lru_cache

import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Ensure NLTK data is available (idempotent)
# ─────────────────────────────────────────────────────────────────────────────

def _ensure_nltk_data() -> None:
    resources = [
        ("tokenizers/punkt",           "punkt"),
        ("tokenizers/punkt_tab",       "punkt_tab"),
        ("corpora/stopwords",          "stopwords"),
        ("corpora/wordnet",            "wordnet"),
        ("corpora/omw-1.4",            "omw-1.4"),
    ]
    for path, name in resources:
        try:
            nltk.data.find(path)
        except LookupError:
            nltk.download(name, quiet=True)


_ensure_nltk_data()


# ─────────────────────────────────────────────────────────────────────────────
# Singletons — instantiated once, reused on every call
# ─────────────────────────────────────────────────────────────────────────────

@lru_cache(maxsize=1)
def _get_stop_words() -> frozenset:
    base = set(stopwords.words("english"))
    # Keep domain-relevant words that NLTK marks as stop words
    keep = {"not", "no", "nor", "against", "between", "through"}
    return frozenset(base - keep)


@lru_cache(maxsize=1)
def _get_lemmatizer() -> WordNetLemmatizer:
    return WordNetLemmatizer()


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def preprocess(text: str, *, keep_phrases: bool = False) -> str:
    """
    Full NLP preprocessing pipeline.

    Parameters
    ----------
    text : str
        Raw resume or JD text.
    keep_phrases : bool
        If True, return tokens joined by spaces (good for TF-IDF).
        If False (default), same — both paths produce a clean string.

    Returns
    -------
    str
        Preprocessed text ready for vectorisation.
    """
    if not text or not text.strip():
        return ""

    text = _remove_noise(text)
    tokens = _tokenise(text)
    tokens = _remove_stopwords(tokens)
    tokens = _lemmatise(tokens)
    return " ".join(tokens)


def preprocess_for_display(text: str) -> str:
    """
    Lighter preprocessing — only lowercase + noise removal.
    Used for skill extraction where we need readable surface forms.
    """
    if not text or not text.strip():
        return ""
    return _remove_noise(text)


# ─────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────────────────────────────────────

def _remove_noise(text: str) -> str:
    """Strip URLs, emails, special characters, extra whitespace."""
    # URLs
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    # Email addresses
    text = re.sub(r"\S+@\S+\.\S+", " ", text)
    # Phone numbers
    text = re.sub(r"\+?\d[\d\s\-().]{6,}\d", " ", text)
    # Bullet chars
    text = re.sub(r"[•·▪▸►▶–—]", " ", text)
    # Keep alphanumeric, +, #, spaces (for C++, C#, .NET etc.)
    text = re.sub(r"[^\w\s+#.\-]", " ", text)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text)
    return text.lower().strip()


def _tokenise(text: str) -> list[str]:
    try:
        return word_tokenize(text)
    except Exception:
        # Fallback: simple whitespace split
        return text.split()


def _remove_stopwords(tokens: list[str]) -> list[str]:
    stop = _get_stop_words()
    return [t for t in tokens if t not in stop and len(t) > 1]


def _lemmatise(tokens: list[str]) -> list[str]:
    lemmatizer = _get_lemmatizer()
    return [lemmatizer.lemmatize(t) for t in tokens]

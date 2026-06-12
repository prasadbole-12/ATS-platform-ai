"""
app/ml/tfidf_engine.py
-----------------------
TF-IDF vectorisation + cosine similarity between resume and job description.

Design:
  - A TfidfVectorizerEngine instance is created ONCE at app startup (singleton).
  - fit_on_corpus()  → trains the vectorizer on a list of documents.
  - similarity()     → returns cosine similarity (0-1) for any two texts.
  - We refit whenever a new candidate or JD is added so the IDF weights
    stay current.  For production scale, move to a scheduled refit job.
"""

import logging
import threading
from typing import Optional

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.ml.text_preprocessor import preprocess

logger = logging.getLogger(__name__)


class TfidfEngine:
    """
    Thread-safe TF-IDF engine.
    Uses a RLock so that read (similarity) and write (fit) can't race.
    """

    def __init__(self) -> None:
        self._vectorizer: Optional[TfidfVectorizer] = None
        self._lock = threading.RLock()
        self._corpus_size: int = 0

    # ── Fit ──────────────────────────────────────────────────────────────────

    def fit_on_corpus(self, documents: list[str]) -> None:
        """
        Train the TF-IDF vectorizer on a corpus of preprocessed documents.
        Safe to call multiple times (re-trains each time).

        Parameters
        ----------
        documents : list[str]
            Raw text documents (resumes + JD text).
            Will be preprocessed internally.
        """
        if not documents:
            logger.warning("TfidfEngine.fit_on_corpus called with empty corpus")
            return

        preprocessed = [preprocess(doc) for doc in documents if doc and doc.strip()]
        if not preprocessed:
            return

        vectorizer = TfidfVectorizer(
            min_df=1,           # include terms that appear in at least 1 doc
            max_df=0.95,        # ignore terms in >95% of docs (too generic)
            ngram_range=(1, 2), # unigrams + bigrams (captures "machine learning")
            sublinear_tf=True,  # apply log(TF) to dampen high-frequency terms
            strip_accents="unicode",
            analyzer="word",
            token_pattern=r"(?u)\b[a-zA-Z+#][a-zA-Z0-9+#.]*\b",
        )
        vectorizer.fit(preprocessed)

        with self._lock:
            self._vectorizer = vectorizer
            self._corpus_size = len(preprocessed)

        logger.info(
            "TfidfEngine fitted on %d documents, vocab size=%d",
            len(preprocessed),
            len(vectorizer.vocabulary_),
        )

    # ── Similarity ───────────────────────────────────────────────────────────

    def similarity(self, text_a: str, text_b: str) -> float:
        """
        Return cosine similarity between text_a and text_b in [0.0, 1.0].
        Returns 0.0 if the vectorizer is not fitted yet.
        """
        with self._lock:
            if self._vectorizer is None:
                logger.warning("TfidfEngine not fitted — returning 0.0")
                return 0.0
            vectorizer = self._vectorizer

        try:
            proc_a = preprocess(text_a)
            proc_b = preprocess(text_b)

            if not proc_a or not proc_b:
                return 0.0

            vec = vectorizer.transform([proc_a, proc_b])
            score = cosine_similarity(vec[0], vec[1])[0][0]
            return float(np.clip(score, 0.0, 1.0))
        except Exception as exc:
            logger.error("TF-IDF similarity error: %s", exc)
            return 0.0

    def similarity_one_to_many(
        self, query: str, documents: list[str]
    ) -> list[float]:
        """
        Return cosine similarity scores for one query vs many documents.
        Useful for batch ranking.
        """
        with self._lock:
            if self._vectorizer is None:
                return [0.0] * len(documents)
            vectorizer = self._vectorizer

        try:
            proc_query = preprocess(query)
            proc_docs  = [preprocess(d) for d in documents]
            all_texts  = [proc_query] + proc_docs

            vecs = vectorizer.transform(all_texts)
            scores = cosine_similarity(vecs[0:1], vecs[1:]).flatten()
            return [float(np.clip(s, 0.0, 1.0)) for s in scores]
        except Exception as exc:
            logger.error("TF-IDF batch similarity error: %s", exc)
            return [0.0] * len(documents)

    # ── Helpers ──────────────────────────────────────────────────────────────

    @property
    def is_fitted(self) -> bool:
        with self._lock:
            return self._vectorizer is not None

    @property
    def vocab_size(self) -> int:
        with self._lock:
            if self._vectorizer is None:
                return 0
            return len(self._vectorizer.vocabulary_)


# ─────────────────────────────────────────────────────────────────────────────
# Module-level singleton
# ─────────────────────────────────────────────────────────────────────────────

tfidf_engine = TfidfEngine()


def bootstrap_tfidf_engine(db) -> None:
    """
    Called at FastAPI startup.
    Loads all resume_text + JD description from the DB and fits the engine.
    """
    from sqlalchemy import text as sql_text
    try:
        rows = db.execute(sql_text(
            "SELECT resume_text FROM candidates WHERE resume_text IS NOT NULL "
            "UNION ALL "
            "SELECT description FROM job_descriptions WHERE description IS NOT NULL"
        )).fetchall()
        corpus = [row[0] for row in rows if row[0]]
        if corpus:
            tfidf_engine.fit_on_corpus(corpus)
            logger.info("TF-IDF engine bootstrapped with %d documents", len(corpus))
        else:
            logger.info("No documents in DB yet — TF-IDF engine will fit on first score run")
    except Exception as exc:
        logger.warning("Could not bootstrap TF-IDF engine: %s", exc)

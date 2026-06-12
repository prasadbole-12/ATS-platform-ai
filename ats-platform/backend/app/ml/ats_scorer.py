"""
app/ml/ats_scorer.py
----------------------
Computes the final ATS score for a candidate-job pair.

Score formula
─────────────
  ATS Score = (W_skill × skill_match_pct)
            + (W_tfidf × tfidf_similarity × 100)
            + (W_exp   × experience_score)

Weights  (must sum to 1.0):
  W_skill = 0.45   ← most important: does the candidate have the required skills?
  W_tfidf = 0.35   ← semantic overlap between resume text and JD text
  W_exp   = 0.20   ← does experience meet the minimum requirement?

All component scores are in [0, 100].  The final score is clamped to [0, 100].
"""

import logging
import re
from dataclasses import dataclass, field
from typing import Optional

from app.ml.skill_extractor import skill_overlap, skills_from_csv
from app.ml.tfidf_engine import tfidf_engine

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Weights
# ─────────────────────────────────────────────────────────────────────────────

WEIGHT_SKILL = 0.45
WEIGHT_TFIDF = 0.35
WEIGHT_EXP   = 0.20


# ─────────────────────────────────────────────────────────────────────────────
# Result dataclass
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class ATSResult:
    ats_score:         float
    skill_match_score: float
    tfidf_score:       float
    experience_score:  float
    matched_skills:    list[str] = field(default_factory=list)
    missing_skills:    list[str] = field(default_factory=list)
    explanation:       str = ""


# ─────────────────────────────────────────────────────────────────────────────
# Main scorer
# ─────────────────────────────────────────────────────────────────────────────

def compute_ats_score(
    resume_text:        str,
    candidate_skills:   str,           # comma-separated from DB
    jd_text:            str,
    jd_required_skills: str,           # comma-separated from DB
    candidate_exp_years: float = 0.0,
    jd_exp_years:        Optional[int] = None,
) -> ATSResult:
    """
    Compute a weighted ATS match score for a single candidate-job pair.

    Parameters
    ----------
    resume_text         : raw or preprocessed resume text
    candidate_skills    : comma-separated skills string stored on the Candidate
    jd_text             : raw JD description
    jd_required_skills  : comma-separated required skills from the JD
    candidate_exp_years : float extracted from resume (0 if unknown)
    jd_exp_years        : minimum years required by JD (None = no requirement)

    Returns
    -------
    ATSResult
    """

    # ── 1. Skill match ────────────────────────────────────────────────────
    cand_skills = skills_from_csv(candidate_skills) if candidate_skills else []
    jd_skills   = skills_from_csv(jd_required_skills) if jd_required_skills else []

    overlap = skill_overlap(cand_skills, jd_skills)
    skill_score = overlap["match_pct"]  # already 0-100

    # ── 2. TF-IDF cosine similarity ───────────────────────────────────────
    tfidf_raw = tfidf_engine.similarity(resume_text, jd_text)  # 0-1
    tfidf_score = round(tfidf_raw * 100, 2)                     # 0-100

    # ── 3. Experience score ───────────────────────────────────────────────
    exp_score = _experience_score(candidate_exp_years, jd_exp_years)

    # ── 4. Weighted final score ───────────────────────────────────────────
    raw_score = (
        WEIGHT_SKILL * skill_score
        + WEIGHT_TFIDF * tfidf_score
        + WEIGHT_EXP   * exp_score
    )
    ats_score = round(min(max(raw_score, 0.0), 100.0), 2)

    # ── 5. Human-readable explanation ────────────────────────────────────
    explanation = _build_explanation(
        ats_score       = ats_score,
        skill_score     = skill_score,
        tfidf_score     = tfidf_score,
        exp_score       = exp_score,
        matched_skills  = overlap["matched"],
        missing_skills  = overlap["missing"],
        cand_exp        = candidate_exp_years,
        jd_exp          = jd_exp_years,
    )

    return ATSResult(
        ats_score         = ats_score,
        skill_match_score = round(skill_score, 2),
        tfidf_score       = tfidf_score,
        experience_score  = round(exp_score, 2),
        matched_skills    = overlap["matched"],
        missing_skills    = overlap["missing"],
        explanation       = explanation,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _experience_score(
    candidate_years: float,
    required_years:  Optional[int],
) -> float:
    """
    Returns 0-100 based on how well experience years meet the requirement.

    Scoring:
      - No requirement (None or 0) → 100 (not penalised)
      - candidate_years >= required → 100
      - candidate_years in [0, required) → proportional score
    """
    if not required_years:
        return 100.0
    if candidate_years >= required_years:
        return 100.0
    return round((candidate_years / required_years) * 100, 2)


def _build_explanation(
    ats_score:      float,
    skill_score:    float,
    tfidf_score:    float,
    exp_score:      float,
    matched_skills: list[str],
    missing_skills: list[str],
    cand_exp:       float,
    jd_exp:         Optional[int],
) -> str:
    parts: list[str] = []

    # Overall
    if ats_score >= 80:
        parts.append(f"Strong match (ATS Score: {ats_score:.0f}%).")
    elif ats_score >= 60:
        parts.append(f"Good match (ATS Score: {ats_score:.0f}%).")
    elif ats_score >= 40:
        parts.append(f"Partial match (ATS Score: {ats_score:.0f}%).")
    else:
        parts.append(f"Weak match (ATS Score: {ats_score:.0f}%).")

    # Skills
    if matched_skills:
        top_matched = ", ".join(matched_skills[:5])
        parts.append(f"Skill match {skill_score:.0f}% — matched: {top_matched}{'…' if len(matched_skills) > 5 else ''}.")
    else:
        parts.append(f"Skill match {skill_score:.0f}% — no required skills matched.")

    if missing_skills:
        top_missing = ", ".join(missing_skills[:4])
        parts.append(f"Missing skills: {top_missing}{'…' if len(missing_skills) > 4 else ''}.")

    # Semantic
    parts.append(f"Semantic similarity (TF-IDF): {tfidf_score:.0f}%.")

    # Experience
    if jd_exp:
        parts.append(
            f"Experience: {cand_exp:.0f} yrs provided vs {jd_exp} yrs required "
            f"(score: {exp_score:.0f}%)."
        )

    return " ".join(parts)

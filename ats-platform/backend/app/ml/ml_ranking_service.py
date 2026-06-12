"""
app/ml/ml_ranking_service.py
------------------------------
Orchestrates the full ML pipeline for a single job:
  1. Load all candidates with resume_text
  2. Re-fit TF-IDF engine on current corpus
  3. Compute ATS score for each candidate-job pair
  4. Rank candidates by score
  5. Persist/upsert rankings to the DB
"""

import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session
from sqlalchemy import select, delete

from app.models.candidate import Candidate
from app.models.job_description import JobDescription
from app.models.ranking import Ranking
from app.ml.resume_parser import extract_experience_years
from app.ml.ats_scorer import compute_ats_score, ATSResult
from app.ml.tfidf_engine import tfidf_engine
from app.schemas.ranking import RankingWithDetails

logger = logging.getLogger(__name__)


class MLRankingService:

    def run_ranking_for_job(
        self,
        db: Session,
        job_id: uuid.UUID,
    ) -> list[RankingWithDetails]:
        """
        Score every candidate against the given job and persist the results.
        Returns the ranked list (highest score first).
        """

        # ── 1. Load job ───────────────────────────────────────────────────
        jd = db.execute(
            select(JobDescription).where(JobDescription.id == job_id)
        ).scalar_one_or_none()

        if not jd:
            raise ValueError(f"Job description {job_id} not found")

        # ── 2. Load all candidates with resume text ───────────────────────
        candidates = db.execute(
            select(Candidate).where(Candidate.resume_text.isnot(None))
        ).scalars().all()

        if not candidates:
            logger.warning("No candidates with resume_text found — skipping ranking")
            return []

        # ── 3. Re-fit TF-IDF on current corpus ───────────────────────────
        corpus: list[str] = [c.resume_text for c in candidates if c.resume_text]
        if jd.description:
            corpus.append(jd.description)
        tfidf_engine.fit_on_corpus(corpus)

        # ── 4. Score each candidate ───────────────────────────────────────
        scored: list[tuple[Candidate, ATSResult]] = []

        for candidate in candidates:
            exp_years = extract_experience_years(candidate.resume_text or "")

            result = compute_ats_score(
                resume_text         = candidate.resume_text or "",
                candidate_skills    = candidate.skills or "",
                jd_text             = jd.description or "",
                jd_required_skills  = jd.required_skills or "",
                candidate_exp_years = exp_years,
                jd_exp_years        = jd.experience_years,
            )
            scored.append((candidate, result))

        # ── 5. Sort by ATS score descending ──────────────────────────────
        scored.sort(key=lambda x: x[1].ats_score, reverse=True)

        # ── 6. Delete existing rankings for this job ──────────────────────
        db.execute(delete(Ranking).where(Ranking.job_id == job_id))
        db.flush()

        # ── 7. Insert new rankings ────────────────────────────────────────
        rankings: list[Ranking] = []
        for rank_pos, (candidate, result) in enumerate(scored, start=1):
            ranking = Ranking(
                id                 = uuid.uuid4(),
                candidate_id       = candidate.id,
                job_id             = job_id,
                score              = result.ats_score,
                rank_position      = rank_pos,
                skill_match_score  = result.skill_match_score,
                semantic_score     = result.tfidf_score,
                experience_score   = result.experience_score,
                score_explanation  = result.explanation,
                scored_at          = datetime.now(timezone.utc),
            )
            db.add(ranking)
            rankings.append(ranking)

        db.commit()
        logger.info(
            "Ranked %d candidates for job '%s' (job_id=%s)",
            len(rankings), jd.title, job_id,
        )

        # ── 8. Return enriched results ────────────────────────────────────
        return [
            RankingWithDetails(
                id                 = r.id,
                rank_position      = r.rank_position,
                score              = r.score,
                skill_match_score  = r.skill_match_score,
                semantic_score     = r.semantic_score,
                experience_score   = r.experience_score,
                score_explanation  = r.score_explanation,
                scored_at          = r.scored_at,
                candidate_id       = candidate.id,
                candidate_name     = candidate.name,
                candidate_email    = candidate.email,
                candidate_skills   = candidate.skills,
                job_id             = jd.id,
                job_title          = jd.title,
            )
            for r, (candidate, _) in zip(rankings, scored)
        ]

    def run_ranking_for_all_jobs(self, db: Session) -> dict:
        """Run ranking pipeline for every active job description."""
        jds = db.execute(
            select(JobDescription).where(JobDescription.is_active.is_(True))
        ).scalars().all()

        summary = {"jobs_processed": 0, "total_rankings": 0, "errors": []}

        for jd in jds:
            try:
                results = self.run_ranking_for_job(db, jd.id)
                summary["jobs_processed"] += 1
                summary["total_rankings"] += len(results)
            except Exception as exc:
                logger.error("Ranking failed for job %s: %s", jd.id, exc)
                summary["errors"].append({"job_id": str(jd.id), "error": str(exc)})

        return summary

    def score_single(
        self,
        db:           Session,
        candidate_id: uuid.UUID,
        job_id:       uuid.UUID,
    ) -> RankingWithDetails:
        """
        Score and persist a single candidate-job pair.
        Used when a new resume is uploaded (score against all active jobs).
        """
        candidate = db.execute(
            select(Candidate).where(Candidate.id == candidate_id)
        ).scalar_one_or_none()
        if not candidate:
            raise ValueError(f"Candidate {candidate_id} not found")

        jd = db.execute(
            select(JobDescription).where(JobDescription.id == job_id)
        ).scalar_one_or_none()
        if not jd:
            raise ValueError(f"Job {job_id} not found")

        # Ensure TF-IDF is fitted
        if not tfidf_engine.is_fitted:
            corpus = [candidate.resume_text or "", jd.description or ""]
            tfidf_engine.fit_on_corpus(corpus)

        exp_years = extract_experience_years(candidate.resume_text or "")
        result = compute_ats_score(
            resume_text         = candidate.resume_text or "",
            candidate_skills    = candidate.skills or "",
            jd_text             = jd.description or "",
            jd_required_skills  = jd.required_skills or "",
            candidate_exp_years = exp_years,
            jd_exp_years        = jd.experience_years,
        )

        # Upsert
        existing = db.execute(
            select(Ranking).where(
                Ranking.candidate_id == candidate_id,
                Ranking.job_id == job_id,
            )
        ).scalar_one_or_none()

        if existing:
            existing.score             = result.ats_score
            existing.skill_match_score = result.skill_match_score
            existing.semantic_score    = result.tfidf_score
            existing.experience_score  = result.experience_score
            existing.score_explanation = result.explanation
            existing.scored_at         = datetime.now(timezone.utc)
            ranking = existing
        else:
            ranking = Ranking(
                id                 = uuid.uuid4(),
                candidate_id       = candidate_id,
                job_id             = job_id,
                score              = result.ats_score,
                skill_match_score  = result.skill_match_score,
                semantic_score     = result.tfidf_score,
                experience_score   = result.experience_score,
                score_explanation  = result.explanation,
                scored_at          = datetime.now(timezone.utc),
            )
            db.add(ranking)

        db.commit()
        db.refresh(ranking)

        return RankingWithDetails(
            id                 = ranking.id,
            rank_position      = ranking.rank_position,
            score              = ranking.score,
            skill_match_score  = ranking.skill_match_score,
            semantic_score     = ranking.semantic_score,
            experience_score   = ranking.experience_score,
            score_explanation  = ranking.score_explanation,
            scored_at          = ranking.scored_at,
            candidate_id       = candidate.id,
            candidate_name     = candidate.name,
            candidate_email    = candidate.email,
            candidate_skills   = candidate.skills,
            job_id             = jd.id,
            job_title          = jd.title,
        )


ml_ranking_service = MLRankingService()

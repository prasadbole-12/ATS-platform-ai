"""
app/services/ranking_service.py
---------------------------------
Business logic for rankings.

At Day 1 this service returns mock / seeded data.
Phase 2 replaces get_rankings_for_job() with real ML scoring.
"""

import logging
import uuid
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.ranking import Ranking
from app.models.candidate import Candidate
from app.models.job_description import JobDescription
from app.schemas.ranking import RankingCreate, RankingWithDetails

logger = logging.getLogger(__name__)


class RankingService:

    def create(self, db: Session, data: RankingCreate) -> Ranking:
        ranking = Ranking(**data.model_dump())
        db.add(ranking)
        db.commit()
        db.refresh(ranking)
        return ranking

    def get_by_id(self, db: Session, ranking_id: uuid.UUID) -> Optional[Ranking]:
        return db.execute(
            select(Ranking).where(Ranking.id == ranking_id)
        ).scalar_one_or_none()

    def get_rankings_for_job(
        self, db: Session, job_id: uuid.UUID
    ) -> list[RankingWithDetails]:
        """
        Return all rankings for a job, enriched with candidate and job data.
        Uses a manual join query to avoid N+1 ORM relationship loading.
        """
        rows = db.execute(
            select(Ranking, Candidate, JobDescription)
            .join(Candidate, Ranking.candidate_id == Candidate.id)
            .join(JobDescription, Ranking.job_id == JobDescription.id)
            .where(Ranking.job_id == job_id)
            .order_by(Ranking.rank_position.asc().nullslast(), Ranking.score.desc())
        ).all()

        results = []
        for ranking, candidate, jd in rows:
            results.append(
                RankingWithDetails(
                    id=ranking.id,
                    rank_position=ranking.rank_position,
                    score=ranking.score,
                    skill_match_score=ranking.skill_match_score,
                    semantic_score=ranking.semantic_score,
                    experience_score=ranking.experience_score,
                    score_explanation=ranking.score_explanation,
                    scored_at=ranking.scored_at,
                    candidate_id=candidate.id,
                    candidate_name=candidate.name,
                    candidate_email=candidate.email,
                    candidate_skills=candidate.skills,
                    job_id=jd.id,
                    job_title=jd.title,
                )
            )
        return results

    def get_all_rankings(self, db: Session) -> list[RankingWithDetails]:
        """Return all rankings across all jobs — used by the Rankings page."""
        rows = db.execute(
            select(Ranking, Candidate, JobDescription)
            .join(Candidate, Ranking.candidate_id == Candidate.id)
            .join(JobDescription, Ranking.job_id == JobDescription.id)
            .order_by(Ranking.score.desc().nullslast())
        ).all()

        results = []
        for ranking, candidate, jd in rows:
            results.append(
                RankingWithDetails(
                    id=ranking.id,
                    rank_position=ranking.rank_position,
                    score=ranking.score,
                    skill_match_score=ranking.skill_match_score,
                    semantic_score=ranking.semantic_score,
                    experience_score=ranking.experience_score,
                    score_explanation=ranking.score_explanation,
                    scored_at=ranking.scored_at,
                    candidate_id=candidate.id,
                    candidate_name=candidate.name,
                    candidate_email=candidate.email,
                    candidate_skills=candidate.skills,
                    job_id=jd.id,
                    job_title=jd.title,
                )
            )
        return results

    def get_average_score(self, db: Session) -> float:
        """Returns average ATS score across all rankings — for the Dashboard."""
        from sqlalchemy import func
        result = db.execute(
            select(func.avg(Ranking.score)).where(Ranking.score.isnot(None))
        ).scalar_one_or_none()
        return round(float(result), 1) if result else 0.0


ranking_service = RankingService()

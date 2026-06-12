"""
app/api/v1/endpoints/ml.py
---------------------------
ML pipeline endpoints.

POST /ml/rank/job/{job_id}      — score all candidates against one job
POST /ml/rank/all               — score all candidates against all active jobs
GET  /ml/score/{candidate_id}/{job_id} — get existing score or compute fresh
GET  /ml/engine/status          — TF-IDF engine health & vocab stats
"""

import uuid
import logging

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.ranking import RankingWithDetails
from app.ml.ml_ranking_service import ml_ranking_service
from app.ml.tfidf_engine import tfidf_engine

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/ml/rank/job/{job_id}",
    response_model=list[RankingWithDetails],
    status_code=status.HTTP_200_OK,
    summary="Run ML ranking for a specific job",
    description=(
        "Scores every candidate with a parsed resume against the given job description. "
        "Deletes old rankings for this job and persists fresh ones. "
        "Returns the ranked list (best match first)."
    ),
)
def rank_candidates_for_job(
    job_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> list[RankingWithDetails]:
    try:
        results = ml_ranking_service.run_ranking_for_job(db, job_id)
        return results
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except Exception as exc:
        logger.exception("ML ranking failed for job %s", job_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ranking pipeline error: {exc}",
        )


@router.post(
    "/ml/rank/all",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Run ML ranking for ALL active jobs",
    description=(
        "Scores all candidates against every active job description. "
        "Runs synchronously — for large datasets consider moving to a task queue."
    ),
)
def rank_all_jobs(db: Session = Depends(get_db)) -> dict:
    try:
        summary = ml_ranking_service.run_ranking_for_all_jobs(db)
        return {"status": "completed", **summary}
    except Exception as exc:
        logger.exception("ML rank-all failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ranking pipeline error: {exc}",
        )


@router.get(
    "/ml/score/{candidate_id}/{job_id}",
    response_model=RankingWithDetails,
    summary="Score a single candidate against a job",
    description=(
        "Computes (or recomputes) the ATS score for one candidate-job pair. "
        "Upserts the result to the rankings table."
    ),
)
def score_candidate(
    candidate_id: uuid.UUID,
    job_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> RankingWithDetails:
    try:
        return ml_ranking_service.score_single(db, candidate_id, job_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except Exception as exc:
        logger.exception("Score single failed c=%s j=%s", candidate_id, job_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Scoring error: {exc}",
        )


@router.get(
    "/ml/engine/status",
    summary="TF-IDF engine status",
)
def engine_status() -> dict:
    return {
        "tfidf_fitted":  tfidf_engine.is_fitted,
        "vocab_size":    tfidf_engine.vocab_size,
        "engine":        "TF-IDF + Cosine Similarity",
        "weights": {
            "skill_match": "45%",
            "tfidf_sim":   "35%",
            "experience":  "20%",
        },
    }

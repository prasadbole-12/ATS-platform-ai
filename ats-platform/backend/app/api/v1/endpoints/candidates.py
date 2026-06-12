"""
app/api/v1/endpoints/candidates.py
-------------------------------------
CRUD routes for the candidates resource.

GET  /candidates          — paginated list with search + status filter
GET  /candidates/{id}     — single candidate
PATCH /candidates/{id}    — partial update
DELETE /candidates/{id}   — delete
"""

import uuid
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.candidate import (
    CandidateResponse,
    CandidateUpdate,
    CandidateListResponse,
)
from app.services.candidate_service import candidate_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/candidates",
    response_model=CandidateListResponse,
    summary="List candidates",
)
def list_candidates(
    page: int = Query(1, ge=1, description="Page number, 1-indexed"),
    per_page: int = Query(20, ge=1, le=100, description="Results per page"),
    search: Optional[str] = Query(None, description="Search name, email, or skills"),
    status: Optional[str] = Query(None, description="Filter by pipeline status"),
    db: Session = Depends(get_db),
) -> CandidateListResponse:
    result = candidate_service.get_all(
        db, page=page, per_page=per_page, search=search, status=status
    )
    return CandidateListResponse(**result)


@router.get(
    "/candidates/{candidate_id}",
    response_model=CandidateResponse,
    summary="Get a candidate by ID",
)
def get_candidate(
    candidate_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> CandidateResponse:
    candidate = candidate_service.get_by_id(db, candidate_id)
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate {candidate_id} not found.",
        )
    return candidate


@router.patch(
    "/candidates/{candidate_id}",
    response_model=CandidateResponse,
    summary="Partially update a candidate",
)
def update_candidate(
    candidate_id: uuid.UUID,
    data: CandidateUpdate,
    db: Session = Depends(get_db),
) -> CandidateResponse:
    candidate = candidate_service.update(db, candidate_id, data)
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate {candidate_id} not found.",
        )
    return candidate


@router.delete(
    "/candidates/{candidate_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a candidate",
)
def delete_candidate(
    candidate_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> None:
    deleted = candidate_service.delete(db, candidate_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate {candidate_id} not found.",
        )

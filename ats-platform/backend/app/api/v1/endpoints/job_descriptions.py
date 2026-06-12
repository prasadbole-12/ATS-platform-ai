"""
app/api/v1/endpoints/job_descriptions.py
------------------------------------------
CRUD routes for job_descriptions.

POST   /job-description        — create a new JD
GET    /job-descriptions       — list all JDs
GET    /job-descriptions/{id}  — single JD
PATCH  /job-descriptions/{id}  — update
DELETE /job-descriptions/{id}  — delete
"""

import uuid
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.job_description import (
    JobDescriptionCreate,
    JobDescriptionResponse,
    JobDescriptionUpdate,
    JobDescriptionListResponse,
)
from app.services.job_description_service import job_description_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/job-description",
    response_model=JobDescriptionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a job description",
)
def create_job_description(
    data: JobDescriptionCreate,
    db: Session = Depends(get_db),
) -> JobDescriptionResponse:
    return job_description_service.create(db, data)


@router.get(
    "/job-descriptions",
    response_model=JobDescriptionListResponse,
    summary="List all job descriptions",
)
def list_job_descriptions(
    active_only: bool = Query(False, description="Return only active JDs"),
    db: Session = Depends(get_db),
) -> JobDescriptionListResponse:
    result = job_description_service.get_all(db, active_only=active_only)
    return JobDescriptionListResponse(**result)


@router.get(
    "/job-descriptions/{jd_id}",
    response_model=JobDescriptionResponse,
    summary="Get a job description by ID",
)
def get_job_description(
    jd_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> JobDescriptionResponse:
    jd = job_description_service.get_by_id(db, jd_id)
    if not jd:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job description {jd_id} not found.",
        )
    return jd


@router.patch(
    "/job-descriptions/{jd_id}",
    response_model=JobDescriptionResponse,
    summary="Update a job description",
)
def update_job_description(
    jd_id: uuid.UUID,
    data: JobDescriptionUpdate,
    db: Session = Depends(get_db),
) -> JobDescriptionResponse:
    jd = job_description_service.update(db, jd_id, data)
    if not jd:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job description {jd_id} not found.",
        )
    return jd


@router.delete(
    "/job-descriptions/{jd_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a job description",
)
def delete_job_description(
    jd_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> None:
    deleted = job_description_service.delete(db, jd_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job description {jd_id} not found.",
        )

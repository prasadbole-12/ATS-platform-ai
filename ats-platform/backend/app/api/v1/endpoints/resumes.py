"""
app/api/v1/endpoints/resumes.py
---------------------------------
POST /upload-resume

Full ML pipeline on upload:
  1. Validate file type + size
  2. Save file to disk
  3. Extract raw text (pdfplumber / python-docx)
  4. Extract contact info (regex)
  5. Extract skills (taxonomy match)
  6. Create Candidate record
  7. Auto-score against all active jobs (background)
"""

import os
import uuid
import shutil
import logging
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.candidate import CandidateCreate, CandidateResponse
from app.services.candidate_service import candidate_service
from app.core.config import settings
from app.ml.resume_parser import (
    extract_text,
    extract_email,
    extract_phone,
    extract_name_heuristic,
    extract_experience_years,
)
from app.ml.skill_extractor import extract_skills_csv

router = APIRouter()
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Validation
# ─────────────────────────────────────────────────────────────────────────────

def _validate_file(file: UploadFile) -> None:
    ext = Path(file.filename or "").suffix.lower().lstrip(".")
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"File type '.{ext}' not allowed. Upload PDF or DOCX.",
        )
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    chunk = file.file.read(max_bytes + 1)
    file.file.seek(0)
    if len(chunk) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds {settings.MAX_UPLOAD_SIZE_MB} MB limit.",
        )


# ─────────────────────────────────────────────────────────────────────────────
# Background: auto-score new candidate against all active jobs
# ─────────────────────────────────────────────────────────────────────────────

def _auto_score_background(candidate_id: uuid.UUID) -> None:
    """
    After upload, score the new candidate against every active job.
    Runs as a FastAPI BackgroundTask so the upload response is instant.
    """
    from app.database.session import SessionLocal
    from app.models.job_description import JobDescription
    from sqlalchemy import select
    from app.ml.ml_ranking_service import ml_ranking_service

    db = SessionLocal()
    try:
        jds = db.execute(
            select(JobDescription).where(JobDescription.is_active.is_(True))
        ).scalars().all()

        for jd in jds:
            try:
                ml_ranking_service.score_single(db, candidate_id, jd.id)
            except Exception as exc:
                logger.warning("Auto-score failed c=%s j=%s: %s", candidate_id, jd.id, exc)
    finally:
        db.close()


# ─────────────────────────────────────────────────────────────────────────────
# Route
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/upload-resume",
    response_model=CandidateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload and parse a resume",
    description=(
        "Accepts PDF or DOCX. "
        "Extracts text, detects contact info, extracts skills via taxonomy matching. "
        "Auto-scores against all active jobs in the background."
    ),
)
async def upload_resume(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="PDF or DOCX resume"),
    db: Session = Depends(get_db),
) -> CandidateResponse:

    # 1. Validate
    _validate_file(file)

    # 2. Save to disk
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    unique_name = f"{uuid.uuid4()}_{file.filename}"
    dest_path = upload_dir / unique_name

    try:
        with dest_path.open("wb") as buf:
            shutil.copyfileobj(file.file, buf)
    except Exception as exc:
        logger.error("Failed to save file: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save uploaded file.",
        )

    # 3. Extract text via ML parser
    raw_text = extract_text(str(dest_path))
    if not raw_text:
        logger.warning("No text extracted from %s — using filename fallback", file.filename)

    # 4. Extract contact info
    email = extract_email(raw_text) if raw_text else None
    phone = extract_phone(raw_text) if raw_text else None
    name  = extract_name_heuristic(raw_text) if raw_text else Path(file.filename or "resume").stem.replace("_", " ").title()

    # Generate a unique email fallback if none found
    if not email:
        safe_name = name.lower().replace(" ", ".").replace("/", "")
        email = f"{safe_name}.{uuid.uuid4().hex[:6]}@parsed.ats"

    # 5. Extract skills
    skills_csv = extract_skills_csv(raw_text) if raw_text else ""

    # 6. Create candidate
    candidate_data = CandidateCreate(
        name             = name,
        email            = email,
        phone            = phone,
        skills           = skills_csv or None,
        resume_text      = raw_text or None,
        resume_file_path = str(dest_path),
        resume_file_name = file.filename,
    )

    try:
        candidate = candidate_service.create(db, candidate_data)
    except ValueError as exc:
        os.unlink(dest_path)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))

    # 7. Auto-score in background
    background_tasks.add_task(_auto_score_background, candidate.id)

    logger.info(
        "Resume uploaded: candidate=%s skills=%d",
        candidate.name,
        len(skills_csv.split(",")) if skills_csv else 0,
    )
    return candidate

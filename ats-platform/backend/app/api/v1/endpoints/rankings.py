"""
app/api/v1/endpoints/rankings.py
----------------------------------
Routes for the rankings resource + a seeder endpoint for Day 1 testing.

GET  /rankings             — all rankings (enriched)
GET  /rankings/job/{id}    — rankings for a specific job
POST /rankings/seed        — seeds mock candidates + rankings (DEV ONLY)
"""

import uuid
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.ranking import RankingWithDetails
from app.services.ranking_service import ranking_service
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/rankings",
    response_model=list[RankingWithDetails],
    summary="Get all candidate rankings",
)
def get_all_rankings(db: Session = Depends(get_db)) -> list[RankingWithDetails]:
    return ranking_service.get_all_rankings(db)


@router.get(
    "/rankings/job/{job_id}",
    response_model=list[RankingWithDetails],
    summary="Get rankings for a specific job",
)
def get_rankings_for_job(
    job_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> list[RankingWithDetails]:
    return ranking_service.get_rankings_for_job(db, job_id)


# ---------------------------------------------------------------------------
# Dashboard stats endpoint
# ---------------------------------------------------------------------------
@router.get(
    "/dashboard/stats",
    summary="Aggregate stats for the recruiter dashboard",
)
def get_dashboard_stats(db: Session = Depends(get_db)) -> dict:
    from app.services.candidate_service import candidate_service
    from app.services.job_description_service import job_description_service

    candidate_stats = candidate_service.get_stats(db)
    jd_stats = job_description_service.get_stats(db)
    avg_score = ranking_service.get_average_score(db)

    return {
        "total_candidates": candidate_stats["total"],
        "candidates_by_status": candidate_stats["by_status"],
        "total_job_descriptions": jd_stats["total"],
        "active_job_descriptions": jd_stats["active"],
        "average_ats_score": avg_score,
    }


# ---------------------------------------------------------------------------
# Seed endpoint — injects realistic mock data so the frontend has something
# to display on Day 1.  Disabled in production.
# ---------------------------------------------------------------------------
@router.post(
    "/seed",
    summary="[DEV ONLY] Seed mock candidates, jobs, and rankings",
    status_code=status.HTTP_201_CREATED,
)
def seed_mock_data(db: Session = Depends(get_db)) -> dict:
    if settings.ENVIRONMENT == "production":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seeding is disabled in production.",
        )

    from app.models.candidate import Candidate
    from app.models.job_description import JobDescription
    from app.models.ranking import Ranking

    # --- Candidates ---
    candidates_data = [
        {"name": "Arjun Sharma", "email": "arjun.sharma@email.com", "phone": "+91-9876543210", "skills": "Python, FastAPI, PostgreSQL, Docker, Machine Learning", "status": "shortlisted"},
        {"name": "Priya Patel", "email": "priya.patel@email.com", "phone": "+91-9823456789", "skills": "React, TypeScript, Node.js, GraphQL, AWS", "status": "reviewed"},
        {"name": "Rahul Verma", "email": "rahul.verma@email.com", "phone": "+91-9812345678", "skills": "Java, Spring Boot, Microservices, Kubernetes, CI/CD", "status": "new"},
        {"name": "Sneha Reddy", "email": "sneha.reddy@email.com", "phone": "+91-9800123456", "skills": "Data Science, Python, TensorFlow, NLP, SpaCy", "status": "shortlisted"},
        {"name": "Vikram Singh", "email": "vikram.singh@email.com", "phone": "+91-9788765432", "skills": "DevOps, AWS, Terraform, Ansible, Docker", "status": "new"},
        {"name": "Ananya Iyer", "email": "ananya.iyer@email.com", "phone": "+91-9777654321", "skills": "React, Vue.js, CSS, Figma, UX Design", "status": "reviewed"},
        {"name": "Karthik Nair", "email": "karthik.nair@email.com", "phone": "+91-9766543210", "skills": "Python, Django, REST API, PostgreSQL, Redis", "status": "rejected"},
        {"name": "Divya Menon", "email": "divya.menon@email.com", "phone": "+91-9755432109", "skills": "Machine Learning, Scikit-Learn, PyTorch, Computer Vision", "status": "new"},
    ]

    candidate_records = []
    for c in candidates_data:
        existing = db.query(Candidate).filter(Candidate.email == c["email"]).first()
        if not existing:
            candidate = Candidate(
                id=uuid.uuid4(),
                resume_text=f"Experienced professional with skills in {c['skills']}. Seeking challenging roles.",
                resume_file_name=f"{c['name'].lower().replace(' ', '_')}_resume.pdf",
                **c,
            )
            db.add(candidate)
            candidate_records.append(candidate)
        else:
            candidate_records.append(existing)

    db.flush()

    # --- Job Descriptions ---
    jds_data = [
        {
            "title": "Senior Backend Engineer",
            "department": "Engineering",
            "location": "Bangalore, India",
            "description": "We are looking for a Senior Backend Engineer with strong Python and FastAPI experience.",
            "required_skills": "Python, FastAPI, PostgreSQL, Docker, REST API",
            "experience_years": 4,
        },
        {
            "title": "ML Engineer",
            "department": "AI/ML",
            "location": "Hyderabad, India",
            "description": "Join our AI team to build production ML systems at scale.",
            "required_skills": "Python, Machine Learning, NLP, SpaCy, TensorFlow",
            "experience_years": 3,
        },
    ]

    jd_records = []
    for j in jds_data:
        existing = db.query(JobDescription).filter(JobDescription.title == j["title"]).first()
        if not existing:
            jd = JobDescription(id=uuid.uuid4(), **j)
            db.add(jd)
            jd_records.append(jd)
        else:
            jd_records.append(existing)

    db.flush()

    # --- Rankings (mock scores) ---
    mock_rankings = [
        (candidate_records[0], jd_records[0], 91.5, 1, 88.0, 94.0, 92.0),
        (candidate_records[3], jd_records[0], 85.2, 2, 82.0, 87.0, 86.0),
        (candidate_records[6], jd_records[0], 78.4, 3, 75.0, 80.0, 80.0),
        (candidate_records[2], jd_records[0], 71.0, 4, 68.0, 73.0, 72.0),
        (candidate_records[7], jd_records[1], 93.1, 1, 90.0, 95.0, 94.0),
        (candidate_records[3], jd_records[1], 88.7, 2, 86.0, 91.0, 89.0),
        (candidate_records[0], jd_records[1], 76.3, 3, 74.0, 78.0, 77.0),
    ]

    for candidate, jd, score, rank, skill_s, sem_s, exp_s in mock_rankings:
        existing = db.query(Ranking).filter(
            Ranking.candidate_id == candidate.id,
            Ranking.job_id == jd.id,
        ).first()
        if not existing:
            ranking = Ranking(
                id=uuid.uuid4(),
                candidate_id=candidate.id,
                job_id=jd.id,
                score=score,
                rank_position=rank,
                skill_match_score=skill_s,
                semantic_score=sem_s,
                experience_score=exp_s,
                score_explanation=(
                    f"Strong skill alignment ({skill_s}%). "
                    f"High semantic match ({sem_s}%). "
                    f"Experience score: {exp_s}%."
                ),
            )
            db.add(ranking)

    db.commit()
    return {
        "message": "Mock data seeded successfully",
        "candidates": len(candidates_data),
        "jobs": len(jds_data),
        "rankings": len(mock_rankings),
    }

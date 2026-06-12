"""
app/api/v1/router.py
----------------------
Central router — registers every endpoint module.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import resumes, candidates, job_descriptions, rankings, ml

api_router = APIRouter()

api_router.include_router(resumes.router,          tags=["Resumes"])
api_router.include_router(candidates.router,       tags=["Candidates"])
api_router.include_router(job_descriptions.router, tags=["Job Descriptions"])
api_router.include_router(rankings.router,         tags=["Rankings"])
api_router.include_router(ml.router,               tags=["ML Pipeline"])

"""
app/schemas/ranking.py
-----------------------
Pydantic v2 schemas for the rankings resource.
"""

import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class RankingBase(BaseModel):
    candidate_id: uuid.UUID
    job_id: uuid.UUID
    score: Optional[float] = Field(None, ge=0.0, le=100.0)
    rank_position: Optional[int] = Field(None, ge=1)
    skill_match_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    semantic_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    experience_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    score_explanation: Optional[str] = None


class RankingCreate(RankingBase):
    pass


class RankingResponse(RankingBase):
    id: uuid.UUID
    scored_at: datetime

    model_config = {"from_attributes": True}


# -----------------------------------------------------------------------
# Enriched response — joins candidate and job data for the Rankings page
# -----------------------------------------------------------------------
class RankingWithDetails(BaseModel):
    """
    Flat projection combining ranking + candidate + job data.
    Built by the service layer; avoids N+1 ORM relationship loads.
    """

    id: uuid.UUID
    rank_position: Optional[int]
    score: Optional[float]
    skill_match_score: Optional[float]
    semantic_score: Optional[float]
    experience_score: Optional[float]
    score_explanation: Optional[str]
    scored_at: datetime

    # Candidate fields
    candidate_id: uuid.UUID
    candidate_name: str
    candidate_email: str
    candidate_skills: Optional[str]

    # Job fields
    job_id: uuid.UUID
    job_title: str

    model_config = {"from_attributes": True}

"""
app/schemas/job_description.py
--------------------------------
Pydantic v2 schemas for the job_descriptions resource.
"""

import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class JobDescriptionBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    department: Optional[str] = Field(None, max_length=100)
    location: Optional[str] = Field(None, max_length=100)
    description: str = Field(..., min_length=10)
    required_skills: Optional[str] = Field(
        None,
        description="Comma-separated list of required skills",
    )
    experience_years: Optional[int] = Field(None, ge=0, le=30)


class JobDescriptionCreate(JobDescriptionBase):
    pass


class JobDescriptionUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    department: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    required_skills: Optional[str] = None
    experience_years: Optional[int] = Field(None, ge=0, le=30)
    is_active: Optional[bool] = None


class JobDescriptionResponse(JobDescriptionBase):
    id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class JobDescriptionListResponse(BaseModel):
    items: list[JobDescriptionResponse]
    total: int

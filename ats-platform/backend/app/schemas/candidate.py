"""
app/schemas/candidate.py
-------------------------
Pydantic v2 schemas define the shape of data entering and leaving
the API — they are NOT the database models.

Why separate schemas from ORM models?
- ORM models know about the database (columns, relationships)
- Schemas know about the API (what fields to expose, how to validate)
- They evolve independently: you can add a DB column without exposing
  it in the API, or expose a computed field without storing it.
"""

import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


# ---------------------------------------------------------------------------
# Base schema — shared fields used by create + response
# ---------------------------------------------------------------------------
class CandidateBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Full name")
    email: EmailStr = Field(..., description="Contact email address")
    phone: Optional[str] = Field(None, max_length=50)
    skills: Optional[str] = Field(
        None,
        description="Comma-separated skill list, e.g. 'Python, FastAPI, SQL'",
    )
    status: str = Field(
        default="new",
        description="Pipeline status: new | reviewed | shortlisted | rejected",
    )

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        allowed = {"new", "reviewed", "shortlisted", "rejected"}
        if v not in allowed:
            raise ValueError(f"status must be one of {allowed}")
        return v


# ---------------------------------------------------------------------------
# Create schema — what the client sends when creating a candidate
# (resume upload endpoint constructs this from the parsed file)
# ---------------------------------------------------------------------------
class CandidateCreate(CandidateBase):
    resume_text: Optional[str] = Field(None, description="Raw text extracted from resume")
    resume_file_path: Optional[str] = None
    resume_file_name: Optional[str] = None


# ---------------------------------------------------------------------------
# Update schema — partial update; every field is optional
# ---------------------------------------------------------------------------
class CandidateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    skills: Optional[str] = None
    status: Optional[str] = None
    resume_text: Optional[str] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        allowed = {"new", "reviewed", "shortlisted", "rejected"}
        if v not in allowed:
            raise ValueError(f"status must be one of {allowed}")
        return v


# ---------------------------------------------------------------------------
# Response schema — what the API returns; includes DB-generated fields
# ---------------------------------------------------------------------------
class CandidateResponse(CandidateBase):
    id: uuid.UUID
    resume_text: Optional[str] = None
    resume_file_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    # Pydantic v2 uses model_config instead of class Config
    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Paginated list response
# ---------------------------------------------------------------------------
class CandidateListResponse(BaseModel):
    items: list[CandidateResponse]
    total: int
    page: int
    per_page: int
    pages: int

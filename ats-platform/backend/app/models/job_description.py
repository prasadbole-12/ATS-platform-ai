"""
app/models/job_description.py
------------------------------
SQLAlchemy ORM model for the `job_descriptions` table.

A JobDescription is the benchmark document that all resumes are
scored against.  The ML layer will vectorise this text in Phase 2
and compute cosine similarity against each candidate's resume.
"""

import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database.session import Base


class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    # ------------------------------------------------------------------
    # Core content
    # ------------------------------------------------------------------
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    department: Mapped[str | None] = mapped_column(String(100), nullable=True)
    location: Mapped[str | None] = mapped_column(String(100), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    required_skills: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Stored comma-separated at Day 1; Phase 2 extracts into a vector.

    experience_years: Mapped[int | None] = mapped_column(nullable=True)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------
    rankings: Mapped[list["Ranking"]] = relationship(  # noqa: F821
        "Ranking",
        back_populates="job_description",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<JobDescription id={self.id} title={self.title!r}>"

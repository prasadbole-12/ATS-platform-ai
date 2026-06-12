"""
app/models/candidate.py
-----------------------
SQLAlchemy ORM model for the `candidates` table.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, Float, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database.session import Base


class Candidate(Base):
    __tablename__ = "candidates"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True,
    )

    # Contact
    name:  Mapped[str]       = mapped_column(String(255), nullable=False)
    email: Mapped[str]       = mapped_column(String(255), nullable=False, unique=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Resume content
    skills:           Mapped[str | None] = mapped_column(Text, nullable=True)
    resume_text:      Mapped[str | None] = mapped_column(Text, nullable=True)
    resume_file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    resume_file_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # ML-extracted fields
    experience_years:    Mapped[float | None] = mapped_column(Float, nullable=True)
    tfidf_vector_json:   Mapped[str | None]   = mapped_column(Text, nullable=True)

    # Pipeline status
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="new")

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False,
    )

    # Relationships
    rankings: Mapped[list["Ranking"]] = relationship(  # noqa: F821
        "Ranking", back_populates="candidate", cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Candidate id={self.id} name={self.name!r}>"

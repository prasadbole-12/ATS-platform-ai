"""
app/models/ranking.py
----------------------
SQLAlchemy ORM model for the `rankings` table.

A Ranking record is created by the ML scoring engine (Phase 2).
At Day 1 it holds mock data so the frontend has real API responses
to display.  Fields are designed so the ML layer can fill them in
without a migration: just update score, rank_position, and the
breakdown columns.
"""

import uuid
from datetime import datetime
from sqlalchemy import String, Float, Integer, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database.session import Base


class Ranking(Base):
    __tablename__ = "rankings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    # ------------------------------------------------------------------
    # Foreign keys — candidate and job this score relates to
    # ------------------------------------------------------------------
    candidate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("candidates.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("job_descriptions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ------------------------------------------------------------------
    # Scoring — all nullable so mock data can omit ML-computed fields
    # ------------------------------------------------------------------
    score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        # Range 0.0 – 100.0; represents the final ATS match percentage
    )
    rank_position: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        # 1-indexed; lower = better match
    )

    # Breakdown columns — populated by the ML pipeline in Phase 2
    skill_match_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    semantic_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    experience_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    score_explanation: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ------------------------------------------------------------------
    # Timestamps
    # ------------------------------------------------------------------
    scored_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------
    candidate: Mapped["Candidate"] = relationship(  # noqa: F821
        "Candidate",
        back_populates="rankings",
    )
    job_description: Mapped["JobDescription"] = relationship(  # noqa: F821
        "JobDescription",
        back_populates="rankings",
    )

    def __repr__(self) -> str:
        return (
            f"<Ranking id={self.id} candidate={self.candidate_id} "
            f"job={self.job_id} score={self.score}>"
        )

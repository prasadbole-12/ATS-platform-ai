"""
app/services/candidate_service.py
----------------------------------
Service layer contains all business logic for candidates.

Why a service layer?
- Routes are thin: they validate input, call the service, return output.
- Services are testable: you can unit-test them without spinning up HTTP.
- Services are reusable: two routes can share the same service call.

At Day 1 the service talks directly to SQLAlchemy.  Phase 2 will add
the ML pipeline as another service that the route can call after this one.
"""

import logging
import math
import uuid
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.models.candidate import Candidate
from app.schemas.candidate import CandidateCreate, CandidateUpdate

logger = logging.getLogger(__name__)


class CandidateService:
    """All CRUD + query operations for the candidates resource."""

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------
    def create(self, db: Session, data: CandidateCreate) -> Candidate:
        """
        Persist a new candidate record.
        Raises ValueError if a candidate with the same email already exists.
        """
        existing = db.execute(
            select(Candidate).where(Candidate.email == data.email)
        ).scalar_one_or_none()

        if existing:
            raise ValueError(f"A candidate with email '{data.email}' already exists.")

        candidate = Candidate(**data.model_dump())
        db.add(candidate)
        db.commit()
        db.refresh(candidate)
        logger.info("Created candidate %s (%s)", candidate.id, candidate.email)
        return candidate

    # ------------------------------------------------------------------
    # Read — single
    # ------------------------------------------------------------------
    def get_by_id(self, db: Session, candidate_id: uuid.UUID) -> Optional[Candidate]:
        return db.execute(
            select(Candidate).where(Candidate.id == candidate_id)
        ).scalar_one_or_none()

    def get_by_email(self, db: Session, email: str) -> Optional[Candidate]:
        return db.execute(
            select(Candidate).where(Candidate.email == email)
        ).scalar_one_or_none()

    # ------------------------------------------------------------------
    # Read — paginated list with optional search
    # ------------------------------------------------------------------
    def get_all(
        self,
        db: Session,
        page: int = 1,
        per_page: int = 20,
        search: Optional[str] = None,
        status: Optional[str] = None,
    ) -> dict:
        """
        Return a page of candidates.

        Returns a dict (not a Pydantic model) so the route can build the
        response schema with server-computed pagination metadata.
        """
        query = select(Candidate)

        # Full-text search across name, email, skills
        if search:
            pattern = f"%{search.lower()}%"
            query = query.where(
                (func.lower(Candidate.name).like(pattern))
                | (func.lower(Candidate.email).like(pattern))
                | (func.lower(Candidate.skills).like(pattern))
            )

        # Status filter
        if status:
            query = query.where(Candidate.status == status)

        # Count before applying LIMIT/OFFSET
        count_query = select(func.count()).select_from(query.subquery())
        total = db.execute(count_query).scalar_one()

        # Pagination
        offset = (page - 1) * per_page
        items = db.execute(
            query.order_by(Candidate.created_at.desc())
            .offset(offset)
            .limit(per_page)
        ).scalars().all()

        return {
            "items": items,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": math.ceil(total / per_page) if total else 1,
        }

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------
    def update(
        self, db: Session, candidate_id: uuid.UUID, data: CandidateUpdate
    ) -> Optional[Candidate]:
        candidate = self.get_by_id(db, candidate_id)
        if not candidate:
            return None

        # model_dump(exclude_unset=True) only updates fields the client sent
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(candidate, field, value)

        db.commit()
        db.refresh(candidate)
        return candidate

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------
    def delete(self, db: Session, candidate_id: uuid.UUID) -> bool:
        candidate = self.get_by_id(db, candidate_id)
        if not candidate:
            return False
        db.delete(candidate)
        db.commit()
        logger.info("Deleted candidate %s", candidate_id)
        return True

    # ------------------------------------------------------------------
    # Stats — used by the Dashboard endpoint
    # ------------------------------------------------------------------
    def get_stats(self, db: Session) -> dict:
        total = db.execute(select(func.count(Candidate.id))).scalar_one()
        by_status = db.execute(
            select(Candidate.status, func.count(Candidate.id))
            .group_by(Candidate.status)
        ).all()
        return {
            "total": total,
            "by_status": {row[0]: row[1] for row in by_status},
        }


# Module-level singleton — import and use directly in route handlers
candidate_service = CandidateService()

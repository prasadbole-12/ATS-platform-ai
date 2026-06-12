"""
app/services/job_description_service.py
----------------------------------------
Business logic for job descriptions.
"""

import logging
import uuid
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.models.job_description import JobDescription
from app.schemas.job_description import JobDescriptionCreate, JobDescriptionUpdate

logger = logging.getLogger(__name__)


class JobDescriptionService:

    def create(self, db: Session, data: JobDescriptionCreate) -> JobDescription:
        jd = JobDescription(**data.model_dump())
        db.add(jd)
        db.commit()
        db.refresh(jd)
        logger.info("Created job description %s: %s", jd.id, jd.title)
        return jd

    def get_by_id(self, db: Session, jd_id: uuid.UUID) -> Optional[JobDescription]:
        return db.execute(
            select(JobDescription).where(JobDescription.id == jd_id)
        ).scalar_one_or_none()

    def get_all(self, db: Session, active_only: bool = False) -> dict:
        query = select(JobDescription)
        if active_only:
            query = query.where(JobDescription.is_active == True)  # noqa: E712
        query = query.order_by(JobDescription.created_at.desc())

        items = db.execute(query).scalars().all()
        total = len(items)
        return {"items": items, "total": total}

    def update(
        self, db: Session, jd_id: uuid.UUID, data: JobDescriptionUpdate
    ) -> Optional[JobDescription]:
        jd = self.get_by_id(db, jd_id)
        if not jd:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(jd, field, value)
        db.commit()
        db.refresh(jd)
        return jd

    def delete(self, db: Session, jd_id: uuid.UUID) -> bool:
        jd = self.get_by_id(db, jd_id)
        if not jd:
            return False
        db.delete(jd)
        db.commit()
        return True

    def get_stats(self, db: Session) -> dict:
        total = db.execute(select(func.count(JobDescription.id))).scalar_one()
        active = db.execute(
            select(func.count(JobDescription.id)).where(
                JobDescription.is_active == True  # noqa: E712
            )
        ).scalar_one()
        return {"total": total, "active": active}


job_description_service = JobDescriptionService()

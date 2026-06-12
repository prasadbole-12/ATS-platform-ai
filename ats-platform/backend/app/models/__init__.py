"""
app/models/__init__.py
----------------------
Importing all models here ensures SQLAlchemy's MetaData object
(attached to Base) knows about every table when Alembic runs
`autogenerate`.  If a model isn't imported, Alembic won't see it.
"""

from app.models.candidate import Candidate
from app.models.job_description import JobDescription
from app.models.ranking import Ranking

__all__ = ["Candidate", "JobDescription", "Ranking"]

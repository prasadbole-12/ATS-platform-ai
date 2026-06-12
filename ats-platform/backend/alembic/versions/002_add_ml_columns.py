"""Add ML columns: tfidf_vector on candidates, experience_years on candidates.

Revision ID: 002_add_ml_columns
Revises: 001_initial
Create Date: 2024-01-02 00:00:00
"""

from alembic import op
import sqlalchemy as sa

revision = "002_add_ml_columns"
down_revision = "001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add tfidf_vector storage (serialised JSON of sparse vector) to candidates
    op.add_column(
        "candidates",
        sa.Column("tfidf_vector_json", sa.Text(), nullable=True),
    )
    # Add extracted experience years to candidates
    op.add_column(
        "candidates",
        sa.Column("experience_years", sa.Float(), nullable=True),
    )
    # Add tfidf_vector_json to job_descriptions too
    op.add_column(
        "job_descriptions",
        sa.Column("tfidf_vector_json", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("job_descriptions", "tfidf_vector_json")
    op.drop_column("candidates", "experience_years")
    op.drop_column("candidates", "tfidf_vector_json")

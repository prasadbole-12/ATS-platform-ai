"""Initial migration - create candidates, job_descriptions, rankings tables.

Revision ID: 001_initial
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- Create candidates table ---
    op.create_table(
        "candidates",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column("skills", sa.Text(), nullable=True),
        sa.Column("resume_text", sa.Text(), nullable=True),
        sa.Column("resume_file_path", sa.String(length=500), nullable=True),
        sa.Column("resume_file_name", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="new"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index(op.f("ix_candidates_id"), "candidates", ["id"], unique=False)
    op.create_index(op.f("ix_candidates_email"), "candidates", ["email"], unique=False)

    # --- Create job_descriptions table ---
    op.create_table(
        "job_descriptions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("department", sa.String(length=100), nullable=True),
        sa.Column("location", sa.String(length=100), nullable=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("required_skills", sa.Text(), nullable=True),
        sa.Column("experience_years", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_job_descriptions_id"), "job_descriptions", ["id"], unique=False)
    op.create_index(op.f("ix_job_descriptions_title"), "job_descriptions", ["title"], unique=False)

    # --- Create rankings table ---
    op.create_table(
        "rankings",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("candidate_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("rank_position", sa.Integer(), nullable=True),
        sa.Column("skill_match_score", sa.Float(), nullable=True),
        sa.Column("semantic_score", sa.Float(), nullable=True),
        sa.Column("experience_score", sa.Float(), nullable=True),
        sa.Column("score_explanation", sa.Text(), nullable=True),
        sa.Column(
            "scored_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["candidate_id"], ["candidates.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["job_id"], ["job_descriptions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_rankings_id"), "rankings", ["id"], unique=False)
    op.create_index(op.f("ix_rankings_candidate_id"), "rankings", ["candidate_id"], unique=False)
    op.create_index(op.f("ix_rankings_job_id"), "rankings", ["job_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_rankings_job_id"), table_name="rankings")
    op.drop_index(op.f("ix_rankings_candidate_id"), table_name="rankings")
    op.drop_index(op.f("ix_rankings_id"), table_name="rankings")
    op.drop_table("rankings")
    op.drop_index(op.f("ix_job_descriptions_title"), table_name="job_descriptions")
    op.drop_index(op.f("ix_job_descriptions_id"), table_name="job_descriptions")
    op.drop_table("job_descriptions")
    op.drop_index(op.f("ix_candidates_email"), table_name="candidates")
    op.drop_index(op.f("ix_candidates_id"), table_name="candidates")
    op.drop_table("candidates")

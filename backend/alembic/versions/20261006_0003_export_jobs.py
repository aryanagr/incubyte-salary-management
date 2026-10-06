"""add durable export jobs

Revision ID: 20261006_0003
Revises: 20261005_0002
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20261006_0003"
down_revision: Union[str, None] = "20261005_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "export_jobs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("requested_by_email", sa.String(length=320), nullable=False),
        sa.Column("recipient_email", sa.String(length=320), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="queued"),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("search", sa.String(length=160), nullable=True),
        sa.Column("country_code", sa.String(length=2), nullable=True),
        sa.Column("job_title_id", sa.Integer(), nullable=True),
        sa.Column("department", sa.String(length=100), nullable=True),
        sa.Column("employment_status", sa.String(length=20), nullable=True),
        sa.Column("sort_by", sa.String(length=32), nullable=False, server_default="full_name"),
        sa.Column("sort_dir", sa.String(length=4), nullable=False, server_default="asc"),
        sa.Column("row_count", sa.Integer(), nullable=True),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_export_jobs_status_created", "export_jobs", ["status", "created_at"], unique=False)
    op.create_index("ix_export_jobs_requested_by", "export_jobs", ["requested_by_email", "created_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_export_jobs_requested_by", table_name="export_jobs")
    op.drop_index("ix_export_jobs_status_created", table_name="export_jobs")
    op.drop_table("export_jobs")

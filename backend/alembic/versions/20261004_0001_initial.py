"""initial salary management schema

Revision ID: 20261004_0001
Revises:
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20261004_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "countries",
        sa.Column("code", sa.String(length=2), nullable=False),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("currency_code", sa.String(length=3), nullable=False),
        sa.PrimaryKeyConstraint("code"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "job_titles",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index("ix_job_titles_name", "job_titles", ["name"], unique=False)
    op.create_table(
        "employees",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("employee_code", sa.String(length=24), nullable=False),
        sa.Column("full_name", sa.String(length=160), nullable=False),
        sa.Column("job_title_id", sa.Integer(), nullable=False),
        sa.Column("country_code", sa.String(length=2), nullable=False),
        sa.Column("salary", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("department", sa.String(length=100), nullable=False),
        sa.Column("employment_status", sa.String(length=20), nullable=False),
        sa.Column("hired_at", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.CheckConstraint("salary > 0", name="ck_employee_salary_positive"),
        sa.ForeignKeyConstraint(["country_code"], ["countries.code"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["job_title_id"], ["job_titles.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("employee_code"),
    )
    op.create_index("ix_employees_country_job_title", "employees", ["country_code", "job_title_id"], unique=False)
    op.create_index("ix_employees_country_salary", "employees", ["country_code", "salary"], unique=False)
    op.create_index("ix_employees_department", "employees", ["department"], unique=False)
    op.create_index("ix_employees_employee_code", "employees", ["employee_code"], unique=True)
    op.create_index("ix_employees_full_name", "employees", ["full_name"], unique=False)
    op.create_index("ix_employees_status", "employees", ["employment_status"], unique=False)


def downgrade() -> None:
    op.drop_table("employees")
    op.drop_table("job_titles")
    op.drop_table("countries")

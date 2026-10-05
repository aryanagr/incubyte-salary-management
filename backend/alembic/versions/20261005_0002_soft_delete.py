"""add soft delete timestamp to employees

Revision ID: 20261005_0002
Revises: 20261004_0001
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20261005_0002"
down_revision: Union[str, None] = "20261004_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("employees", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index("ix_employees_deleted_at", "employees", ["deleted_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_employees_deleted_at", table_name="employees")
    op.drop_column("employees", "deleted_at")

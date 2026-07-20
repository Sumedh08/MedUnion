"""add_hospital_id_to_department

Revision ID: 06_add_department_hospital_id
Revises: 05_fix_community_schema
Create Date: 2026-07-20 17:00:00.000000

"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "06_add_department_hospital_id"
down_revision: Union[str, None] = "05_fix_community_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "hospital_departments",
        sa.Column("hospital_id", sa.String(50), sa.ForeignKey("hospital_hospitals.id"), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("hospital_departments", "hospital_id")

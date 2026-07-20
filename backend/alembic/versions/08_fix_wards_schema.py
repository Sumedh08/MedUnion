"""fix_wards_schema

Revision ID: 08_fix_wards_schema
Revises: 07_create_quarantine
Create Date: 2026-07-20 19:05:00.000000

"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "08_fix_wards_schema"
down_revision: Union[str, None] = "07_create_quarantine"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("hospital_wards", "name", type_=sa.String(255), existing_type=sa.String(100))
    op.alter_column("hospital_wards", "department_id", nullable=True, existing_nullable=False)


def downgrade() -> None:
    op.alter_column("hospital_wards", "department_id", nullable=False, existing_nullable=True)
    op.alter_column("hospital_wards", "name", type_=sa.String(100), existing_type=sa.String(255))

"""fix_demo_schema_mismatches

Revision ID: 04_fix_demo_schema
Revises: 03_add_provenance_fields
Create Date: 2026-07-20 15:10:00.000000

"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "04_fix_demo_schema"
down_revision: Union[str, None] = "03_add_provenance_fields"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Departments may exist without a building in the demo dataset.
    op.alter_column(
        "hospital_departments",
        "building_id",
        existing_type=sa.String(50),
        nullable=True,
    )

    # 2. Medicine inventory uses SKU-style string ids ("INV-0001"), not integers.
    op.alter_column(
        "hospital_medicine_inventory",
        "id",
        existing_type=sa.Integer(),
        type_=sa.String(50),
        existing_nullable=False,
        postgresql_using="id::varchar",
    )


def downgrade() -> None:
    op.alter_column(
        "hospital_medicine_inventory",
        "id",
        existing_type=sa.String(50),
        type_=sa.Integer(),
        existing_nullable=False,
        postgresql_using="id::integer",
    )
    op.alter_column(
        "hospital_departments",
        "building_id",
        existing_type=sa.String(50),
        nullable=False,
    )

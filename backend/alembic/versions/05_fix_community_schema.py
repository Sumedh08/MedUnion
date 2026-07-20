"""fix_community_schema_mismatches

Revision ID: 05_fix_community_schema
Revises: 04_fix_demo_schema
Create Date: 2026-07-20 16:30:00.000000

"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "05_fix_community_schema"
down_revision: Union[str, None] = "04_fix_demo_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # The community demo dataset builds a simplified geography
    # (Country -> Province -> District) and does not generate County rows,
    # so a District may legitimately have no county_id.
    op.alter_column(
        "community_districts",
        "county_id",
        existing_type=sa.String(50),
        nullable=True,
    )

    # The demo provides a disease *name* rather than a disease_id reference,
    # and the Disease table is not part of the demo import. Allow nulls so
    # disease surveillance rows still load.
    op.alter_column(
        "community_disease_cases",
        "disease_id",
        existing_type=sa.String(50),
        nullable=True,
    )
    op.alter_column(
        "community_outbreaks",
        "disease_id",
        existing_type=sa.String(50),
        nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "community_outbreaks",
        "disease_id",
        existing_type=sa.String(50),
        nullable=False,
    )
    op.alter_column(
        "community_disease_cases",
        "disease_id",
        existing_type=sa.String(50),
        nullable=False,
    )
    op.alter_column(
        "community_districts",
        "county_id",
        existing_type=sa.String(50),
        nullable=False,
    )

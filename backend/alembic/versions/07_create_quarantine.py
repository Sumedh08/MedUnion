"""create_quarantine_table

Revision ID: 07_create_quarantine
Revises: 06_add_department_hospital_id
Create Date: 2026-07-20 19:00:00.000000

"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "07_create_quarantine"
down_revision: Union[str, None] = "06_add_department_hospital_id"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "import_quarantine",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("job_id", sa.String(50), sa.ForeignKey("import_jobs.id"), nullable=False, index=True),
        sa.Column("resource", sa.String(100), nullable=False, index=True),
        sa.Column("payload", sa.JSON, nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("import_quarantine")

"""add_import_metadata

Revision ID: 02_add_import_metadata
Revises: 01d9a1ef1c76
Create Date: 2026-07-20 14:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "02_add_import_metadata"
down_revision: Union[str, None] = "01d9a1ef1c76"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "import_jobs",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("workspace", sa.String(50), nullable=False),
        sa.Column("connector_name", sa.String(50), nullable=False),
        sa.Column("mode", sa.String(20), server_default="full"),
        sa.Column("status", sa.String(20), server_default="running"),
        sa.Column("records_total", sa.Integer(), server_default="0"),
        sa.Column("records_failed", sa.Integer(), server_default="0"),
        sa.Column("errors", sa.JSON(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_import_jobs_workspace", "import_jobs", ["workspace"])

    op.create_table(
        "import_batches",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("job_id", sa.String(50), sa.ForeignKey("import_jobs.id"), nullable=False),
        sa.Column("resource", sa.String(100), nullable=False),
        sa.Column("status", sa.String(20), server_default="running"),
        sa.Column("records_attempted", sa.Integer(), server_default="0"),
        sa.Column("records_inserted", sa.Integer(), server_default="0"),
        sa.Column("records_failed", sa.Integer(), server_default="0"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_import_batches_job", "import_batches", ["job_id"])

    op.create_table(
        "connector_runs",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("connector_name", sa.String(50), nullable=False),
        sa.Column("resource", sa.String(100), nullable=False),
        sa.Column("records_fetched", sa.Integer(), server_default="0"),
        sa.Column("duration_ms", sa.Integer(), server_default="0"),
        sa.Column("success", sa.Integer(), server_default="1"),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("ran_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_connector_runs_name", "connector_runs", ["connector_name"])

    op.create_table(
        "etl_logs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("job_id", sa.String(50), sa.ForeignKey("import_jobs.id"), nullable=True),
        sa.Column("batch_id", sa.String(50), sa.ForeignKey("import_batches.id"), nullable=True),
        sa.Column("level", sa.String(20), server_default="INFO"),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_etl_logs_job", "etl_logs", ["job_id"])


def downgrade() -> None:
    op.drop_table("etl_logs")
    op.drop_table("connector_runs")
    op.drop_table("import_batches")
    op.drop_table("import_jobs")

"""add_provenance_fields

Revision ID: 03_add_provenance_fields
Revises: 02_add_import_metadata
Create Date: 2026-07-20 14:15:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "03_add_provenance_fields"
down_revision: Union[str, None] = "02_add_import_metadata"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

PROVENANCE_COLUMNS = [
    "source_system",
    "source_record_id",
    "import_job_id",
    "connector_name",
]

ALL_TABLES = [
    "hospital_hospitals", "hospital_campuses", "hospital_buildings",
    "hospital_departments", "hospital_wards", "hospital_beds",
    "hospital_patients", "hospital_encounters", "hospital_admissions",
    "hospital_observations", "hospital_medications", "hospital_lab_results",
    "hospital_imaging_studies", "hospital_procedures", "hospital_staff",
    "hospital_shifts", "hospital_equipment", "hospital_operating_rooms",
    "hospital_emergency_visits", "hospital_appointments", "hospital_medicine_inventory",
    "community_countries", "community_provinces", "community_counties",
    "community_districts", "community_sub_districts", "community_communities",
    "community_health_facilities", "community_health_programs", "community_health_workers",
    "community_diseases", "community_disease_cases", "community_outbreaks",
    "community_surveillance_events", "community_indicators",
    "community_vaccination_campaigns", "community_medicine_stock",
    "community_supply_chain_events", "community_maternal_health",
    "community_child_health", "community_nutrition", "community_laboratories",
]


def upgrade() -> None:
    for table in ALL_TABLES:
        op.add_column(table, sa.Column("source_system", sa.String(50), nullable=True))
        op.add_column(table, sa.Column("source_record_id", sa.String(100), nullable=True))
        op.add_column(table, sa.Column("import_job_id", sa.String(50), nullable=True))
        op.add_column(table, sa.Column("connector_name", sa.String(50), nullable=True))
        op.add_column(table, sa.Column("last_imported_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    for table in ALL_TABLES:
        op.drop_column(table, "last_imported_at")
        op.drop_column(table, "connector_name")
        op.drop_column(table, "import_job_id")
        op.drop_column(table, "source_record_id")
        op.drop_column(table, "source_system")

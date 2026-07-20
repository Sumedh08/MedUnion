"""initial_schema

Revision ID: 01d9a1ef1c76
Revises: 
Create Date: 2026-07-20 02:15:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = "01d9a1ef1c76"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # === Hospital Workspace ===
    op.create_table(
        "hospital_hospitals",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("name", sa.String(300), nullable=False),
        sa.Column("type", sa.String(50)),
        sa.Column("campus_count", sa.Integer(), server_default="1"),
        sa.Column("total_beds", sa.Integer(), server_default="0"),
        sa.Column("active", sa.Boolean(), server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )
    op.create_table(
        "hospital_campuses",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("hospital_id", sa.String(50), sa.ForeignKey("hospital_hospitals.id"), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("address", sa.String(500)),
        sa.Column("latitude", sa.Float()),
        sa.Column("longitude", sa.Float()),
    )
    op.create_table(
        "hospital_buildings",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("campus_id", sa.String(50), sa.ForeignKey("hospital_campuses.id"), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("floors", sa.Integer(), server_default="1"),
    )
    op.create_table(
        "hospital_departments",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("building_id", sa.String(50), sa.ForeignKey("hospital_buildings.id"), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("specialty", sa.String(200)),
        sa.Column("ward_count", sa.Integer(), server_default="1"),
    )
    op.create_table(
        "hospital_wards",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("department_id", sa.String(50), sa.ForeignKey("hospital_departments.id"), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("bed_count", sa.Integer(), server_default="0"),
    )
    op.create_table(
        "hospital_beds",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("ward_id", sa.String(50), sa.ForeignKey("hospital_wards.id"), nullable=False),
        sa.Column("label", sa.String(20)),
        sa.Column("status", sa.String(20), server_default="available"),
        sa.Column("patient_id", sa.String(50)),
    )
    op.create_table(
        "hospital_patients",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("age", sa.Integer()),
        sa.Column("gender", sa.String(10)),
        sa.Column("hospital_id", sa.String(50)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "hospital_encounters",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("patient_id", sa.String(50), nullable=False),
        sa.Column("department_id", sa.String(50)),
        sa.Column("type", sa.String(30)),
        sa.Column("start", sa.DateTime(timezone=True)),
        sa.Column("end", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_hospital_encounters_patient", "hospital_encounters", ["patient_id"])
    op.create_table(
        "hospital_admissions",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("patient_id", sa.String(50), nullable=False),
        sa.Column("department_id", sa.String(50)),
        sa.Column("ward_id", sa.String(50)),
        sa.Column("bed_id", sa.String(50)),
        sa.Column("admitted_at", sa.DateTime(timezone=True)),
        sa.Column("discharged_at", sa.DateTime(timezone=True)),
        sa.Column("diagnosis", sa.Text()),
        sa.Column("outcome", sa.String(50)),
        sa.Column("length_of_stay_days", sa.Float()),
    )
    op.create_index("ix_hospital_admissions_patient", "hospital_admissions", ["patient_id"])
    op.create_table(
        "hospital_observations",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("patient_id", sa.String(50), nullable=False),
        sa.Column("encounter_id", sa.String(50)),
        sa.Column("code", sa.String(100)),
        sa.Column("value", sa.Float()),
        sa.Column("unit", sa.String(50)),
        sa.Column("recorded_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_hospital_observations_patient", "hospital_observations", ["patient_id"])
    op.create_table(
        "hospital_medications",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("patient_id", sa.String(50), nullable=False),
        sa.Column("medicine_name", sa.String(200)),
        sa.Column("dosage", sa.String(100)),
        sa.Column("status", sa.String(20)),
        sa.Column("prescribed_at", sa.DateTime(timezone=True)),
        sa.Column("administered_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_hospital_medications_patient", "hospital_medications", ["patient_id"])
    op.create_table(
        "hospital_lab_results",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("patient_id", sa.String(50), nullable=False),
        sa.Column("encounter_id", sa.String(50)),
        sa.Column("test_name", sa.String(200)),
        sa.Column("test_category", sa.String(100)),
        sa.Column("result_value", sa.String(200)),
        sa.Column("result_unit", sa.String(50)),
        sa.Column("reference_range", sa.String(100)),
        sa.Column("is_abnormal", sa.Integer(), server_default="0"),
        sa.Column("performed_at", sa.DateTime(timezone=True)),
        sa.Column("turnaround_hours", sa.Float()),
    )
    op.create_index("ix_hospital_lab_results_patient", "hospital_lab_results", ["patient_id"])
    op.create_table(
        "hospital_imaging_studies",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("patient_id", sa.String(50), nullable=False),
        sa.Column("study_type", sa.String(100)),
        sa.Column("body_site", sa.String(100)),
        sa.Column("status", sa.String(30)),
        sa.Column("ordered_at", sa.DateTime(timezone=True)),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("turnaround_hours", sa.Float()),
    )
    op.create_index("ix_hospital_imaging_patient", "hospital_imaging_studies", ["patient_id"])
    op.create_table(
        "hospital_procedures",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("patient_id", sa.String(50), nullable=False),
        sa.Column("procedure_type", sa.String(200)),
        sa.Column("department_id", sa.String(50)),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("status", sa.String(30)),
    )
    op.create_index("ix_hospital_procedures_patient", "hospital_procedures", ["patient_id"])
    op.create_table(
        "hospital_staff",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("department_id", sa.String(50)),
        sa.Column("name", sa.String(200)),
        sa.Column("role", sa.String(100)),
        sa.Column("active", sa.Boolean(), server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "hospital_shifts",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("staff_id", sa.String(50), nullable=False),
        sa.Column("department_id", sa.String(50)),
        sa.Column("start", sa.DateTime(timezone=True)),
        sa.Column("end", sa.DateTime(timezone=True)),
        sa.Column("shift_type", sa.String(30)),
    )
    op.create_index("ix_hospital_shifts_staff", "hospital_shifts", ["staff_id"])
    op.create_table(
        "hospital_equipment",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("department_id", sa.String(50)),
        sa.Column("equipment_type", sa.String(100)),
        sa.Column("status", sa.String(30)),
        sa.Column("last_maintenance", sa.DateTime(timezone=True)),
        sa.Column("next_maintenance", sa.DateTime(timezone=True)),
    )
    op.create_table(
        "hospital_operating_rooms",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("department_id", sa.String(50)),
        sa.Column("name", sa.String(100)),
        sa.Column("status", sa.String(30)),
        sa.Column("current_procedure_id", sa.String(50)),
        sa.Column("scheduled_start", sa.DateTime(timezone=True)),
        sa.Column("scheduled_end", sa.DateTime(timezone=True)),
    )
    op.create_table(
        "hospital_emergency_visits",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("patient_id", sa.String(50), nullable=False),
        sa.Column("acuity", sa.Integer()),
        sa.Column("chief_complaint", sa.String(300)),
        sa.Column("arrival_time", sa.DateTime(timezone=True)),
        sa.Column("triage_time", sa.DateTime(timezone=True)),
        sa.Column("seen_by_doctor", sa.DateTime(timezone=True)),
        sa.Column("disposition", sa.String(50)),
        sa.Column("disposition_time", sa.DateTime(timezone=True)),
        sa.Column("wait_time_minutes", sa.Integer()),
    )
    op.create_index("ix_hospital_emergency_patient", "hospital_emergency_visits", ["patient_id"])
    op.create_table(
        "hospital_appointments",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("patient_id", sa.String(50), nullable=False),
        sa.Column("department_id", sa.String(50)),
        sa.Column("scheduled_at", sa.DateTime(timezone=True)),
        sa.Column("status", sa.String(30)),
        sa.Column("reason", sa.String(300)),
    )
    op.create_index("ix_hospital_appointments_patient", "hospital_appointments", ["patient_id"])
    op.create_table(
        "hospital_medicine_inventory",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("department_id", sa.String(50)),
        sa.Column("medicine_name", sa.String(200)),
        sa.Column("stock_current", sa.Float()),
        sa.Column("stock_max", sa.Float()),
        sa.Column("consumption_rate", sa.Float()),
        sa.Column("days_until_stockout", sa.Float()),
        sa.Column("unit", sa.String(20), server_default="units"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # === Community Workspace ===
    op.create_table(
        "community_countries",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("code", sa.String(10)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "community_provinces",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("country_id", sa.String(50), sa.ForeignKey("community_countries.id"), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("code", sa.String(10)),
    )
    op.create_table(
        "community_counties",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("province_id", sa.String(50), sa.ForeignKey("community_provinces.id"), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("code", sa.String(10)),
    )
    op.create_table(
        "community_districts",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("county_id", sa.String(50), sa.ForeignKey("community_counties.id"), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("code", sa.String(10)),
        sa.Column("population", sa.Integer(), server_default="0"),
    )
    op.create_table(
        "community_sub_districts",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("district_id", sa.String(50), sa.ForeignKey("community_districts.id"), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
    )
    op.create_table(
        "community_communities",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("district_id", sa.String(50)),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("population", sa.Integer(), server_default="0"),
    )
    op.create_table(
        "community_health_facilities",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("district_id", sa.String(50), sa.ForeignKey("community_districts.id"), nullable=False),
        sa.Column("name", sa.String(300), nullable=False),
        sa.Column("type", sa.String(50)),
        sa.Column("latitude", sa.Float()),
        sa.Column("longitude", sa.Float()),
        sa.Column("active", sa.Boolean(), server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "community_health_programs",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("name", sa.String(300), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("status", sa.String(30)),
        sa.Column("budget", sa.Float(), server_default="0"),
        sa.Column("coverage_pct", sa.Float(), server_default="0"),
        sa.Column("start_date", sa.DateTime(timezone=True)),
        sa.Column("end_date", sa.DateTime(timezone=True)),
    )
    op.create_table(
        "community_health_workers",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("district_id", sa.String(50)),
        sa.Column("facility_id", sa.String(50)),
        sa.Column("role", sa.String(100)),
        sa.Column("active", sa.Boolean(), server_default="true"),
    )
    op.create_table(
        "community_diseases",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("code", sa.String(50)),
        sa.Column("category", sa.String(100)),
    )
    op.create_table(
        "community_disease_cases",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("disease_id", sa.String(50), nullable=False),
        sa.Column("district_id", sa.String(50), nullable=False),
        sa.Column("confirmed", sa.Integer(), server_default="0"),
        sa.Column("suspected", sa.Integer(), server_default="0"),
        sa.Column("deaths", sa.Integer(), server_default="0"),
        sa.Column("recovered", sa.Integer(), server_default="0"),
        sa.Column("reporting_week", sa.String(10)),
        sa.Column("reported_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_community_cases_disease", "community_disease_cases", ["disease_id"])
    op.create_index("ix_community_cases_district", "community_disease_cases", ["district_id"])
    op.create_table(
        "community_outbreaks",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("disease_id", sa.String(50), nullable=False),
        sa.Column("district_id", sa.String(50), nullable=False),
        sa.Column("status", sa.String(30)),
        sa.Column("cases", sa.Integer(), server_default="0"),
        sa.Column("risk_level", sa.String(20)),
        sa.Column("detected_at", sa.DateTime(timezone=True)),
        sa.Column("contained_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_community_outbreaks_disease", "community_outbreaks", ["disease_id"])
    op.create_index("ix_community_outbreaks_district", "community_outbreaks", ["district_id"])
    op.create_table(
        "community_surveillance_events",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("district_id", sa.String(50), nullable=False),
        sa.Column("event_type", sa.String(50)),
        sa.Column("reported_at", sa.DateTime(timezone=True)),
        sa.Column("complete", sa.Boolean(), server_default="false"),
    )
    op.create_index("ix_community_surveillance_district", "community_surveillance_events", ["district_id"])
    op.create_table(
        "community_indicators",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("name", sa.String(300), nullable=False),
        sa.Column("value", sa.Float()),
        sa.Column("target", sa.Float()),
        sa.Column("district_id", sa.String(50)),
        sa.Column("period", sa.String(20)),
        sa.Column("recorded_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "community_vaccination_campaigns",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("vaccine", sa.String(200)),
        sa.Column("district_id", sa.String(50)),
        sa.Column("doses_target", sa.Integer(), server_default="0"),
        sa.Column("doses_administered", sa.Integer(), server_default="0"),
        sa.Column("coverage_pct", sa.Float(), server_default="0"),
        sa.Column("start_date", sa.DateTime(timezone=True)),
        sa.Column("end_date", sa.DateTime(timezone=True)),
        sa.Column("status", sa.String(30)),
    )
    op.create_table(
        "community_medicine_stock",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("district_id", sa.String(50)),
        sa.Column("medicine", sa.String(200)),
        sa.Column("stock_on_hand", sa.Integer(), server_default="0"),
        sa.Column("monthly_consumption", sa.Integer(), server_default="0"),
        sa.Column("days_of_stock", sa.Float(), server_default="0"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "community_supply_chain_events",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("district_id", sa.String(50)),
        sa.Column("medicine", sa.String(200)),
        sa.Column("quantity", sa.Integer()),
        sa.Column("event_type", sa.String(30)),
        sa.Column("event_date", sa.DateTime(timezone=True)),
        sa.Column("status", sa.String(30)),
    )
    op.create_table(
        "community_maternal_health",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("district_id", sa.String(50)),
        sa.Column("anc_visits", sa.Integer(), server_default="0"),
        sa.Column("facility_deliveries", sa.Integer(), server_default="0"),
        sa.Column("maternal_deaths", sa.Integer(), server_default="0"),
        sa.Column("period", sa.String(20)),
        sa.Column("recorded_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "community_child_health",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("district_id", sa.String(50)),
        sa.Column("under_five_population", sa.Integer(), server_default="0"),
        sa.Column("immunized", sa.Integer(), server_default="0"),
        sa.Column("malnourished", sa.Integer(), server_default="0"),
        sa.Column("under_five_deaths", sa.Integer(), server_default="0"),
        sa.Column("period", sa.String(20)),
        sa.Column("recorded_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "community_nutrition",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("district_id", sa.String(50)),
        sa.Column("children_screened", sa.Integer(), server_default="0"),
        sa.Column("severely_malnourished", sa.Integer(), server_default="0"),
        sa.Column("moderately_malnourished", sa.Integer(), server_default="0"),
        sa.Column("receiving_supplements", sa.Integer(), server_default="0"),
        sa.Column("period", sa.String(20)),
        sa.Column("recorded_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "community_laboratories",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("district_id", sa.String(50)),
        sa.Column("name", sa.String(200)),
        sa.Column("type", sa.String(50)),
        sa.Column("active", sa.Boolean(), server_default="true"),
        sa.Column("tests_per_month", sa.Integer(), server_default="0"),
        sa.Column("reporting_complete", sa.Boolean(), server_default="true"),
    )
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.String(100)),
        sa.Column("action", sa.String(50)),
        sa.Column("resource", sa.String(100)),
        sa.Column("resource_id", sa.String(100)),
        sa.Column("details", sa.JSON()),
        sa.Column("result", sa.String(20), server_default="success"),
        sa.Column("ip_address", sa.String(50)),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_audit_logs_user", "audit_logs", ["user_id"])


def downgrade() -> None:
    op.drop_table("hospital_medicine_inventory")
    op.drop_table("hospital_appointments")
    op.drop_table("hospital_emergency_visits")
    op.drop_table("hospital_operating_rooms")
    op.drop_table("hospital_equipment")
    op.drop_table("hospital_shifts")
    op.drop_table("hospital_staff")
    op.drop_table("hospital_procedures")
    op.drop_table("hospital_imaging_studies")
    op.drop_table("hospital_lab_results")
    op.drop_table("hospital_medications")
    op.drop_table("hospital_observations")
    op.drop_table("hospital_admissions")
    op.drop_table("hospital_encounters")
    op.drop_table("hospital_patients")
    op.drop_table("hospital_beds")
    op.drop_table("hospital_wards")
    op.drop_table("hospital_departments")
    op.drop_table("hospital_buildings")
    op.drop_table("hospital_campuses")
    op.drop_table("hospital_hospitals")
    op.drop_table("community_laboratories")
    op.drop_table("community_nutrition")
    op.drop_table("community_child_health")
    op.drop_table("community_maternal_health")
    op.drop_table("community_supply_chain_events")
    op.drop_table("community_medicine_stock")
    op.drop_table("community_vaccination_campaigns")
    op.drop_table("community_indicators")
    op.drop_table("community_surveillance_events")
    op.drop_table("community_outbreaks")
    op.drop_table("community_disease_cases")
    op.drop_table("community_diseases")
    op.drop_table("community_health_workers")
    op.drop_table("community_health_programs")
    op.drop_table("community_health_facilities")
    op.drop_table("community_communities")
    op.drop_table("community_sub_districts")
    op.drop_table("community_districts")
    op.drop_table("community_counties")
    op.drop_table("community_provinces")
    op.drop_table("community_countries")
    op.drop_table("audit_logs")

"""Seed canonical database from fixture SQL file.

Usage:
    python seed.py              # loads fixtures/seed_data.sql
    python seed.py --check      # check if data already exists
    python seed.py --clear      # truncate all canonical tables first

This replaces bootstrap_canonical_data() which previously ran the
ImportManager with demo connectors. The fixture was exported from
one final run of the demo generators.
"""
import os
import sys

from core.database import engine, SessionLocal
from core.logging import logger
from sqlalchemy import text

FIXTURE_PATH = os.path.join(os.path.dirname(__file__), "fixtures", "seed_data.sql")

CANONICAL_TABLES = [
    "hospital_hospitals", "hospital_campuses", "hospital_buildings",
    "hospital_departments", "hospital_wards", "hospital_beds",
    "hospital_patients", "hospital_encounters", "hospital_admissions",
    "hospital_observations", "hospital_medications", "hospital_lab_results",
    "hospital_imaging_studies", "hospital_procedures", "hospital_staff",
    "hospital_shifts", "hospital_equipment", "hospital_operating_rooms",
    "hospital_emergency_visits", "hospital_appointments",
    "hospital_medicine_inventory",
    "community_countries", "community_provinces", "community_counties",
    "community_districts", "community_sub_districts", "community_communities",
    "community_health_facilities", "community_health_programs",
    "community_health_workers", "community_diseases", "community_disease_cases",
    "community_outbreaks", "community_surveillance_events",
    "community_indicators", "community_vaccination_campaigns",
    "community_medicine_stock", "community_supply_chain_events",
    "community_maternal_health", "community_child_health",
    "community_nutrition", "community_laboratories",
]


def is_seeded() -> bool:
    db = SessionLocal()
    try:
        n = db.execute(text("SELECT count(*) FROM hospital_hospitals")).scalar()
        return n > 0
    finally:
        db.close()


def clear():
    db = SessionLocal()
    try:
        for t in CANONICAL_TABLES:
            db.execute(text(f"TRUNCATE TABLE {t} RESTART IDENTITY CASCADE"))
        db.execute(text("TRUNCATE TABLE import_jobs RESTART IDENTITY CASCADE"))
        db.execute(text("TRUNCATE TABLE import_batches RESTART IDENTITY CASCADE"))
        db.commit()
        logger.info(f"Cleared {len(CANONICAL_TABLES)} canonical tables")
    finally:
        db.close()


def seed():
    if not os.path.exists(FIXTURE_PATH):
        logger.error(f"Seed file not found: {FIXTURE_PATH}")
        sys.exit(1)

    with open(FIXTURE_PATH, "r", encoding="utf-8") as f:
        sql = f.read()

    conn = engine.raw_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()
        logger.info("Seed data loaded successfully")
    except Exception as e:
        conn.rollback()
        logger.error(f"Seed failed: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    if "--check" in sys.argv:
        print("seeded" if is_seeded() else "empty")
    elif "--clear" in sys.argv:
        clear()
    else:
        if is_seeded():
            logger.info("Database already seeded — skipping")
        else:
            seed()

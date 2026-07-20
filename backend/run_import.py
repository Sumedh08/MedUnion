"""Clear seed data and run live imports from FHIR + DHIS2."""
import sys
sys.path.insert(0, ".")

from core.database import SessionLocal
from seed import clear, is_seeded
from connectors import init_connectors, connector_registry
from services.import_manager import ImportManager
from sqlalchemy import text

# Step 1: Init connectors
print("=== Step 0: Init connectors ===")
init_connectors()
for name, c in connector_registry._connectors.items():
    print(f"  {name}: connected={c.is_connected}")

# Step 2: Clear seed data
print()
print("=== Step 1: Clearing seed data ===")
if is_seeded():
    clear()
    print("  Seed data cleared")
else:
    print("  No seed data found")

# Step 3: Run FHIR import (hospital workspace)
print()
print("=== Step 2: FHIR Import (hospital) ===")
db = SessionLocal()
try:
    mgr = ImportManager(db)
    results = mgr.run_import("hospital")
    for r in results:
        status = "OK" if r.success else "FAIL"
        print(f"  {r.resource}: {r.records_processed} inserted, {r.records_failed} failed [{status}]")
        if r.errors:
            for e in r.errors[:3]:
                print(f"    error: {e}")
except Exception as e:
    print(f"  Hospital import failed: {type(e).__name__}: {e}")
finally:
    db.close()

# Step 4: Run DHIS2 import (community workspace)
print()
print("=== Step 3: DHIS2 Import (community) ===")
db = SessionLocal()
try:
    mgr = ImportManager(db)
    results = mgr.run_import("community")
    for r in results:
        status = "OK" if r.success else "FAIL"
        print(f"  {r.resource}: {r.records_processed} inserted, {r.records_failed} failed [{status}]")
        if r.errors:
            for e in r.errors[:3]:
                print(f"    error: {e}")
except Exception as e:
    print(f"  Community import failed: {type(e).__name__}: {e}")
finally:
    db.close()

# Step 5: Verify
print()
print("=== Verification ===")
db = SessionLocal()
try:
    tables = [
        ("hospitals", "hospital_hospitals"),
        ("patients", "hospital_patients"),
        ("admissions", "hospital_admissions"),
        ("staff", "hospital_staff"),
        ("medicine", "hospital_medicine_inventory"),
        ("equipment", "hospital_equipment"),
        ("departments", "hospital_departments"),
        ("wards", "hospital_wards"),
        ("beds", "hospital_beds"),
        ("districts", "community_districts"),
        ("facilities", "community_health_facilities"),
        ("indicators", "community_indicators"),
        ("disease_cases", "community_disease_cases"),
        ("vaccinations", "community_vaccination_campaigns"),
        ("surveillance", "community_surveillance_events"),
    ]
    for label, table in tables:
        n = db.execute(text(f"SELECT count(*) FROM {table}")).scalar()
        print(f"  {label} ({table}): {n}")
finally:
    db.close()

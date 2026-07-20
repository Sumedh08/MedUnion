from datetime import date
from typing import Optional

from etl.mappers.base import BaseCanonicalMapper


def _is_fhir(records: list[dict]) -> bool:
    """Detect FHIR-shaped data by checking for resourceType field."""
    return bool(records and "resourceType" in records[0])


def _fhir_name(r: dict) -> Optional[str]:
    """Extract best-effort human name from a FHIR resource."""
    names = r.get("name") or []
    if names and isinstance(names, list):
        human = names[0]
        parts = []
        if isinstance(human, dict):
            for k in ("prefix", "given", "family"):
                val = human.get(k, "")
                if isinstance(val, list):
                    val = " ".join(str(v) for v in val if v)
                if val:
                    parts.append(str(val))
        name_str = " ".join(parts)
        if name_str.strip():
            return name_str.strip()
    if isinstance(names, dict):
        parts = []
        for k in ("prefix", "given", "family"):
            val = names.get(k, "")
            if isinstance(val, list):
                val = " ".join(str(v) for v in val if v)
            if val:
                parts.append(str(val))
        name_str = " ".join(parts)
        if name_str.strip():
            return name_str.strip()
    return None


def _fhir_reference_id(ref: Optional[str]) -> Optional[str]:
    """Extract an id from a FHIR reference string like 'Patient/123'."""
    if not ref:
        return None
    return ref.split("/")[-1] if "/" in ref else ref


def _fhir_coding_first(r: dict, *keys: str) -> Optional[str]:
    """Drill into a FHIR codeable concept to get the first code."""
    obj = r
    for k in keys:
        obj = obj.get(k) or {}
        if isinstance(obj, list):
            obj = obj[0] if obj else {}
    return obj if isinstance(obj, str) else None


def _fhir_org_type(r: dict) -> str:
    types = r.get("type") or []
    if types and isinstance(types, list):
        coding = (types[0].get("coding") or [{}])[0]
        return coding.get("code") or coding.get("display") or "unknown"
    return "unknown"


class HospitalCanonicalMapper(BaseCanonicalMapper):
    """Maps hospital connector records to canonical domain dicts.

    Auto-detects FHIR data (records with resourceType) vs demo/near-canonical.
    """

    def _map_hospitals(self, records: list[dict]) -> list[dict]:
        if not _is_fhir(records):
            return records
        return self._map_Organization(records)

    def _map_patients(self, records: list[dict]) -> list[dict]:
        if not _is_fhir(records):
            out = []
            for r in records:
                item = dict(r)
                if "hospital_id" not in item and "department_id" in item:
                    item.pop("department_id", None)
                out.append(item)
            return out
        return self._map_Patient(records)

    def _map_admissions(self, records: list[dict]) -> list[dict]:
        """FHIR Encounter → canonical admission. Pass-through for demo data."""
        if not _is_fhir(records):
            return records
        out = []
        for r in records:
            period = r.get("period") or {}
            admitted = period.get("start") if isinstance(period, dict) else None
            discharged = period.get("end") if isinstance(period, dict) else None
            los = None
            if admitted and discharged:
                try:
                    from datetime import datetime
                    a = datetime.fromisoformat(admitted.replace("Z", "+00:00"))
                    d = datetime.fromisoformat(discharged.replace("Z", "+00:00"))
                    los = (d - a).total_seconds() / 86400
                except Exception:
                    pass

            subject_ref = (r.get("subject") or {}).get("reference")
            patient_id = _fhir_reference_id(subject_ref) if subject_ref else None

            diagnosis = None
            diag_list = r.get("diagnosis") or []
            if diag_list and isinstance(diag_list, list):
                cond = diag_list[0]
                cond_ref = (cond.get("condition") or {}).get("reference")
                if cond_ref:
                    diagnosis = cond_ref

            class_info = r.get("class") or {}
            department_id = class_info.get("code") if isinstance(class_info, dict) else None

            out.append({
                "id": r.get("id", ""),
                "patient_id": patient_id or "unknown",
                "department_id": department_id,
                "admitted_at": admitted,
                "discharged_at": discharged,
                "length_of_stay_days": los,
                "diagnosis": diagnosis,
                "outcome": r.get("status"),
                "source_record_id": r.get("id"),
            })
        return out

    def _map_staff(self, records: list[dict]) -> list[dict]:
        """FHIR Practitioner → canonical staff. Pass-through for demo data."""
        if not _is_fhir(records):
            return records
        out = []
        for r in records:
            name_str = _fhir_name(r)
            role = None
            quals = r.get("qualification") or []
            if quals and isinstance(quals, list):
                role = _fhir_coding_first(quals[0], "code", "coding", 0, "display")
            out.append({
                "id": r.get("id", ""),
                "name": name_str or "Unknown",
                "role": role,
                "active": r.get("active", True) if r.get("active") is not None else True,
                "source_record_id": r.get("id"),
            })
        return out

    def _map_medicine_inventory(self, records: list[dict]) -> list[dict]:
        """FHIR MedicationRequest → canonical medicine inventory. Pass-through for demo."""
        if not _is_fhir(records):
            return records
        out = []
        for r in records:
            med_concept = r.get("medicationCodeableConcept") or {}
            med_name = _fhir_coding_first(med_concept, "coding", 0, "display") or med_concept.get("text")
            subject_ref = (r.get("subject") or {}).get("reference")

            out.append({
                "id": r.get("id", ""),
                "medicine_name": med_name or "Unknown",
                "stock_current": None,
                "stock_max": None,
                "consumption_rate": None,
                "days_until_stockout": None,
                "unit": "units",
                "source_record_id": r.get("id"),
            })
        return out

    def _map_equipment(self, records: list[dict]) -> list[dict]:
        if not _is_fhir(records):
            out = []
            for r in records:
                item = dict(r)
                if "equipment_type" not in item and "type" in item:
                    item["equipment_type"] = item.pop("type")
                out.append(item)
            return out
        # FHIR Device → equipment
        out = []
        for r in records:
            raw_type = r.get("type")
            if isinstance(raw_type, list):
                raw_type = raw_type[0] if raw_type else {}
            eq_type = None
            if isinstance(raw_type, dict):
                eq_type = _fhir_coding_first(raw_type, "coding", 0, "display") or raw_type.get("text")
            elif isinstance(raw_type, str):
                eq_type = raw_type
            out.append({
                "id": r.get("id", ""),
                "equipment_type": eq_type or "Unknown",
                "status": r.get("status"),
                "source_record_id": r.get("id"),
            })
        return out

    def _map_Patient(self, records: list[dict]) -> list[dict]:
        """FHIR Patient → canonical patient."""
        out = []
        for r in records:
            gender = r.get("gender")
            birth = r.get("birthDate")
            age = None
            if birth:
                try:
                    y = int(str(birth)[:4])
                    age = max(0, date.today().year - y)
                except (ValueError, TypeError):
                    age = None
            out.append({
                "id": r.get("id") or r.get("resourceType", "Patient") + "-" + str(hash(str(r)))[:8],
                "age": age,
                "gender": gender,
                "hospital_id": None,
                "source_record_id": r.get("id"),
            })
        return out

    def _map_Organization(self, records: list[dict]) -> list[dict]:
        """FHIR Organization → canonical hospital."""
        out = []
        for r in records:
            out.append({
                "id": r.get("id", ""),
                "name": (r.get("name") or "Unknown"),
                "type": _fhir_org_type(r),
                "campus_count": 1,
                "total_beds": 0,
                "active": r.get("active", True),
                "source_record_id": r.get("id"),
            })
        return out


    def _map_departments(self, records: list[dict]) -> list[dict]:
        """No direct FHIR equivalent for departments. Return empty for FHIR data."""
        if _is_fhir(records):
            return []
        return records

    def _map_wards(self, records: list[dict]) -> list[dict]:
        if _is_fhir(records):
            out = []
            for r in records:
                out.append({
                    "id": r.get("id", ""),
                    "name": r.get("name") or r.get("description") or "Unknown",
                    "department_id": None,
                    "ward_type": _fhir_coding_first(r, "type", "coding", 0, "display") or r.get("type"),
                    "capacity": 0,
                    "source_record_id": r.get("id"),
                })
            return out
        return records

    def _map_beds(self, records: list[dict]) -> list[dict]:
        """No direct FHIR equivalent for beds. Return empty for FHIR data."""
        if _is_fhir(records):
            return []
        return records


hospital_mapper = HospitalCanonicalMapper()

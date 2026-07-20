from typing import Optional

from etl.mappers.base import BaseCanonicalMapper


def _is_dhis2(records: list[dict]) -> bool:
    """Detect DHIS2-shaped data by checking for DHIS2-specific fields."""
    if not records:
        return False
    r = records[0]
    return bool("organisationUnitGroups" in r or "level" in r or "shortName" in r or "indicatorType" in r)


def _is_analytics(records: list[dict]) -> bool:
    """Detect DHIS2 analytics response shape."""
    if not records:
        return False
    return "headers" in records[0] or "rows" in records[0] or "metaData" in records[0]


class CommunityCanonicalMapper(BaseCanonicalMapper):
    """Maps community connector records to canonical domain dicts.

    Auto-detects DHIS2 data (organisationUnitGroups, level, etc.)
    vs demo/near-canonical data.
    """

    def _map_districts(self, records: list[dict]) -> list[dict]:
        if not _is_dhis2(records):
            out = []
            for r in records:
                item = dict(r)
                item.pop("province_id", None)
                item.pop("district_count", None)
                item.pop("facility_count", None)
                if "population" not in item:
                    item["population"] = 0
                out.append(item)
            return out
        return self._map_organisationUnits(records)

    def _map_facilities(self, records: list[dict]) -> list[dict]:
        """DHIS2 organisationUnits at facility level, or demo pass-through."""
        if not _is_dhis2(records):
            return records
        out = []
        for r in records:
            parent = r.get("parent")
            if not parent or not isinstance(parent, dict) or not parent.get("id"):
                continue
            name = r.get("name") or r.get("displayName") or "Unknown"
            out.append({
                "id": r.get("id", ""),
                "district_id": parent["id"],
                "name": name,
                "type": _dhis2_orgunit_type(r),
                "latitude": None,
                "longitude": None,
                "active": True,
                "source_record_id": r.get("id"),
            })
        return out

    def _map_disease_reports(self, records: list[dict]) -> list[dict]:
        if _is_analytics(records):
            return self._map_analytics_disease(records)
        out = []
        for r in records:
            item = dict(r)
            if not item.get("disease_id") and item.get("disease"):
                item["disease_id"] = str(item["disease"])[:50]
            item.pop("disease", None)
            out.append(item)
        return out

    def _map_outbreaks(self, records: list[dict]) -> list[dict]:
        out = []
        for r in records:
            item = dict(r)
            if not item.get("disease_id") and item.get("disease"):
                item["disease_id"] = str(item["disease"])[:50]
            item.pop("disease", None)
            out.append(item)
        return out

    def _map_vaccinations(self, records: list[dict]) -> list[dict]:
        if _is_dhis2(records):
            return self._map_programs_vaccinations(records)
        out = []
        for r in records:
            item = dict(r)
            if "doses_administered" not in item and "doses" in item:
                item["doses_administered"] = item.pop("doses")
            if "doses_target" not in item:
                cov = float(item.get("coverage_pct") or 0)
                admin = int(item.get("doses_administered") or 0)
                item["doses_target"] = int(admin / (cov / 100)) if cov > 0 else admin
            if "status" not in item:
                item["status"] = "active"
            item.pop("recorded_at", None)
            out.append(item)
        return out

    def _map_indicators(self, records: list[dict]) -> list[dict]:
        """DHIS2 indicators → canonical indicators, or demo pass-through."""
        if _is_dhis2(records):
            out = []
            for r in records:
                out.append({
                    "id": r.get("id", ""),
                    "name": r.get("name") or r.get("displayName") or "Unknown",
                    "value": r.get("value"),
                    "target": None,
                    "district_id": None,
                    "period": r.get("period"),
                    "source_record_id": r.get("id"),
                })
            return out
        return records

    def _map_analytics_disease(self, records: list[dict]) -> list[dict]:
        """Convert DHIS2 analytics response rows to disease report format."""
        out = []
        for resp in records:
            headers = resp.get("headers", [])
            rows = resp.get("rows", [])
            cols = [h.get("name", f"col{i}") for i, h in enumerate(headers)]
            for row in rows:
                rec = dict(zip(cols, row))
                out.append({
                    "id": f"analytics-{rec.get('ou', 'unknown')}-{rec.get('pe', 'unknown')}",
                    "district_id": rec.get("ou"),
                    "disease_id": rec.get("dx"),
                    "confirmed": _int_or(rec.get("value"), 0),
                    "suspected": 0,
                    "deaths": 0,
                    "recovered": 0,
                    "reporting_week": rec.get("pe"),
                    "source_record_id": f"analytics/{rec.get('ou')}/{rec.get('pe')}",
                })
        return out

    def _map_programs_vaccinations(self, records: list[dict]) -> list[dict]:
        """DHIS2 programs → vaccination campaigns."""
        out = []
        for r in records:
            out.append({
                "id": r.get("id", ""),
                "vaccine": r.get("name") or r.get("displayName") or "Unknown",
                "district_id": None,
                "doses_target": 0,
                "doses_administered": 0,
                "coverage_pct": 0,
                "start_date": None,
                "end_date": None,
                "status": "active",
                "source_record_id": r.get("id"),
            })
        return out

    def _map_organisationUnits(self, records: list[dict]) -> list[dict]:
        """DHIS2 organisationUnits → districts."""
        out = []
        for r in records:
            out.append({
                "id": r.get("id", ""),
                "name": r.get("name") or r.get("displayName") or "Unknown",
                "code": r.get("code"),
                "county_id": None,
                "population": 0,
                "source_record_id": r.get("id"),
            })
        return out

    def _map_surveillance_events(self, records: list[dict]) -> list[dict]:
        """DHIS2 events → surveillance events, or demo pass-through."""
        if _is_dhis2(records):
            out = []
            for r in records:
                out.append({
                    "id": r.get("event") or r.get("id", ""),
                    "district_id": r.get("orgUnit") or "unknown",
                    "event_type": r.get("program"),
                    "reported_at": r.get("eventDate") or r.get("created"),
                    "complete": r.get("status") == "COMPLETED",
                    "source_record_id": r.get("event") or r.get("id"),
                })
            return out
        return records


def _dhis2_orgunit_type(r: dict) -> Optional[str]:
    groups = r.get("organisationUnitGroups") or []
    if groups and isinstance(groups, list):
        first = groups[0]
        name = first.get("name") or first.get("displayName") if isinstance(first, dict) else None
        if name:
            return name.replace("Organisation Unit ", "").lower()
    return None


def _int_or(val, default=0):
    if val is None:
        return default
    try:
        return int(val)
    except (ValueError, TypeError):
        return default


community_mapper = CommunityCanonicalMapper()

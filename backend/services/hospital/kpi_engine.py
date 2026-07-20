from datetime import datetime, timedelta


class HospitalKPIEngine:
    def __init__(self, connector):
        self._connector = connector

    def get_hospitals_enriched(self):
        hospitals = self._connector.fetch("hospitals")
        departments = self._connector.fetch("departments")
        wards = self._connector.fetch("wards")
        beds = self._connector.fetch("beds")
        staff = self._connector.fetch("staff")
        admissions = self._connector.fetch("admissions")
        equipment = self._connector.fetch("equipment")

        dept_to_hosp = {d["id"]: d["hospital_id"] for d in departments}
        ward_to_dept = {w["id"]: w["department_id"] for w in wards}
        hosp_departments = {}
        for d in departments:
            hid = d["hospital_id"]
            hosp_departments.setdefault(hid, []).append(d)

        hosp_staff = {}
        for s in staff:
            hid = dept_to_hosp.get(s.get("department_id", ""), "")
            hosp_staff.setdefault(hid, []).append(s)

        hosp_admissions = {}
        for a in admissions:
            hid = dept_to_hosp.get(a.get("department_id", ""), "")
            hosp_admissions.setdefault(hid, []).append(a)

        bed_summary = self._bed_summary_by_hospital(beds, wards, dept_to_hosp)

        equipment_by_hosp = {}
        for e in equipment:
            hid = dept_to_hosp.get(e.get("department_id", ""), "")
            equipment_by_hosp.setdefault(hid, []).append(e)

        results = []
        for h in hospitals:
            hid = h["id"]
            bs = bed_summary.get(hid, {"total": 0, "occupied": 0, "available": 0})
            h_staff = hosp_staff.get(hid, [])
            h_adm = hosp_admissions.get(hid, [])
            h_eq = equipment_by_hosp.get(hid, [])
            results.append(self._enrich(h, bs, h_staff, h_adm, h_eq, hosp_departments.get(hid, [])))
        return results

    def get_hospital_detail(self, hospital_id):
        enriched = self.get_hospitals_enriched()
        for h in enriched:
            if h["id"] == hospital_id:
                return h
        return None

    def compute_kpis(self, hospital_id=None):
        enriched = self.get_hospitals_enriched()
        if hospital_id:
            enriched = [h for h in enriched if h["id"] == hospital_id]
        return [self._build_kpis(h) for h in enriched]

    def _bed_summary_by_hospital(self, beds, wards, dept_to_hosp):
        ward_to_hosp = {}
        for w in wards:
            did = w.get("department_id", "")
            ward_to_hosp[w["id"]] = dept_to_hosp.get(did, "")

        summary = {}
        for bed in beds:
            wid = bed.get("ward_id", "")
            hid = ward_to_hosp.get(wid, "")
            if not hid:
                continue
            s = summary.setdefault(hid, {"total": 0, "occupied": 0, "available": 0, "maintenance": 0, "reserved": 0})
            s["total"] += 1
            status = bed.get("status", "available")
            if status in s:
                s[status] += 1
            else:
                s["available"] += 1
        return summary

    def _enrich(self, h, bed_summary, staff, admissions, equipment, departments):
        total_beds = bed_summary["total"]
        occupied = bed_summary["occupied"]
        icu_depts = [d for d in departments if "ICU" in d.get("name", "").upper()]
        icu_beds = 0
        icu_occupied = 0

        active_staff = [s for s in staff if s.get("active", False)]
        recent_adm = [a for a in admissions if a.get("admitted_at", "") > (datetime.now() - timedelta(days=30)).isoformat()]
        op_eq = [e for e in equipment if e.get("status") == "operational"]

        return {
            **h,
            "total_beds": total_beds,
            "occupied_beds": occupied,
            "available_beds": bed_summary.get("available", 0),
            "bed_occupancy_pct": round((occupied / total_beds * 100) if total_beds else 0, 1),
            "icu_beds": icu_beds,
            "icu_occupied": icu_occupied,
            "icu_occupancy_pct": 0.0,
            "staff_count": len(staff),
            "active_staff_count": len(active_staff),
            "admissions_30d": len(recent_adm),
            "equipment_count": len(equipment),
            "operational_equipment": len(op_eq),
            "department_count": len(departments),
        }

    def _build_kpis(self, h):
        return {
            "hospital_id": h["id"],
            "hospital_name": h["name"],
            "bed_occupancy": {
                "value": h["bed_occupancy_pct"],
                "unit": "%",
                "benchmark": 85.0,
                "status": "critical" if h["bed_occupancy_pct"] >= 90 else "warning" if h["bed_occupancy_pct"] >= 80 else "normal",
            },
            "icu_occupancy": {
                "value": h.get("icu_occupancy_pct", 0),
                "unit": "%",
                "benchmark": 75.0,
                "status": "normal",
            },
            "staff_count": {
                "value": h.get("active_staff_count", 0),
                "unit": "count",
                "benchmark": None,
                "status": "normal",
            },
            "admissions_30d": {
                "value": h.get("admissions_30d", 0),
                "unit": "count",
                "benchmark": None,
                "status": "normal",
            },
            "equipment_uptime": {
                "value": round((h.get("operational_equipment", 0) / h.get("equipment_count", 1)) * 100, 1) if h.get("equipment_count") else 0,
                "unit": "%",
                "benchmark": 95.0,
                "status": "normal",
            },
        }

    def get_kpi_summary(self):
        kpis = self.compute_kpis()
        if not kpis:
            return {}
        avg_occupancy = sum(k["bed_occupancy"]["value"] for k in kpis) / len(kpis)
        critical = [k for k in kpis if k["bed_occupancy"]["status"] == "critical"]
        warning = [k for k in kpis if k["bed_occupancy"]["status"] == "warning"]
        return {
            "hospitals_count": len(kpis),
            "avg_bed_occupancy": round(avg_occupancy, 1),
            "critical_hospitals": len(critical),
            "warning_hospitals": len(warning),
            "normal_hospitals": len(kpis) - len(critical) - len(warning),
            "critical_hospital_names": [k["hospital_name"] for k in critical],
            "total_staff": sum(k["staff_count"]["value"] for k in kpis),
            "total_admissions_30d": sum(k["admissions_30d"]["value"] for k in kpis),
        }

    def get_admissions_trend(self, hospital_id=None, days=30):
        admissions = self._connector.fetch("admissions")
        if hospital_id:
            departments = self._connector.fetch("departments")
            wards = self._connector.fetch("wards")
            dept_to_hosp = {d["id"]: d["hospital_id"] for d in departments}
            admissions = [a for a in admissions if dept_to_hosp.get(a.get("department_id", ""), "") == hospital_id]

        cutoff = datetime.now() - timedelta(days=days)
        trend = {}
        for a in admissions:
            try:
                dt = datetime.fromisoformat(a["admitted_at"])
                if dt < cutoff:
                    continue
                day = dt.strftime("%Y-%m-%d")
                trend[day] = trend.get(day, 0) + 1
            except (ValueError, KeyError):
                continue
        sorted_days = sorted(trend.keys())
        return [{"date": d, "admissions": trend[d]} for d in sorted_days]

    def get_occupancy_by_ward(self, hospital_id=None):
        departments = self._connector.fetch("departments")
        wards = self._connector.fetch("wards")
        beds = self._connector.fetch("beds")
        dept_to_hosp = {d["id"]: d["hospital_id"] for d in departments}

        if hospital_id:
            dept_ids = {d["id"] for d in departments if d["hospital_id"] == hospital_id}
            wards = [w for w in wards if w["department_id"] in dept_ids]

        result = []
        for w in wards:
            w_beds = [b for b in beds if b.get("ward_id") == w["id"]]
            total = len(w_beds)
            occupied = sum(1 for b in w_beds if b.get("status") == "occupied")
            dept_name = next((d["name"] for d in departments if d["id"] == w["department_id"]), "Unknown")
            result.append({
                "ward_id": w["id"],
                "ward_name": w.get("name", w["id"]),
                "department": dept_name,
                "total": total,
                "occupied": occupied,
                "occupancy_pct": round((occupied / total * 100) if total else 0, 1),
            })
        return result

    def get_equipment_status(self, hospital_id=None):
        equipment = self._connector.fetch("equipment")
        departments = self._connector.fetch("departments")
        dept_to_hosp = {d["id"]: d["hospital_id"] for d in departments}

        if hospital_id:
            dept_ids = {d["id"] for d in departments if d["hospital_id"] == hospital_id}
            equipment = [e for e in equipment if e.get("department_id") in dept_ids]

        status_count = {}
        for e in equipment:
            st = e.get("status", "unknown")
            status_count[st] = status_count.get(st, 0) + 1

        return {
            "total": len(equipment),
            "by_status": status_count,
            "operational_pct": round((status_count.get("operational", 0) / len(equipment) * 100) if equipment else 0, 1),
        }

    def get_staff_summary(self, hospital_id=None):
        staff = self._connector.fetch("staff")
        departments = self._connector.fetch("departments")
        dept_to_hosp = {d["id"]: d["hospital_id"] for d in departments}

        if hospital_id:
            dept_ids = {d["id"] for d in departments if d["hospital_id"] == hospital_id}
            staff = [s for s in staff if s.get("department_id") in dept_ids]

        role_count = {}
        for s in staff:
            role = s.get("role", "Unknown")
            role_count[role] = role_count.get(role, 0) + 1

        active = sum(1 for s in staff if s.get("active", False))
        return {
            "total": len(staff),
            "active": active,
            "inactive": len(staff) - active,
            "by_role": role_count,
        }

    def get_inventory(self, hospital_id=None):
        return self._connector.fetch("medicine_inventory") if hasattr(self._connector, "_fetch_medicine_inventory") else []

from datetime import datetime, timedelta


THRESHOLDS = {
    "bed_occupancy_critical": 90.0,
    "bed_occupancy_warning": 80.0,
    "equipment_uptime_critical": 80.0,
    "equipment_uptime_warning": 90.0,
    "staff_shortage_warning": 5,
}


class AlertEngine:
    def __init__(self, kpi_engine):
        self._kpi = kpi_engine

    def check_alerts(self, hospital_id=None):
        alerts = []
        enriched = self._kpi.get_hospitals_enriched()
        if hospital_id:
            enriched = [h for h in enriched if h["id"] == hospital_id]

        for h in enriched:
            occ = h["bed_occupancy_pct"]
            if occ >= THRESHOLDS["bed_occupancy_critical"]:
                alerts.append(self._make_alert(h, "critical", "bed_occupancy", f"Bed occupancy at {occ}% exceeds critical threshold of {THRESHOLDS['bed_occupancy_critical']}%"))
            elif occ >= THRESHOLDS["bed_occupancy_warning"]:
                alerts.append(self._make_alert(h, "warning", "bed_occupancy", f"Bed occupancy at {occ}% exceeds warning threshold of {THRESHOLDS['bed_occupancy_warning']}%"))

            eq = self._kpi.get_equipment_status(h["id"])
            eq_pct = eq.get("operational_pct", 100)
            if eq_pct < THRESHOLDS["equipment_uptime_critical"]:
                alerts.append(self._make_alert(h, "critical", "equipment", f"Equipment uptime at {eq_pct}% — only {eq.get('by_status', {}).get('operational', 0)} of {eq['total']} operational"))
            elif eq_pct < THRESHOLDS["equipment_uptime_warning"]:
                alerts.append(self._make_alert(h, "warning", "equipment", f"Equipment uptime at {eq_pct}% needs attention"))

            active_staff = h.get("active_staff_count", 0)
            if active_staff < THRESHOLDS["staff_shortage_warning"]:
                alerts.append(self._make_alert(h, "critical", "staffing", f"Critical staff shortage — only {active_staff} active staff"))

        return alerts

    def _make_alert(self, hospital, severity, category, message):
        return {
            "id": f"ALT-{hospital['id']}-{category}-{datetime.now().strftime('%H%M%S')}",
            "hospital_id": hospital["id"],
            "hospital_name": hospital["name"],
            "severity": severity,
            "category": category,
            "message": message,
            "timestamp": datetime.now().isoformat(),
        }

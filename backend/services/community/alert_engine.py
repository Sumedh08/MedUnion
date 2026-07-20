from datetime import datetime


THRESHOLDS = {
    "vaccination_critical": 70.0,
    "vaccination_warning": 90.0,
    "outbreak_active": 1,
    "stock_critical": 5,
    "stock_warning": 15,
    "health_worker_critical": 10,
}


class CommunityAlertEngine:
    def __init__(self, kpi_engine):
        self._kpi = kpi_engine

    def check_alerts(self, district_id=None):
        alerts = []
        enriched = self._kpi.get_districts_enriched()
        if district_id:
            enriched = [d for d in enriched if d["id"] == district_id]

        outbreaks = self._kpi.get_outbreaks()

        for d in enriched:
            did = d["id"]

            vax = d.get("avg_vaccination_coverage", 100)
            if vax < THRESHOLDS["vaccination_critical"]:
                alerts.append(self._make_alert(d, "critical", "vaccination", f"Vaccination coverage at {vax}% — well below 70% threshold"))
            elif vax < THRESHOLDS["vaccination_warning"]:
                alerts.append(self._make_alert(d, "warning", "vaccination", f"Vaccination coverage at {vax}% — below 90% target"))

            d_outbreaks = [o for o in outbreaks if o.get("district_id") == did and o.get("status") in ("active", "monitoring")]
            for ob in d_outbreaks:
                alerts.append(self._make_alert(d, "critical", "outbreak", f"Active {ob.get('disease', 'disease')} outbreak — {ob.get('cases', 0)} cases, risk: {ob.get('risk_level', 'unknown')}"))

            low_stock = d.get("low_stock_items", 0)
            if low_stock > THRESHOLDS["stock_critical"]:
                alerts.append(self._make_alert(d, "critical", "medicine_stock", f"{low_stock} medicine items critically low (< 7 days stock)"))
            elif low_stock > THRESHOLDS["stock_warning"]:
                alerts.append(self._make_alert(d, "warning", "medicine_stock", f"{low_stock} medicine items running low (< 30 days stock)"))

            hw = d.get("active_health_workers", 999)
            if hw < THRESHOLDS["health_worker_critical"]:
                alerts.append(self._make_alert(d, "critical", "staffing", f"Critical health worker shortage — only {hw} active workers"))

        return alerts

    def _make_alert(self, district, severity, category, message):
        return {
            "id": f"ALT-{district['id']}-{category}-{datetime.now().strftime('%H%M%S')}",
            "district_id": district["id"],
            "district_name": district["name"],
            "severity": severity,
            "category": category,
            "message": message,
            "timestamp": datetime.now().isoformat(),
        }

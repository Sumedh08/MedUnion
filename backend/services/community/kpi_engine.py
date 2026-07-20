from datetime import datetime, timedelta


class CommunityKPIEngine:
    def __init__(self, connector):
        self._connector = connector

    def get_districts_enriched(self):
        districts = self._connector.fetch("districts")
        facilities = self._connector.fetch("facilities")
        disease_reports = self._connector.fetch("disease_reports")
        indicators = self._connector.fetch("indicators")
        vaccinations = self._connector.fetch("vaccinations")
        health_workers = self._connector.fetch("health_workers")
        outbreaks = self._connector.fetch("outbreaks")
        medicine_stock = self._connector.fetch("medicine_stock")

        results = []
        for d in districts:
            did = d["id"]
            d_fac = [f for f in facilities if f.get("district_id") == did]
            d_reports = [r for r in disease_reports if r.get("district_id") == did]
            d_inds = [i for i in indicators if i.get("district_id") == did]
            d_vax = [v for v in vaccinations if v.get("district_id") == did]
            d_hw = [h for h in health_workers if h.get("district_id") == did]
            d_ob = [o for o in outbreaks if o.get("district_id") == did]
            d_stock = [s for s in medicine_stock if s.get("district_id") == did]
            results.append(self._enrich(d, d_fac, d_reports, d_inds, d_vax, d_hw, d_ob, d_stock))
        return results

    def get_district_detail(self, district_id):
        enriched = self.get_districts_enriched()
        for d in enriched:
            if d["id"] == district_id:
                return d
        return None

    def compute_kpis(self, district_id=None):
        enriched = self.get_districts_enriched()
        if district_id:
            enriched = [d for d in enriched if d["id"] == district_id]
        return [self._build_kpis(d) for d in enriched]

    def _enrich(self, district, facilities, reports, indicators, vaccinations, health_workers, outbreaks, stock):
        active_fac = [f for f in facilities if f.get("active", False)]
        total_cases = sum(r.get("confirmed_cases", 0) for r in reports)
        total_deaths = sum(r.get("deaths", 0) for r in reports)
        active_hw = [h for h in health_workers if h.get("active", False)]
        active_ob = [o for o in outbreaks if o.get("status") in ("active", "monitoring")]
        low_stock = [s for s in stock if s.get("days_of_stock", 90) < 30]
        avg_vax = 0
        if vaccinations:
            avg_vax = sum(v.get("coverage_pct", 0) for v in vaccinations) / len(vaccinations)

        return {
            **district,
            "facility_count": len(facilities),
            "active_facilities": len(active_fac),
            "total_confirmed_cases": total_cases,
            "total_deaths": total_deaths,
            "active_health_workers": len(active_hw),
            "total_health_workers": len(health_workers),
            "active_outbreaks": len(active_ob),
            "low_stock_items": len(low_stock),
            "avg_vaccination_coverage": round(avg_vax, 1),
        }

    def _build_kpis(self, d):
        return {
            "district_id": d["id"],
            "district_name": d["name"],
            "vaccination_coverage": {
                "value": d.get("avg_vaccination_coverage", 0),
                "unit": "%",
                "benchmark": 90.0,
                "status": "critical" if d.get("avg_vaccination_coverage", 0) < 70 else "warning" if d.get("avg_vaccination_coverage", 0) < 90 else "normal",
            },
            "active_outbreaks": {
                "value": d.get("active_outbreaks", 0),
                "unit": "count",
                "benchmark": 0,
                "status": "critical" if d.get("active_outbreaks", 0) > 0 else "normal",
            },
            "confirmed_cases": {
                "value": d.get("total_confirmed_cases", 0),
                "unit": "count",
                "benchmark": None,
                "status": "normal",
            },
            "health_worker_coverage": {
                "value": d.get("active_health_workers", 0),
                "unit": "count",
                "benchmark": 50,
                "status": "warning" if d.get("active_health_workers", 0) < 20 else "normal",
            },
            "low_stock_items": {
                "value": d.get("low_stock_items", 0),
                "unit": "count",
                "benchmark": 0,
                "status": "critical" if d.get("low_stock_items", 0) > 5 else "warning" if d.get("low_stock_items", 0) > 0 else "normal",
            },
        }

    def get_kpi_summary(self):
        kpis = self.compute_kpis()
        if not kpis:
            return {}
        districts = self.get_districts_enriched()
        total_cases = sum(d.get("total_confirmed_cases", 0) for d in districts)
        total_outbreaks = sum(d.get("active_outbreaks", 0) for d in districts)
        total_hw = sum(d.get("active_health_workers", 0) for d in districts)
        avg_vax = sum(d.get("avg_vaccination_coverage", 0) for d in districts) / len(districts) if districts else 0
        return {
            "districts_count": len(districts),
            "total_confirmed_cases": total_cases,
            "total_active_outbreaks": total_outbreaks,
            "total_health_workers": total_hw,
            "avg_vaccination_coverage": round(avg_vax, 1),
            "districts_with_outbreaks": sum(1 for d in districts if d.get("active_outbreaks", 0) > 0),
        }

    def get_disease_reports(self, district_id=None):
        reports = self._connector.fetch("disease_reports")
        if district_id:
            reports = [r for r in reports if r.get("district_id") == district_id]
        return reports

    def get_outbreaks(self):
        return self._connector.fetch("outbreaks")

    def get_vaccination_summary(self, district_id=None):
        vax = self._connector.fetch("vaccinations")
        if district_id:
            vax = [v for v in vax if v.get("district_id") == district_id]
        by_vaccine = {}
        for v in vax:
            name = v.get("vaccine", "Unknown")
            if name not in by_vaccine:
                by_vaccine[name] = {"total_doses": 0, "coverages": []}
            by_vaccine[name]["total_doses"] += v.get("doses_administered", 0)
            by_vaccine[name]["coverages"].append(v.get("coverage_pct", 0))
        return {
            "total_records": len(vax),
            "by_vaccine": {
                name: {
                    "total_doses": data["total_doses"],
                    "avg_coverage": round(sum(data["coverages"]) / len(data["coverages"]), 1) if data["coverages"] else 0,
                }
                for name, data in by_vaccine.items()
            },
        }

    def get_medicine_stock(self, district_id=None):
        stock = self._connector.fetch("medicine_stock")
        if district_id:
            stock = [s for s in stock if s.get("district_id") == district_id]
        low = [s for s in stock if s.get("days_of_stock", 90) < 30]
        critical = [s for s in stock if s.get("days_of_stock", 90) < 7]
        return {
            "total_items": len(stock),
            "low_stock": len(low),
            "critical_stock": len(critical),
            "items": stock,
        }

    def get_health_worker_summary(self, district_id=None):
        hw = self._connector.fetch("health_workers")
        if district_id:
            hw = [h for h in hw if h.get("district_id") == district_id]
        by_role = {}
        for h in hw:
            role = h.get("role", "Unknown")
            by_role[role] = by_role.get(role, 0) + 1
        active = sum(1 for h in hw if h.get("active", False))
        return {
            "total": len(hw),
            "active": active,
            "inactive": len(hw) - active,
            "by_role": by_role,
        }

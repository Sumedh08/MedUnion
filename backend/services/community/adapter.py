"""Repo-backed adapter mirroring CommunityKPIEngine interface."""

from datetime import datetime as _dt, date as _date

from repositories import CommunityUnitOfWork


class CommunityAdapter:
    def __init__(self, db):
        self._uow = CommunityUnitOfWork(db)

    @staticmethod
    def _to_dict(obj):
        if obj is None:
            return None
        if isinstance(obj, dict):
            return obj
        out = {}
        for c in obj.__table__.columns:
            v = getattr(obj, c.name)
            if isinstance(v, (_dt, _date)):
                v = v.isoformat()
            out[c.name] = v
        return out

    def _rows(self, objs):
        return [self._to_dict(o) for o in (objs or [])]

    def _row(self, obj):
        return self._to_dict(obj)

    def get_districts_enriched(self):
        districts = self._rows(self._uow.districts.get_all())
        facilities = self._rows(self._uow.facilities.get_all())
        disease_reports = self._rows(self._uow.disease_cases.get_all())
        indicators = self._rows(self._uow.indicators.get_all())
        vaccinations = self._rows(self._uow.vaccinations.get_all())
        health_workers = self._rows(self._uow.health_workers.get_all())
        outbreaks = self._rows(self._uow.outbreaks.get_all())
        medicine_stock = self._rows(self._uow.medicine_stock.get_all())
        results = []
        for d in districts:
            did = d["id"]
            results.append(self._enrich(d,
                [f for f in facilities if f.get("district_id") == did],
                [r for r in disease_reports if r.get("district_id") == did],
                [i for i in indicators if i.get("district_id") == did],
                [v for v in vaccinations if v.get("district_id") == did],
                [h for h in health_workers if h.get("district_id") == did],
                [o for o in outbreaks if o.get("district_id") == did],
                [s for s in medicine_stock if s.get("district_id") == did],
            ))
        return results

    def get_district_detail(self, district_id):
        d = self._row(self._uow.districts.get_by_id(district_id))
        if not d:
            return None
        facilities = self._rows(self._uow.facilities.get_by_field("district_id", district_id))
        disease_reports = self._rows(self._uow.disease_cases.get_by_field("district_id", district_id))
        indicators = self._rows(self._uow.indicators.get_by_field("district_id", district_id))
        vaccinations = self._rows(self._uow.vaccinations.get_by_field("district_id", district_id))
        health_workers = self._rows(self._uow.health_workers.get_by_field("district_id", district_id))
        outbreaks = self._rows(self._uow.outbreaks.get_by_field("district_id", district_id))
        medicine_stock = self._rows(self._uow.medicine_stock.get_by_field("district_id", district_id))
        return self._enrich(d, facilities, disease_reports, indicators, vaccinations, health_workers, outbreaks, medicine_stock)

    def compute_kpis(self, district_id=None):
        enriched = self.get_districts_enriched()
        if district_id:
            enriched = [d for d in enriched if d["id"] == district_id]
        return [self._build_kpis(d) for d in enriched]

    def _enrich(self, district, facilities, reports, indicators, vaccinations, health_workers, outbreaks, stock):
        active_fac = [f for f in facilities if f.get("active", False)]
        total_cases = sum(r.get("confirmed", 0) for r in reports)
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
        if district_id:
            return self._rows(self._uow.disease_cases.get_by_field("district_id", district_id))
        return self._rows(self._uow.disease_cases.get_all())

    def get_outbreaks(self):
        return self._rows(self._uow.outbreaks.get_all())

    def get_vaccination_summary(self, district_id=None):
        if district_id:
            vax = self._rows(self._uow.vaccinations.get_by_field("district_id", district_id))
        else:
            vax = self._rows(self._uow.vaccinations.get_all())
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
        if district_id:
            stock = self._rows(self._uow.medicine_stock.get_by_field("district_id", district_id))
        else:
            stock = self._rows(self._uow.medicine_stock.get_all())
        return {
            "items": stock,
            "total": len(stock),
            "low_stock": [s for s in stock if (s.get("days_of_stock") or 0) < 30],
        }

    def get_health_worker_summary(self, district_id=None):
        if district_id:
            hw = self._rows(self._uow.health_workers.get_by_field("district_id", district_id))
        else:
            hw = self._rows(self._uow.health_workers.get_all())
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

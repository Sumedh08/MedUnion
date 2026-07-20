from datetime import datetime, timezone


class BaseLoader:
    """Loads canonical domain records into PostgreSQL via repositories.

    Stamps provenance fields and wraps each resource in a transaction.
    """

    UOW_ATTR = None

    def __init__(self, db, uow):
        self._db = db
        self._uow = uow

    def load(self, resource: str, records: list[dict], import_job_id: str, connector_name: str, source_system: str) -> tuple[int, int]:
        uow_attr = self.get_uow_attr(resource) if hasattr(self, "get_uow_attr") else resource
        repo = getattr(self._uow, uow_attr, None)
        if not repo:
            return 0, 0

        if not records:
            return 0, 0

        now = datetime.now(timezone.utc)
        stamped = []
        seen = set()
        for r in records:
            r["source_system"] = source_system
            r["source_record_id"] = r.get("source_record_id") or r.get("id")
            r["import_job_id"] = import_job_id
            r["connector_name"] = connector_name
            r["last_imported_at"] = now
            rid = r.get("id")
            if rid and rid in seen:
                continue
            if rid:
                seen.add(rid)
            stamped.append(r)

        try:
            inserted = repo.upsert(stamped, conflict_columns=["id"])
            self._db.flush()
            return inserted, 0
        except Exception:
            # Do NOT rollback here — the import transaction boundary is owned by
            # ImportManager (commit on success, rollback on outer failure). Re-raise
            # so the pipeline/manager can decide. Rolling back here would discard
            # the ImportJob and sibling batches loaded in the same transaction.
            raise

    def truncate_all(self, resources: list[str]):
        for res in resources:
            repo = getattr(self._uow, res, None)
            if repo:
                repo.truncate()
        self._db.flush()

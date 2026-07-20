from typing import Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from core.logging import logger


class BaseRepository:
    """Generic CRUD for a SQLAlchemy model."""

    def __init__(self, db: Session, model: type):
        self._db = db
        self._model = model
        self._table = model.__tablename__

    def get_all(self) -> list:
        return list(self._db.query(self._model).all())

    def get_by_id(self, id: str) -> Optional[Any]:
        return self._db.query(self._model).filter(self._model.id == id).first()

    def get_by_field(self, field: str, value: Any) -> list:
        col = getattr(self._model, field, None)
        if col is None:
            logger.warning(f"Unknown field {field} on {self._model.__name__}")
            return []
        return list(self._db.query(self._model).filter(col == value).all())

    def count(self) -> int:
        return self._db.query(self._model).count()

    def bulk_insert(self, records: list[dict]) -> int:
        if not records:
            return 0
        self._db.execute(self._model.__table__.insert(), records)
        return len(records)

    def truncate(self):
        self._db.execute(text(f"TRUNCATE TABLE {self._table} RESTART IDENTITY CASCADE"))

    def upsert(self, records: list[dict], conflict_columns: list[str]) -> int:
        if not records:
            return 0
        from sqlalchemy.dialects.postgresql import insert as pg_insert
        stmt = pg_insert(self._model.__table__).values(records)
        update_cols = {c: stmt.excluded[c] for c in records[0] if c not in conflict_columns}
        if update_cols:
            stmt = stmt.on_conflict_do_update(index_elements=conflict_columns, set_=update_cols)
        self._db.execute(stmt)
        return len(records)

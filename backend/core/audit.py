from typing import Optional
from sqlalchemy.orm import Session
from models.sql.audit_log import AuditLog
from core.logging import logger


def log_action(
    db: Session,
    user_id: str,
    action: str,
    resource: str,
    resource_id: Optional[str] = None,
    details: Optional[dict] = None,
    result: str = "success",
    ip_address: Optional[str] = None,
):
    try:
        log = AuditLog(
            user_id=user_id or "anonymous",
            action=action,
            resource=resource,
            resource_id=resource_id,
            details=details,
            result=result,
            ip_address=ip_address,
        )
        db.add(log)
        db.commit()
    except Exception as e:
        logger.warning(f"Audit log failed: {e}")
        try:
            db.rollback()
        except Exception:
            pass

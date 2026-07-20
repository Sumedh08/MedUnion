from sqlalchemy import Column, Integer, String, DateTime, JSON, Text
from sqlalchemy.sql import func
from core.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), index=True)
    action = Column(String(50))
    resource = Column(String(100))
    resource_id = Column(String(100), nullable=True)
    details = Column(JSON, nullable=True)
    result = Column(String(20), default="success")
    ip_address = Column(String(50), nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

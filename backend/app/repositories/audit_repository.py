import uuid
from datetime import datetime
from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.audit import AuditLog
from app.models.enums import ActorTypeEnum


class AuditRepository:
    def __init__(self, db: Session):
        self.db = db

    def insert(
        self,
        action: str,
        resource_type: str,
        actor_type: ActorTypeEnum = ActorTypeEnum.SYSTEM,
        actor_id: Optional[uuid.UUID] = None,
        resource_id: Optional[uuid.UUID] = None,
        old_value: Optional[dict] = None,
        new_value: Optional[dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        metadata_payload: Optional[dict] = None,
    ) -> AuditLog:
        log_entry = AuditLog(
            action=action,
            resource_type=resource_type,
            actor_type=actor_type,
            actor_id=actor_id,
            resource_id=resource_id,
            old_value=old_value,
            new_value=new_value,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata_payload=metadata_payload,
        )
        self.db.add(log_entry)
        self.db.commit()
        self.db.refresh(log_entry)
        return log_entry

    def search(
        self,
        skip: int = 0,
        limit: int = 100,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        actor_id: Optional[uuid.UUID] = None,
        resource_type: Optional[str] = None,
        action: Optional[str] = None,
    ) -> tuple[Sequence[AuditLog], int]:
        stmt = select(AuditLog)
        
        if start_date:
            stmt = stmt.where(AuditLog.timestamp >= start_date)
        if end_date:
            stmt = stmt.where(AuditLog.timestamp <= end_date)
        if actor_id:
            stmt = stmt.where(AuditLog.actor_id == actor_id)
        if resource_type:
            stmt = stmt.where(AuditLog.resource_type == resource_type)
        if action:
            stmt = stmt.where(AuditLog.action == action)
            
        stmt = stmt.order_by(AuditLog.timestamp.desc())
        
        total_stmt = select(AuditLog)
        if start_date:
            total_stmt = total_stmt.where(AuditLog.timestamp >= start_date)
        if end_date:
            total_stmt = total_stmt.where(AuditLog.timestamp <= end_date)
        if actor_id:
            total_stmt = total_stmt.where(AuditLog.actor_id == actor_id)
        if resource_type:
            total_stmt = total_stmt.where(AuditLog.resource_type == resource_type)
        if action:
            total_stmt = total_stmt.where(AuditLog.action == action)
            
        total = len(self.db.scalars(total_stmt).all()) # simplistic count
        
        logs = self.db.scalars(stmt.offset(skip).limit(limit)).all()
        return logs, total

    def get_by_id(self, log_id: int) -> Optional[AuditLog]:
        return self.db.scalars(select(AuditLog).where(AuditLog.id == log_id)).first()

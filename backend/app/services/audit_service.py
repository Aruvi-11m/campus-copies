import uuid
from datetime import datetime
from typing import Any, Optional, Sequence

from app.models.audit import AuditLog
from app.models.enums import ActorTypeEnum
from app.repositories.audit_repository import AuditRepository


class AuditService:
    def __init__(self, repository: AuditRepository):
        self.repository = repository

    def log_action(
        self,
        action: str,
        resource_type: str,
        actor_type: ActorTypeEnum = ActorTypeEnum.SYSTEM,
        actor_id: Optional[uuid.UUID] = None,
        resource_id: Optional[uuid.UUID] = None,
        old_value: Optional[dict[str, Any]] = None,
        new_value: Optional[dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        metadata_payload: Optional[dict[str, Any]] = None,
    ) -> AuditLog:
        return self.repository.insert(
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

    def search_logs(
        self,
        skip: int = 0,
        limit: int = 100,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        actor_id: Optional[uuid.UUID] = None,
        resource_type: Optional[str] = None,
        action: Optional[str] = None,
    ) -> tuple[Sequence[AuditLog], int]:
        return self.repository.search(
            skip=skip,
            limit=limit,
            start_date=start_date,
            end_date=end_date,
            actor_id=actor_id,
            resource_type=resource_type,
            action=action,
        )

    def get_log_details(self, log_id: int) -> Optional[AuditLog]:
        return self.repository.get_by_id(log_id)

import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_admin
from app.models.admin import Admin
from app.repositories.audit_repository import AuditRepository
from app.schemas.audit import AuditLogResponse
from app.schemas.pagination import PaginatedResponse
from app.services.audit_service import AuditService

router = APIRouter(prefix="/admin/audit", tags=["Admin Audit"])

def get_audit_service(db: Session = Depends(get_db)) -> AuditService:
    repo = AuditRepository(db)
    return AuditService(repo)

@router.get("", response_model=PaginatedResponse[AuditLogResponse])
def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    actor_id: Optional[uuid.UUID] = None,
    resource_type: Optional[str] = None,
    action: Optional[str] = None,
    admin: Admin = Depends(require_admin),
    service: AuditService = Depends(get_audit_service)
):
    logs, total = service.search_logs(
        skip=skip,
        limit=limit,
        start_date=start_date,
        end_date=end_date,
        actor_id=actor_id,
        resource_type=resource_type,
        action=action,
    )
    return PaginatedResponse(
        items=[AuditLogResponse.model_validate(log) for log in logs],
        total=total,
        page=(skip // limit) + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )

@router.get("/{id}", response_model=AuditLogResponse)
def get_audit_log(
    id: int,
    admin: Admin = Depends(require_admin),
    service: AuditService = Depends(get_audit_service)
):
    log = service.get_log_details(id)
    if not log:
        raise HTTPException(status_code=404, detail="Audit log not found")
    return log

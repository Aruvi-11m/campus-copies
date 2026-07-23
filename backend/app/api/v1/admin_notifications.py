from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_admin
from app.models.admin import Admin
from app.repositories.notification_repository import NotificationRepository
from app.schemas.notification import NotificationCreate, NotificationResponse, NotificationUpdate
from app.schemas.pagination import PaginatedResponse
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/admin/notifications", tags=["Admin Notifications"])

def get_notification_service(db: Session = Depends(get_db)) -> NotificationService:
    repo = NotificationRepository(db)
    return NotificationService(repo)

@router.get("", response_model=PaginatedResponse[NotificationResponse])
def get_admin_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    admin: Admin = Depends(require_admin),
    service: NotificationService = Depends(get_notification_service)
):
    notifs, total = service.get_admin_notifications(skip, limit)
    return PaginatedResponse(
        items=[NotificationResponse.model_validate(n) for n in notifs],
        total=total,
        page=(skip // limit) + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )

@router.post("", response_model=NotificationResponse)
def create_notification(
    data: NotificationCreate,
    admin: Admin = Depends(require_admin),
    service: NotificationService = Depends(get_notification_service)
):
    notif = service.create_notification(
        target_user=data.target_user,
        type=data.type,
        event_type=data.event_type,
        title=data.title,
        message=data.message,
        target_user_id=data.target_user_id,
        order_id=data.order_id,
    )
    return notif

@router.patch("/{id}", response_model=NotificationResponse)
def update_notification(
    id: int,
    data: NotificationUpdate,
    admin: Admin = Depends(require_admin),
    service: NotificationService = Depends(get_notification_service)
):
    notif = service.mark_read(id) if data.is_read else None
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notif

@router.delete("/{id}")
def delete_notification(
    id: int,
    admin: Admin = Depends(require_admin),
    service: NotificationService = Depends(get_notification_service)
):
    success = service.delete_notification(id)
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"status": "success"}

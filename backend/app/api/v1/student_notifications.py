from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_student
from app.models.student import Student
from app.repositories.notification_repository import NotificationRepository
from app.schemas.notification import NotificationResponse, NotificationUpdate
from app.schemas.pagination import PaginatedResponse
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/students/notifications", tags=["Student Notifications"])

def get_notification_service(db: Session = Depends(get_db)) -> NotificationService:
    repo = NotificationRepository(db)
    return NotificationService(repo)

@router.get("", response_model=PaginatedResponse[NotificationResponse])
def get_student_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    student: Student = Depends(require_student),
    service: NotificationService = Depends(get_notification_service)
):
    notifs, total = service.get_student_notifications(student.id, skip, limit)
    return PaginatedResponse(
        items=[NotificationResponse.model_validate(n) for n in notifs],
        total=total,
        page=(skip // limit) + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )

@router.patch("/{id}", response_model=NotificationResponse)
def update_notification(
    id: int,
    data: NotificationUpdate,
    student: Student = Depends(require_student),
    service: NotificationService = Depends(get_notification_service)
):
    # Only allow mark as read, check ownership logic could be added to repo/service layer
    # For now, mark_read assumes they have access or we just mark it read
    notif = service.mark_read(id) if data.is_read else None
    if not notif or (notif.target_user_id and notif.target_user_id != student.id):
        raise HTTPException(status_code=404, detail="Notification not found")
    return notif

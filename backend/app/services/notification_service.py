import uuid
from typing import Optional, Sequence

from app.models.notification import Notification
from app.models.enums import NotificationTargetEnum, NotificationTypeEnum
from app.repositories.notification_repository import NotificationRepository


class NotificationService:
    def __init__(self, repository: NotificationRepository):
        self.repository = repository

    def create_notification(
        self,
        target_user: NotificationTargetEnum,
        type: NotificationTypeEnum,
        event_type: str,
        title: str,
        message: str,
        target_user_id: Optional[uuid.UUID] = None,
        order_id: Optional[uuid.UUID] = None,
    ) -> Notification:
        # In future, this might also push to SSE stream or WebSockets
        return self.repository.create(
            target_user=target_user,
            type=type,
            event_type=event_type,
            title=title,
            message=message,
            target_user_id=target_user_id,
            order_id=order_id,
        )

    def broadcast(
        self,
        target_user: NotificationTargetEnum,
        title: str,
        message: str,
        type: NotificationTypeEnum = NotificationTypeEnum.INFO,
        event_type: str = "broadcast",
    ) -> Notification:
        return self.repository.create(
            target_user=target_user,
            target_user_id=None,  # None means all users of that target type
            type=type,
            event_type=event_type,
            title=title,
            message=message,
        )

    def get_admin_notifications(self, skip: int = 0, limit: int = 100) -> tuple[Sequence[Notification], int]:
        return self.repository.list_for_admin(skip, limit)

    def get_student_notifications(self, student_id: uuid.UUID, skip: int = 0, limit: int = 100) -> tuple[Sequence[Notification], int]:
        return self.repository.list_for_student(student_id, skip, limit)

    def mark_read(self, notif_id: int) -> Optional[Notification]:
        return self.repository.update_read_status(notif_id, True)

    def mark_all_read(self, student_id: uuid.UUID) -> None:
        self.repository.mark_all_read_for_student(student_id)

    def delete_notification(self, notif_id: int) -> bool:
        return self.repository.delete(notif_id)

    def unread_count(self, student_id: uuid.UUID) -> int:
        # A quick unread count function could just list and count or execute a specific COUNT query.
        # For simplicity, we use the list but in production we might want a count query in repo.
        # Adding a quick implementation here based on list:
        notifs, _ = self.repository.list_for_student(student_id, skip=0, limit=1000)
        return sum(1 for n in notifs if not n.is_read)

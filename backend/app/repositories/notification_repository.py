import uuid
from typing import Optional, Sequence

from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.models.enums import NotificationTargetEnum, NotificationTypeEnum


class NotificationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        target_user: NotificationTargetEnum,
        type: NotificationTypeEnum,
        event_type: str,
        title: str,
        message: str,
        target_user_id: Optional[uuid.UUID] = None,
        order_id: Optional[uuid.UUID] = None,
    ) -> Notification:
        notif = Notification(
            target_user=target_user,
            target_user_id=target_user_id,
            type=type,
            event_type=event_type,
            title=title,
            message=message,
            order_id=order_id,
        )
        self.db.add(notif)
        self.db.commit()
        self.db.refresh(notif)
        return notif

    def list_for_admin(self, skip: int = 0, limit: int = 100) -> tuple[Sequence[Notification], int]:
        stmt = (
            select(Notification)
            .where(Notification.target_user == NotificationTargetEnum.ADMIN)
            .order_by(Notification.created_at.desc())
        )
        total_stmt = select(Notification).where(Notification.target_user == NotificationTargetEnum.ADMIN)
        total = len(self.db.scalars(total_stmt).all())
        return self.db.scalars(stmt.offset(skip).limit(limit)).all(), total

    def list_for_student(self, student_id: uuid.UUID, skip: int = 0, limit: int = 100) -> tuple[Sequence[Notification], int]:
        stmt = (
            select(Notification)
            .where(
                (Notification.target_user == NotificationTargetEnum.STUDENT)
                & (
                    (Notification.target_user_id == student_id)
                    | (Notification.target_user_id.is_(None))
                )
            )
            .order_by(Notification.created_at.desc())
        )
        total_stmt = select(Notification).where(
            (Notification.target_user == NotificationTargetEnum.STUDENT)
            & (
                (Notification.target_user_id == student_id)
                | (Notification.target_user_id.is_(None))
            )
        )
        total = len(self.db.scalars(total_stmt).all())
        return self.db.scalars(stmt.offset(skip).limit(limit)).all(), total

    def get_by_id(self, notif_id: int) -> Optional[Notification]:
        return self.db.scalars(select(Notification).where(Notification.id == notif_id)).first()

    def update_read_status(self, notif_id: int, is_read: bool) -> Optional[Notification]:
        notif = self.get_by_id(notif_id)
        if notif:
            notif.is_read = is_read
            self.db.commit()
            self.db.refresh(notif)
        return notif

    def mark_all_read_for_student(self, student_id: uuid.UUID) -> None:
        stmt = (
            update(Notification)
            .where(
                (Notification.target_user == NotificationTargetEnum.STUDENT)
                & (
                    (Notification.target_user_id == student_id)
                    | (Notification.target_user_id.is_(None))
                )
            )
            .values(is_read=True)
        )
        self.db.execute(stmt)
        self.db.commit()
        
    def delete(self, notif_id: int) -> bool:
        stmt = delete(Notification).where(Notification.id == notif_id)
        res = self.db.execute(stmt)
        self.db.commit()
        return res.rowcount > 0

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import NotificationTargetEnum, NotificationTypeEnum


class NotificationBase(BaseModel):
    target_user: NotificationTargetEnum
    target_user_id: Optional[uuid.UUID] = None
    type: NotificationTypeEnum
    event_type: str = Field(..., max_length=50)
    title: str = Field(..., max_length=100)
    message: str
    order_id: Optional[uuid.UUID] = None


class NotificationCreate(NotificationBase):
    pass


class NotificationUpdate(BaseModel):
    is_read: bool


class NotificationResponse(NotificationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_read: bool
    created_at: datetime

"""
Campus Copies ERP - Order Status History Model

SQLAlchemy 2.x ORM definition for `order_status_history` table.
Grounding: docs/Database.md §3.15, docs/DatabaseRelationships.md §2.15
"""

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import OrderStatusEnum


class OrderStatusHistory(Base):
    __tablename__ = "order_status_history"

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )
    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    from_status: Mapped[Optional[OrderStatusEnum]] = mapped_column(
        Enum(OrderStatusEnum, name="order_status_enum", create_type=False),
        nullable=True,
        default=None,
    )
    to_status: Mapped[OrderStatusEnum] = mapped_column(
        Enum(OrderStatusEnum, name="order_status_enum", create_type=False),
        nullable=False,
    )
    admin_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("admins.id", ondelete="RESTRICT"),
        nullable=True,
        default=None,
    )
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        default=None,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    order: Mapped["Order"] = relationship(
        "Order",
        back_populates="status_history",
    )
    admin: Mapped[Optional["Admin"]] = relationship(
        "Admin",
        foreign_keys=[admin_id],
    )

    def __repr__(self) -> str:
        return f"<OrderStatusHistory(id={self.id}, order_id={self.order_id}, {self.from_status}->{self.to_status})>"

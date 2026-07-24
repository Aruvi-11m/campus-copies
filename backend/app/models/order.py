"""
Campus Copies ERP - Order ORM Model

SQLAlchemy 2.x ORM model for `orders` table.
Grounding: docs/Database.md §3.3, docs/DatabaseRelationships.md §2.3
"""

import uuid
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import (
    BindingTypeEnum,
    ColorModeEnum,
    OrderStatusEnum,
    PaymentMethodEnum,
    PrintSideEnum,
)


class Order(Base):
    __tablename__ = "orders"
    __table_args__ = (
        CheckConstraint("copies >= 1 AND copies <= 100", name="ck_orders_copies_range"),
        CheckConstraint("page_count >= 1", name="ck_orders_page_count_positive"),
        CheckConstraint(
            "per_page_price >= 0.00", name="ck_orders_per_page_price_positive"
        ),
        CheckConstraint(
            "binding_price >= 0.00", name="ck_orders_binding_price_positive"
        ),
        CheckConstraint("total_price >= 0.00", name="ck_orders_total_price_positive"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    display_id: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("students.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    status: Mapped[OrderStatusEnum] = mapped_column(
        Enum(OrderStatusEnum, name="order_status_enum", create_type=False),
        default=OrderStatusEnum.PENDING_PAYMENT,
        nullable=False,
        index=True,
    )
    print_side: Mapped[PrintSideEnum] = mapped_column(
        Enum(PrintSideEnum, name="print_side_enum", create_type=False),
        nullable=False,
    )
    color_mode: Mapped[ColorModeEnum] = mapped_column(
        Enum(ColorModeEnum, name="color_mode_enum", create_type=False),
        nullable=False,
    )
    binding_type: Mapped[BindingTypeEnum] = mapped_column(
        Enum(BindingTypeEnum, name="binding_type_enum", create_type=False),
        default=BindingTypeEnum.NONE,
        nullable=False,
    )
    copies: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )
    page_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    per_page_price: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )
    binding_price: Mapped[float] = mapped_column(
        Numeric(10, 2),
        default=0.00,
        nullable=False,
    )
    total_price: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )
    payment_method: Mapped[Optional[PaymentMethodEnum]] = mapped_column(
        Enum(PaymentMethodEnum, name="payment_method_enum", create_type=False),
        nullable=True,
        default=None,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_by_admin_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("admins.id", ondelete="RESTRICT"),
        nullable=True,
        default=None,
    )

    # Relationships
    student: Mapped["Student"] = relationship(
        "Student",
        backref="orders",
    )
    files: Mapped[List["OrderFile"]] = relationship(
        "OrderFile",
        back_populates="order",
        cascade="all, delete-orphan",
    )
    pickup_code: Mapped[Optional["PickupCode"]] = relationship(
        "PickupCode",
        uselist=False,
        back_populates="order",
        cascade="all, delete-orphan",
    )
    status_history: Mapped[List["OrderStatusHistory"]] = relationship(
        "OrderStatusHistory",
        back_populates="order",
        cascade="all, delete-orphan",
        order_by="OrderStatusHistory.created_at.asc()",
    )

    def __repr__(self) -> str:
        return f"<Order(id={self.id}, display_id={self.display_id}, status={self.status}, total_price={self.total_price})>"

"""
Campus Copies ERP - Pickup Code Model

SQLAlchemy 2.x ORM definition for `pickup_codes` table.
Grounding: docs/Database.md §3.6, docs/DatabaseRelationships.md §2.6
"""

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import PickupCodeStatusEnum


class PickupCode(Base):
    __tablename__ = "pickup_codes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    code: Mapped[str] = mapped_column(
        String(6),
        nullable=False,
        index=True,
    )
    status: Mapped[PickupCodeStatusEnum] = mapped_column(
        Enum(PickupCodeStatusEnum, name="pickup_code_status_enum", create_type=False),
        default=PickupCodeStatusEnum.ACTIVE,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    redeemed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )

    order: Mapped["Order"] = relationship(
        "Order",
        back_populates="pickup_code",
    )

    def __repr__(self) -> str:
        return f"<PickupCode(id={self.id}, code={self.code}, status={self.status})>"

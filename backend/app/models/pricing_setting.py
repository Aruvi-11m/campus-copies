"""
Campus Copies ERP - Pricing Setting Model

SQLAlchemy 2.x ORM definition for `pricing_settings` table.
Grounding: docs/Database.md §3.7, docs/DatabaseRelationships.md §2.7
"""

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class PricingSetting(Base):
    __tablename__ = "pricing_settings"

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )
    bw_single_side: Mapped[float] = mapped_column(
        Numeric(10, 2),
        default=1.50,
        nullable=False,
    )
    bw_double_side: Mapped[float] = mapped_column(
        Numeric(10, 2),
        default=1.00,
        nullable=False,
    )
    bw_multi_page: Mapped[float] = mapped_column(
        Numeric(10, 2),
        default=1.00,
        nullable=False,
    )
    color_single_side: Mapped[float] = mapped_column(
        Numeric(10, 2),
        default=5.00,
        nullable=False,
    )
    spiral_binding_price: Mapped[float] = mapped_column(
        Numeric(10, 2),
        default=30.00,
        nullable=False,
    )
    soft_binding_price: Mapped[float] = mapped_column(
        Numeric(10, 2),
        default=40.00,
        nullable=False,
    )
    hard_binding_price: Mapped[float] = mapped_column(
        Numeric(10, 2),
        default=70.00,
        nullable=False,
    )
    stapling_price: Mapped[float] = mapped_column(
        Numeric(10, 2),
        default=5.00,
        nullable=False,
    )
    is_current: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    created_by_admin_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("admins.id", ondelete="RESTRICT"),
        nullable=True,
    )

    creator_admin: Mapped[Optional["Admin"]] = relationship(
        "Admin",
        foreign_keys=[created_by_admin_id],
    )

    def __repr__(self) -> str:
        return f"<PricingSetting(id={self.id}, is_current={self.is_current}, bw_single={self.bw_single_side}, color_single={self.color_single_side})>"

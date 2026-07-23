"""
Campus Copies ERP - Cash Ledger ORM Model

Immutable append-only financial transaction ledger.
Every financial event (payment, expense, refund, adjustment) creates one entry.
Historical entries are NEVER modified or deleted.
Grounding: docs/BusinessRules.md §9, docs/Database.md §3.11
"""

import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class LedgerEntry(Base):
    __tablename__ = "ledger_entries"

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )
    entry_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
    )
    # Allowed entry_type values:
    #   PAYMENT_CASH, PAYMENT_UPI, EXPENSE_CASH, EXPENSE_UPI,
    #   REFUND_CASH, REFUND_UPI, ADJUSTMENT

    amount: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )
    # Positive = money in (payment), Negative = money out (expense, refund)

    running_cash_balance: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=0.00,
    )

    order_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="SET NULL"),
        nullable=True,
        default=None,
        index=True,
    )
    payment_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        default=None,
    )
    expense_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        default=None,
    )
    admin_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("admins.id", ondelete="RESTRICT"),
        nullable=True,
        default=None,
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    # Relationships
    admin: Mapped[Optional["Admin"]] = relationship(
        "Admin",
        backref="ledger_entries",
    )

    def __repr__(self) -> str:
        return f"<LedgerEntry(id={self.id}, type={self.entry_type}, amount={self.amount})>"

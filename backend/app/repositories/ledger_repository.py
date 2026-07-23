"""
Campus Copies ERP - Ledger Repository

Data access methods for the immutable append-only LedgerEntry table.
Grounding: docs/BusinessRules.md §9 (BR-FIN-01)
"""

import uuid
from datetime import date, datetime
from typing import List, Optional, Tuple
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.ledger_entry import LedgerEntry
from app.repositories.base import BaseRepository


class LedgerRepository(BaseRepository[LedgerEntry]):
    def __init__(self, db: Session):
        super().__init__(LedgerEntry, db)

    def append_entry(
        self,
        entry_type: str,
        amount: float,
        running_cash_balance: float,
        description: str,
        admin_id: Optional[uuid.UUID] = None,
        order_id: Optional[uuid.UUID] = None,
        payment_id: Optional[uuid.UUID] = None,
        expense_id: Optional[uuid.UUID] = None,
    ) -> LedgerEntry:
        """Appends a new immutable ledger entry. NEVER updates or deletes existing entries."""
        entry = LedgerEntry(
            entry_type=entry_type,
            amount=amount,
            running_cash_balance=running_cash_balance,
            description=description,
            admin_id=admin_id,
            order_id=order_id,
            payment_id=payment_id,
            expense_id=expense_id,
        )
        self.save(entry)
        return entry

    def get_latest_cash_balance(self) -> float:
        """Returns the running_cash_balance of the most recent ledger entry, or 0.0 if empty."""
        latest = (
            self.db.query(LedgerEntry.running_cash_balance)
            .order_by(LedgerEntry.id.desc())
            .first()
        )
        return float(latest[0]) if latest else 0.0

    def list_entries(
        self,
        entry_type: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[LedgerEntry], int]:
        query = self.db.query(LedgerEntry)

        if entry_type and entry_type.strip():
            query = query.filter(LedgerEntry.entry_type == entry_type.strip())

        if date_from:
            query = query.filter(func.date(LedgerEntry.created_at) >= date_from)

        if date_to:
            query = query.filter(func.date(LedgerEntry.created_at) <= date_to)

        total = query.count()
        items = query.order_by(LedgerEntry.id.desc()).offset(skip).limit(limit).all()
        return items, total

    def sum_by_type_prefix(self, prefix: str) -> float:
        """Sum all amounts matching entry_type starting with prefix (e.g., 'PAYMENT_')."""
        result = (
            self.db.query(func.coalesce(func.sum(LedgerEntry.amount), 0.0))
            .filter(LedgerEntry.entry_type.like(f"{prefix}%"))
            .scalar()
        )
        return float(result or 0.0)

    def sum_by_type(self, entry_type: str) -> float:
        """Sum all amounts matching exact entry_type."""
        result = (
            self.db.query(func.coalesce(func.sum(LedgerEntry.amount), 0.0))
            .filter(LedgerEntry.entry_type == entry_type)
            .scalar()
        )
        return float(result or 0.0)

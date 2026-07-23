"""
Campus Copies ERP - Inventory Repository

Data access methods for Inventory entities.
Grounding: docs/Database.md §3.8, §3.9
"""

import uuid
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.inventory import InventoryItem, InventoryTransaction
from app.repositories.base import BaseRepository


class InventoryItemRepository(BaseRepository[InventoryItem]):
    def __init__(self, db: Session):
        super().__init__(InventoryItem, db)

    def get_by_item_code(self, item_code: str) -> Optional[InventoryItem]:
        return (
            self.db.query(InventoryItem)
            .filter(InventoryItem.item_code == item_code)
            .first()
        )

    def get_by_id_for_update(self, item_id: uuid.UUID) -> Optional[InventoryItem]:
        """Gets an item with pessimistic lock for concurrent stock updates."""
        try:
            return (
                self.db.query(InventoryItem)
                .filter(InventoryItem.id == item_id)
                .with_for_update()
                .first()
            )
        except Exception as e:
            # Fallback for SQLite which doesn't support SELECT FOR UPDATE
            if "sqlite" in str(e).lower() or "sqlite" in self.db.bind.dialect.name.lower():
                return self.get_by_id(item_id)
            raise

    def list_active_items(self) -> List[InventoryItem]:
        return (
            self.db.query(InventoryItem)
            .filter(InventoryItem.is_archived == False)
            .all()
        )

    def list_low_stock_items(self) -> List[InventoryItem]:
        return (
            self.db.query(InventoryItem)
            .filter(InventoryItem.is_archived == False)
            .filter(InventoryItem.current_stock < InventoryItem.min_threshold)
            .all()
        )


class InventoryTransactionRepository(BaseRepository[InventoryTransaction]):
    def __init__(self, db: Session):
        super().__init__(InventoryTransaction, db)

    def append_transaction(self, transaction: InventoryTransaction) -> InventoryTransaction:
        """Appends a transaction (append-only ledger)."""
        self.db.add(transaction)
        self.db.flush()
        return transaction

    def list_by_item(
        self, item_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> List[InventoryTransaction]:
        return (
            self.db.query(InventoryTransaction)
            .filter(InventoryTransaction.item_id == item_id)
            .order_by(InventoryTransaction.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def list_transactions(
        self, skip: int = 0, limit: int = 100
    ) -> List[InventoryTransaction]:
        return (
            self.db.query(InventoryTransaction)
            .order_by(InventoryTransaction.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

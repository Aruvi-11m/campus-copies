"""
Campus Copies ERP - Inventory Service

Business logic for managing inventory stock levels, transactions,
automatic deductions, and low-stock detection.
Grounding: docs/BusinessRules.md §6
"""

import math
import uuid
from typing import List, Optional
from sqlalchemy.orm import Session

from app.core.errors import ConflictError, NotFoundError, ValidationError
from app.models.enums import InventoryCategoryEnum, InventoryTxnTypeEnum
from app.models.inventory import InventoryItem, InventoryTransaction
from app.models.order import Order
from app.repositories.inventory_repository import (
    InventoryItemRepository,
    InventoryTransactionRepository,
)
from app.services.dashboard_service import invalidate_dashboard_cache


class InventoryService:
    def __init__(self, db: Session):
        self.db = db
        self.item_repo = InventoryItemRepository(db)
        self.txn_repo = InventoryTransactionRepository(db)

    def _execute_stock_change(
        self,
        item: InventoryItem,
        quantity_change: int,
        transaction_type: InventoryTxnTypeEnum,
        admin_id: Optional[uuid.UUID] = None,
        order_id: Optional[uuid.UUID] = None,
        reason: Optional[str] = None,
    ) -> InventoryTransaction:
        """Core internal method to adjust stock and record a transaction."""
        if item.current_stock + quantity_change < 0:
            raise ConflictError(
                f"Insufficient stock for {item.item_name}. Required: {abs(quantity_change)}, Available: {item.current_stock}"
            )

        item.current_stock += quantity_change

        txn = InventoryTransaction(
            item_id=item.id,
            admin_id=admin_id,
            order_id=order_id,
            transaction_type=transaction_type,
            quantity_change=quantity_change,
            stock_after_txn=item.current_stock,
            unit_cost_snapshot=item.unit_cost,
            reason=reason,
        )
        self.txn_repo.append_transaction(txn)
        invalidate_dashboard_cache()
        return txn

    def add_stock(
        self,
        item_id: uuid.UUID,
        admin_id: uuid.UUID,
        quantity: int,
        reason: Optional[str] = None,
    ) -> InventoryTransaction:
        if quantity <= 0:
            raise ValidationError("Add stock quantity must be positive")

        item = self.item_repo.get_by_id_for_update(item_id)
        if not item:
            raise NotFoundError("Inventory item not found")

        return self._execute_stock_change(
            item=item,
            quantity_change=quantity,
            transaction_type=InventoryTxnTypeEnum.RESTOCK,
            admin_id=admin_id,
            reason=reason,
        )

    def remove_stock(
        self,
        item_id: uuid.UUID,
        admin_id: uuid.UUID,
        quantity: int,
        transaction_type: InventoryTxnTypeEnum,
        reason: Optional[str] = None,
    ) -> InventoryTransaction:
        if quantity <= 0:
            raise ValidationError("Remove stock quantity must be positive")
        if transaction_type not in (
            InventoryTxnTypeEnum.WASTAGE,
            InventoryTxnTypeEnum.ADJUSTMENT,
        ):
            raise ValidationError("Invalid transaction type for manual removal")

        item = self.item_repo.get_by_id_for_update(item_id)
        if not item:
            raise NotFoundError("Inventory item not found")

        return self._execute_stock_change(
            item=item,
            quantity_change=-quantity,
            transaction_type=transaction_type,
            admin_id=admin_id,
            reason=reason,
        )

    def deduct_order_materials(self, order: Order, admin_id: uuid.UUID) -> None:
        """
        Automatically deducts materials based on the order's print configuration.
        Expected to be called within an active transaction.
        """
        # Calculate requirements
        # For simplicity in V1, we fetch the first active item for the category.
        paper_qty = order.copies * (
            order.page_count if order.print_side.value == "SINGLE_SIDE" else math.ceil(order.page_count / 2)
        )
        ink_qty = order.copies * order.page_count  # 1 unit per printed page face
        binding_qty = order.copies if order.binding_type.value != "NONE" else 0

        # Find items
        active_items = self.item_repo.list_active_items()
        paper_item = next(
            (i for i in active_items if i.category == InventoryCategoryEnum.PAPER), None
        )
        ink_item = next(
            (i for i in active_items if i.category == InventoryCategoryEnum.INK), None
        )
        binding_item = None
        if binding_qty > 0:
            binding_item = next(
                (
                    i
                    for i in active_items
                    if i.category == InventoryCategoryEnum.BINDING
                    and i.sub_category.value == order.binding_type.value
                ),
                None,
            )

        # Execute deductions (will lock the rows)
        if paper_item and paper_qty > 0:
            p_item = self.item_repo.get_by_id_for_update(paper_item.id)
            if p_item:
                self._execute_stock_change(
                    item=p_item,
                    quantity_change=-paper_qty,
                    transaction_type=InventoryTxnTypeEnum.CONSUMPTION,
                    admin_id=admin_id,
                    order_id=order.id,
                    reason=f"Auto deduction for order {order.display_id}",
                )

        if ink_item and ink_qty > 0:
            i_item = self.item_repo.get_by_id_for_update(ink_item.id)
            if i_item:
                self._execute_stock_change(
                    item=i_item,
                    quantity_change=-ink_qty,
                    transaction_type=InventoryTxnTypeEnum.CONSUMPTION,
                    admin_id=admin_id,
                    order_id=order.id,
                    reason=f"Auto deduction for order {order.display_id}",
                )

        if binding_item and binding_qty > 0:
            b_item = self.item_repo.get_by_id_for_update(binding_item.id)
            if b_item:
                self._execute_stock_change(
                    item=b_item,
                    quantity_change=-binding_qty,
                    transaction_type=InventoryTxnTypeEnum.CONSUMPTION,
                    admin_id=admin_id,
                    order_id=order.id,
                    reason=f"Auto deduction for order {order.display_id}",
                )

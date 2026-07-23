"""
Campus Copies ERP - Inventory API Routes

Endpoints for inventory management (Admin only).
Grounding: docs/API.md
"""

import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.errors import ConflictError, NotFoundError
from app.database import get_db
from app.dependencies import require_admin
from app.models.admin import Admin
from app.models.enums import InventoryTxnTypeEnum
from app.models.inventory import InventoryItem
from app.repositories.inventory_repository import (
    InventoryItemRepository,
    InventoryTransactionRepository,
)
from app.schemas.inventory import (
    InventoryItemCreate,
    InventoryItemOut,
    InventoryItemUpdate,
    InventoryStockAdjustment,
    InventoryTransactionOut,
)
from app.services.inventory_service import InventoryService

router = APIRouter()


@router.post("", response_model=InventoryItemOut, status_code=201)
def create_inventory_item(
    item_data: InventoryItemCreate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(require_admin),
):
    """Creates a new inventory item."""
    repo = InventoryItemRepository(db)
    
    # Check duplicate
    if repo.get_by_item_code(item_data.item_code):
        raise ConflictError(f"Inventory item with code '{item_data.item_code}' already exists")
    
    new_item = InventoryItem(
        item_code=item_data.item_code,
        item_name=item_data.item_name,
        category=item_data.category,
        sub_category=item_data.sub_category,
        min_threshold=item_data.min_threshold,
        unit_cost=item_data.unit_cost,
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item


@router.get("", response_model=List[InventoryItemOut])
def list_inventory_items(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(require_admin),
):
    """Lists all active inventory items."""
    repo = InventoryItemRepository(db)
    return repo.list_active_items()


@router.get("/low-stock", response_model=List[InventoryItemOut])
def list_low_stock_items(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(require_admin),
):
    """Lists all active inventory items that are below their minimum threshold."""
    repo = InventoryItemRepository(db)
    return repo.list_low_stock_items()


@router.get("/transactions", response_model=List[InventoryTransactionOut])
def list_all_inventory_transactions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(require_admin),
):
    """Lists global inventory transaction history (append-only ledger)."""
    repo = InventoryTransactionRepository(db)
    return repo.list_transactions(skip=skip, limit=limit)


@router.get("/{item_id}", response_model=InventoryItemOut)
def get_inventory_item(
    item_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(require_admin),
):
    """Retrieves a specific inventory item by ID."""
    repo = InventoryItemRepository(db)
    item = repo.get_by_id(item_id)
    if not item:
        raise NotFoundError("Inventory item not found")
    return item


@router.patch("/{item_id}", response_model=InventoryItemOut)
def update_inventory_item(
    item_id: uuid.UUID,
    update_data: InventoryItemUpdate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(require_admin),
):
    """Updates inventory item metadata (name, cost, threshold). Cannot change stock levels here."""
    repo = InventoryItemRepository(db)
    item = repo.get_by_id(item_id)
    if not item:
        raise NotFoundError("Inventory item not found")

    if update_data.item_name is not None:
        item.item_name = update_data.item_name
    if update_data.min_threshold is not None:
        item.min_threshold = update_data.min_threshold
    if update_data.unit_cost is not None:
        item.unit_cost = update_data.unit_cost
    if update_data.is_archived is not None:
        item.is_archived = update_data.is_archived

    db.commit()
    db.refresh(item)
    return item


@router.post("/{item_id}/stock", response_model=InventoryTransactionOut)
def adjust_inventory_stock(
    item_id: uuid.UUID,
    adjustment: InventoryStockAdjustment,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(require_admin),
):
    """
    Manually adds or removes stock.
    For adding: RESTOCK (quantity_change > 0)
    For removing: WASTAGE, ADJUSTMENT (quantity_change > 0 is passed to remove_stock)
    """
    inventory_service = InventoryService(db)
    
    if adjustment.transaction_type == InventoryTxnTypeEnum.RESTOCK:
        txn = inventory_service.add_stock(
            item_id=item_id,
            admin_id=current_admin.id,
            quantity=adjustment.quantity_change,
            reason=adjustment.reason,
        )
    elif adjustment.transaction_type in (InventoryTxnTypeEnum.WASTAGE, InventoryTxnTypeEnum.ADJUSTMENT):
        txn = inventory_service.remove_stock(
            item_id=item_id,
            admin_id=current_admin.id,
            quantity=adjustment.quantity_change,
            transaction_type=adjustment.transaction_type,
            reason=adjustment.reason,
        )
    else:
        raise ConflictError(f"Manual stock adjustment cannot use type {adjustment.transaction_type.value}")
        
    db.commit()
    return txn

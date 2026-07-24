import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import (
    InventoryCategoryEnum,
    InventorySubCategoryEnum,
    InventoryTxnTypeEnum,
)


class InventoryItemBase(BaseModel):
    item_code: str = Field(..., max_length=50)
    item_name: str = Field(..., max_length=100)
    category: InventoryCategoryEnum
    sub_category: InventorySubCategoryEnum = InventorySubCategoryEnum.NONE
    min_threshold: int = Field(default=100, ge=0)
    unit_cost: Decimal = Field(default=Decimal("0.00"), ge=0)


class InventoryItemCreate(InventoryItemBase):
    pass


class InventoryItemUpdate(BaseModel):
    item_name: Optional[str] = Field(None, max_length=100)
    min_threshold: Optional[int] = Field(None, ge=0)
    unit_cost: Optional[Decimal] = Field(None, ge=0)
    is_archived: Optional[bool] = None


class InventoryItemOut(InventoryItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    current_stock: int
    is_archived: bool
    created_at: datetime
    updated_at: datetime


class InventoryTransactionBase(BaseModel):
    item_id: uuid.UUID
    quantity_change: int


class InventoryTransactionCreate(BaseModel):
    quantity_change: int
    reason: Optional[str] = None


class InventoryTransactionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    item_id: uuid.UUID
    admin_id: Optional[uuid.UUID]
    order_id: Optional[uuid.UUID]
    transaction_type: InventoryTxnTypeEnum
    quantity_change: int
    stock_after_txn: int
    unit_cost_snapshot: Decimal
    reason: Optional[str]
    created_at: datetime


class InventoryStockAdjustment(BaseModel):
    quantity_change: int = Field(...)
    transaction_type: InventoryTxnTypeEnum = Field(...)
    reason: Optional[str] = None

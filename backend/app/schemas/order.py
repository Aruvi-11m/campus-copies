"""
Campus Copies ERP - Order Request & Response Pydantic Schemas

Grounding: docs/API.md §4, docs/BackendSpecification.md §6
"""

import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import BindingTypeEnum, ColorModeEnum, OrderStatusEnum, PaymentMethodEnum, PrintSideEnum


class OrderCreateRequest(BaseModel):
    file_ids: List[uuid.UUID] = Field(..., min_length=1, max_length=5, description="List of 1 to 5 uploaded file UUIDs")
    print_side: PrintSideEnum = Field(..., description="SINGLE_SIDE, DOUBLE_SIDE, or MULTI_PAGE")
    color_mode: ColorModeEnum = Field(..., description="BW or COLOR")
    binding_type: BindingTypeEnum = Field(default=BindingTypeEnum.NONE, description="NONE, SPIRAL, SOFT_COVER, HARD_COVER, STAPLE_PINS")
    copies: int = Field(default=1, ge=1, le=100, description="Number of print copies (1..100)")


class OrderStatusUpdateRequest(BaseModel):
    status: OrderStatusEnum = Field(..., description="Target advanced OrderStatusEnum state")
    payment_method: Optional[PaymentMethodEnum] = Field(default=None, description="Required when marking status as PAID")
    notes: Optional[str] = Field(default=None, description="Optional transition notes")


class OrderFileItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    original_name: str
    file_size: int
    mime_type: str


class OrderStatusHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    from_status: Optional[str] = None
    to_status: str
    notes: Optional[str] = None
    created_at: datetime


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    display_id: str
    student_id: uuid.UUID
    status: str
    print_side: str
    color_mode: str
    binding_type: str
    copies: int
    page_count: int
    per_page_price: float
    binding_price: float
    total_price: float
    payment_method: Optional[str] = None
    pickup_code: Optional[str] = None
    files: List[OrderFileItemResponse] = []
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_orm_order(cls, order) -> "OrderResponse":
        pickup_str = order.pickup_code.code if order.pickup_code else None
        files_data = [OrderFileItemResponse.model_validate(f) for f in order.files]
        return cls(
            id=order.id,
            display_id=order.display_id,
            student_id=order.student_id,
            status=order.status.value if hasattr(order.status, 'value') else str(order.status),
            print_side=order.print_side.value if hasattr(order.print_side, 'value') else str(order.print_side),
            color_mode=order.color_mode.value if hasattr(order.color_mode, 'value') else str(order.color_mode),
            binding_type=order.binding_type.value if hasattr(order.binding_type, 'value') else str(order.binding_type),
            copies=order.copies,
            page_count=order.page_count,
            per_page_price=float(order.per_page_price),
            binding_price=float(order.binding_price),
            total_price=float(order.total_price),
            payment_method=order.payment_method.value if order.payment_method and hasattr(order.payment_method, 'value') else None,
            pickup_code=pickup_str,
            files=files_data,
            created_at=order.created_at,
            updated_at=order.updated_at,
        )


class PaginatedOrdersResponse(BaseModel):
    items: List[OrderResponse]
    total: int
    page: int
    size: int
    pages: int

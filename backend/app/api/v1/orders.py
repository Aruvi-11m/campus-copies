"""
Campus Copies ERP - Student & Admin Order API Endpoints

Handlers for order submission, order history, details query, and admin status updates.
Grounding: docs/API.md §4, docs/BackendSpecification.md §8
"""

import math
import uuid
from datetime import datetime, timezone
from typing import Optional, Union

from fastapi import APIRouter, Depends, Query, Request, status
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_admin, require_student
from app.models.admin import Admin
from app.models.enums import OrderStatusEnum
from app.models.student import Student
from app.schemas.order import (
    OrderCreateRequest,
    OrderResponse,
    OrderStatusUpdateRequest,
    PaginatedOrdersResponse,
)
from app.services.order_service import OrderService

router = APIRouter(prefix="/orders", tags=["Order Management"])
limiter = Limiter(key_func=get_remote_address)


def build_success_response(
    data: dict, status_code: int = status.HTTP_200_OK
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "success": True,
            "data": data,
            "error": None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Print Order",
)
@limiter.limit("10/hour")
async def create_order(
    request: Request,
    body: OrderCreateRequest,
    current_student: Student = Depends(require_student),
    db: Session = Depends(get_db),
) -> JSONResponse:
    """
    Submits a print order for authenticated student.
    Validates uploaded files, computes pricing snapshot, and assigns 6-character pickup code.
    """
    service = OrderService(db)
    order = service.create_order(
        student=current_student,
        file_ids=body.file_ids,
        print_side=body.print_side,
        color_mode=body.color_mode,
        binding_type=body.binding_type,
        copies=body.copies,
    )
    order_data = OrderResponse.from_orm_order(order)
    return build_success_response(
        order_data.model_dump(mode="json"), status_code=status.HTTP_201_CREATED
    )


@router.get(
    "",
    response_model=PaginatedOrdersResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Student Order History",
)
async def list_student_orders(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_student: Student = Depends(require_student),
    db: Session = Depends(get_db),
) -> JSONResponse:
    """
    Lists order submission history for authenticated student.
    """
    service = OrderService(db)
    skip = (page - 1) * size
    orders, total = service.order_repo.list_by_student(
        student_id=current_student.id,
        skip=skip,
        limit=size,
    )

    items = [OrderResponse.from_orm_order(o) for o in orders]
    total_pages = math.ceil(total / size) if total > 0 else 1

    paginated = PaginatedOrdersResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=total_pages,
    )
    return build_success_response(paginated.model_dump(mode="json"))


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Order Details",
)
async def get_order_details(
    order_id: uuid.UUID,
    current_user: Union[Student, Admin] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> JSONResponse:
    """
    Retrieves order details. Enforces student ownership checks (Admins bypass).
    """
    service = OrderService(db)
    order = service.get_order_by_id(order_id, requesting_user=current_user)
    order_data = OrderResponse.from_orm_order(order)
    return build_success_response(order_data.model_dump(mode="json"))


@router.patch(
    "/{order_id}/status",
    response_model=OrderResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Order Status (Admin Only)",
)
async def update_order_status(
    order_id: uuid.UUID,
    body: OrderStatusUpdateRequest,
    current_admin: Admin = Depends(require_admin),
    db: Session = Depends(get_db),
) -> JSONResponse:
    """
    Advances order status using strict forward-only state machine transition logic.
    Admin authorization required. Returns HTTP 409 Conflict if transition is invalid.
    """
    service = OrderService(db)
    updated_order = service.update_order_status(
        order_id=order_id,
        new_status=body.status,
        admin=current_admin,
        payment_method=body.payment_method,
        notes=body.notes,
    )
    order_data = OrderResponse.from_orm_order(updated_order)
    return build_success_response(order_data.model_dump(mode="json"))

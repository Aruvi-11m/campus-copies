"""
Campus Copies ERP - Admin Order Management API Endpoints

Admin order listing, search, filtering, and pagination.
Grounding: docs/API.md §4.5, docs/BackendSpecification.md §8
"""

import math
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_admin
from app.models.admin import Admin
from app.models.enums import OrderStatusEnum
from app.schemas.order import OrderResponse, PaginatedOrdersResponse
from app.services.order_service import OrderService

router = APIRouter(prefix="/admin/orders", tags=["Admin Order Management"])


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


@router.get(
    "",
    response_model=PaginatedOrdersResponse,
    status_code=status.HTTP_200_OK,
    summary="Admin Search & Filter Orders",
)
async def list_admin_orders(
    search: Optional[str] = Query(
        None, description="Search by display ID, student name, or mobile"
    ),
    order_status: Optional[OrderStatusEnum] = Query(
        None, alias="status", description="Filter by order status"
    ),
    department: Optional[str] = Query(None, description="Filter by student department"),
    date_from: Optional[datetime] = Query(None, description="Filter from created date"),
    date_to: Optional[datetime] = Query(None, description="Filter to created date"),
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    current_admin: Admin = Depends(require_admin),
    db: Session = Depends(get_db),
) -> JSONResponse:
    """
    Search and filter order submissions across all students.
    Admin authorization required.
    """
    service = OrderService(db)
    skip = (page - 1) * size

    orders, total = service.order_repo.list_admin_orders(
        search=search,
        status=order_status,
        department=department,
        date_from=date_from,
        date_to=date_to,
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

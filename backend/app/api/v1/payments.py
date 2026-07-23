"""
Campus Copies ERP - Payment API Routes

Admin payment verification, ledger viewing, and financial balance endpoints.
Grounding: docs/API.md §7, docs/BackendSpecification.md §1
"""

import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.errors import build_error_response
from app.database import get_db
from app.dependencies import require_admin
from app.models.admin import Admin
from app.schemas.payment import (
    FinanceBalanceResponse,
    FinanceSummaryResponse,
    LedgerEntryResponse,
    PaginatedLedgerResponse,
    PaymentResponse,
    PaymentVerifyRequest,
)
from app.services.finance_service import FinanceService

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post(
    "/verify",
    response_model=None,
    status_code=201,
    summary="Admin verifies and records payment for an order",
)
def verify_payment(
    payload: PaymentVerifyRequest,
    admin: Admin = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Verifies payment for an order, transitions order to PAID status,
    creates immutable payment record, and updates the financial ledger.
    BR-PAY: Prevents duplicate verification. Validates amount matches order total.
    """
    finance_service = FinanceService(db)
    payment = finance_service.verify_payment(
        order_id=payload.order_id,
        amount=payload.amount,
        payment_method=payload.payment_method,
        admin=admin,
        notes=payload.notes,
    )
    return {
        "success": True,
        "data": PaymentResponse.from_orm_payment(payment).model_dump(mode="json"),
        "message": "Payment verified and recorded successfully",
    }


@router.get(
    "/balance",
    summary="Admin retrieves current financial balance",
)
def get_financial_balance(
    admin: Admin = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Returns current cash-in-hand, revenue by method, total expenses, and net profit."""
    finance_service = FinanceService(db)
    balance = finance_service.get_balance()
    return {
        "success": True,
        "data": FinanceBalanceResponse(**balance).model_dump(mode="json"),
    }


@router.get(
    "/summary",
    summary="Admin retrieves financial summary for a period",
)
def get_financial_summary(
    period: str = Query(default="daily", description="daily|weekly|monthly|yearly"),
    admin: Admin = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Returns aggregated financial metrics for the specified period."""
    finance_service = FinanceService(db)
    summary = finance_service.get_summary(period=period)
    return {
        "success": True,
        "data": FinanceSummaryResponse(**summary).model_dump(mode="json"),
    }


@router.get(
    "/ledger",
    summary="Admin retrieves financial ledger entries",
)
def get_financial_ledger(
    entry_type: Optional[str] = Query(default=None, description="Filter by entry type"),
    page: int = Query(default=1, ge=1, description="Page number"),
    limit: int = Query(default=50, ge=1, le=100, description="Items per page"),
    admin: Admin = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Returns paginated immutable ledger entries for admin review."""
    finance_service = FinanceService(db)
    ledger_repo = finance_service.ledger_repo

    skip = (page - 1) * limit
    items, total = ledger_repo.list_entries(
        entry_type=entry_type,
        skip=skip,
        limit=limit,
    )

    return {
        "success": True,
        "data": PaginatedLedgerResponse(
            items=[LedgerEntryResponse.from_orm_entry(e) for e in items],
            total=total,
            page=page,
            size=limit,
            pages=(total + limit - 1) // limit if total > 0 else 1,
        ).model_dump(mode="json"),
    }


@router.get(
    "/{order_id}",
    summary="Admin retrieves payment details for a specific order",
)
def get_payment_for_order(
    order_id: uuid.UUID,
    admin: Admin = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Returns the payment record for the specified order."""
    finance_service = FinanceService(db)
    payment = finance_service.get_payment_by_order_id(order_id)
    if not payment:
        from app.core.errors import NotFoundError
        raise NotFoundError(f"No payment found for order '{order_id}'")
    return {
        "success": True,
        "data": PaymentResponse.from_orm_payment(payment).model_dump(mode="json"),
    }

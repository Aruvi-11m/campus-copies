"""
Campus Copies ERP - Expense API Routes

Admin expense recording and retrieval endpoints.
Grounding: docs/API.md §9.2-9.3, docs/BackendSpecification.md §1
"""

import uuid
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_admin
from app.models.admin import Admin
from app.schemas.payment import (
    ExpenseCreateRequest,
    ExpenseResponse,
    PaginatedExpensesResponse,
)
from app.services.finance_service import FinanceService

router = APIRouter(prefix="/expenses", tags=["Expenses"])


@router.post(
    "",
    response_model=None,
    status_code=201,
    summary="Admin records a new operating expense",
)
def create_expense(
    payload: ExpenseCreateRequest,
    admin: Admin = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Records an operating expense and creates corresponding immutable ledger entry.
    Cash expenses reduce the cash-in-hand balance.
    """
    finance_service = FinanceService(db)
    expense = finance_service.create_expense(
        amount=payload.amount,
        category=payload.category,
        description=payload.description,
        admin=admin,
        expense_date=payload.expense_date,
        payment_method=payload.payment_method,
    )
    return {
        "success": True,
        "data": ExpenseResponse.from_orm_expense(expense).model_dump(mode="json"),
        "message": "Expense recorded successfully",
    }


@router.get(
    "",
    summary="Admin retrieves expense list with filtering and pagination",
)
def list_expenses(
    category: Optional[str] = Query(default=None, description="Filter by category"),
    date_from: Optional[date] = Query(default=None, description="Start date filter"),
    date_to: Optional[date] = Query(default=None, description="End date filter"),
    page: int = Query(default=1, ge=1, description="Page number"),
    limit: int = Query(default=50, ge=1, le=100, description="Items per page"),
    admin: Admin = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Returns paginated expense records with optional category and date filtering."""
    finance_service = FinanceService(db)
    expense_repo = finance_service.expense_repo

    skip = (page - 1) * limit
    items, total = expense_repo.list_expenses(
        category=category,
        date_from=date_from,
        date_to=date_to,
        skip=skip,
        limit=limit,
    )

    return {
        "success": True,
        "data": PaginatedExpensesResponse(
            items=[ExpenseResponse.from_orm_expense(e) for e in items],
            total=total,
            page=page,
            size=limit,
            pages=(total + limit - 1) // limit if total > 0 else 1,
        ).model_dump(mode="json"),
    }

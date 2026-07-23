"""
Campus Copies ERP - Payment & Finance Pydantic Schemas

Request/response schemas for payment verification, expenses, and financial summary.
Grounding: docs/API.md §7, docs/BusinessRules.md §5, §9
"""

import uuid
from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import PaymentMethodEnum


# ──────────────────────────────────────────────────
# Payment Schemas
# ──────────────────────────────────────────────────

class PaymentVerifyRequest(BaseModel):
    order_id: uuid.UUID = Field(..., description="UUID of the order to verify payment for")
    amount: float = Field(..., gt=0.00, description="Payment amount (must match order total_price)")
    payment_method: PaymentMethodEnum = Field(..., description="UPI or CASH")
    notes: Optional[str] = Field(default=None, description="Optional verification notes")


class PaymentRefundRequest(BaseModel):
    order_id: uuid.UUID = Field(..., description="UUID of the order to refund")
    amount: float = Field(..., gt=0.00, description="Refund amount")
    reason: str = Field(..., min_length=1, max_length=500, description="Reason for refund")


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    order_id: uuid.UUID
    amount: float
    payment_method: str
    verified_by_admin_id: uuid.UUID
    payment_date: datetime
    notes: Optional[str] = None

    @classmethod
    def from_orm_payment(cls, payment) -> "PaymentResponse":
        return cls(
            id=payment.id,
            order_id=payment.order_id,
            amount=float(payment.amount),
            payment_method=payment.payment_method.value if hasattr(payment.payment_method, 'value') else str(payment.payment_method),
            verified_by_admin_id=payment.verified_by_admin_id,
            payment_date=payment.payment_date,
            notes=payment.notes,
        )


# ──────────────────────────────────────────────────
# Expense Schemas
# ──────────────────────────────────────────────────

class ExpenseCreateRequest(BaseModel):
    amount: float = Field(..., gt=0.00, description="Expense amount")
    category: str = Field(..., min_length=1, max_length=50, description="Expense category (e.g., MATERIALS, UTILITIES)")
    description: str = Field(..., min_length=1, max_length=1000, description="Expense description")
    expense_date: Optional[date] = Field(default=None, description="Date expense incurred (defaults to today)")
    payment_method: PaymentMethodEnum = Field(default=PaymentMethodEnum.CASH, description="UPI or CASH")


class ExpenseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    amount: float
    category: str
    description: str
    expense_date: date
    payment_method: str
    created_by_admin_id: uuid.UUID
    created_at: datetime

    @classmethod
    def from_orm_expense(cls, expense) -> "ExpenseResponse":
        return cls(
            id=expense.id,
            amount=float(expense.amount),
            category=expense.category,
            description=expense.description,
            expense_date=expense.expense_date,
            payment_method=expense.payment_method.value if hasattr(expense.payment_method, 'value') else str(expense.payment_method),
            created_by_admin_id=expense.created_by_admin_id,
            created_at=expense.created_at,
        )


class PaginatedExpensesResponse(BaseModel):
    items: List[ExpenseResponse]
    total: int
    page: int
    size: int
    pages: int


# ──────────────────────────────────────────────────
# Finance / Ledger Schemas
# ──────────────────────────────────────────────────

class FinanceBalanceResponse(BaseModel):
    cash_in_hand: float = Field(..., description="Current physical cash balance")
    total_upi_revenue: float = Field(..., description="Total UPI revenue collected")
    total_cash_revenue: float = Field(..., description="Total cash revenue collected")
    total_revenue: float = Field(..., description="Gross total revenue (UPI + CASH)")
    total_expenses: float = Field(..., description="Total operating expenses")
    net_profit: float = Field(..., description="Net profit = revenue - expenses")


class FinanceSummaryResponse(BaseModel):
    period: str = Field(..., description="Summary period (daily/weekly/monthly/yearly)")
    date: Optional[str] = None
    total_orders_paid: int = Field(default=0, description="Orders with verified payment in period")
    total_revenue: float = Field(default=0.00, description="Gross revenue in period")
    upi_revenue: float = Field(default=0.00, description="UPI revenue in period")
    cash_revenue: float = Field(default=0.00, description="Cash revenue in period")
    total_expenses: float = Field(default=0.00, description="Total expenses in period")
    net_profit: float = Field(default=0.00, description="Net profit in period")
    cash_in_hand: float = Field(default=0.00, description="Cash balance at period end")


class LedgerEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    entry_type: str
    amount: float
    running_cash_balance: float
    order_id: Optional[uuid.UUID] = None
    payment_id: Optional[uuid.UUID] = None
    expense_id: Optional[uuid.UUID] = None
    admin_id: Optional[uuid.UUID] = None
    description: str
    created_at: datetime

    @classmethod
    def from_orm_entry(cls, entry) -> "LedgerEntryResponse":
        return cls(
            id=entry.id,
            entry_type=entry.entry_type,
            amount=float(entry.amount),
            running_cash_balance=float(entry.running_cash_balance),
            order_id=entry.order_id,
            payment_id=entry.payment_id,
            expense_id=entry.expense_id,
            admin_id=entry.admin_id,
            description=entry.description,
            created_at=entry.created_at,
        )


class PaginatedLedgerResponse(BaseModel):
    items: List[LedgerEntryResponse]
    total: int
    page: int
    size: int
    pages: int

"""
Campus Copies ERP - Expense Repository

Data access methods for Expense entity.
Grounding: docs/Database.md §3.10, docs/BackendSpecification.md §5
"""

import uuid
from datetime import date, datetime
from typing import List, Optional, Tuple
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.expense import Expense
from app.models.enums import PaymentMethodEnum
from app.repositories.base import BaseRepository


class ExpenseRepository(BaseRepository[Expense]):
    def __init__(self, db: Session):
        super().__init__(Expense, db)

    def list_expenses(
        self,
        category: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[Expense], int]:
        query = self.db.query(Expense)

        if category and category.strip():
            query = query.filter(func.lower(Expense.category) == category.strip().lower())

        if date_from:
            query = query.filter(Expense.expense_date >= date_from)

        if date_to:
            query = query.filter(Expense.expense_date <= date_to)

        total = query.count()
        items = query.order_by(Expense.created_at.desc()).offset(skip).limit(limit).all()
        return items, total

    def sum_expenses_by_method(
        self,
        payment_method: Optional[PaymentMethodEnum] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> float:
        query = self.db.query(func.coalesce(func.sum(Expense.amount), 0.0))
        if payment_method:
            query = query.filter(Expense.payment_method == payment_method)
        if date_from:
            query = query.filter(Expense.expense_date >= date_from)
        if date_to:
            query = query.filter(Expense.expense_date <= date_to)
        return float(query.scalar() or 0.0)

from datetime import datetime, timedelta, timezone
from typing import Dict, List

from sqlalchemy import Date, cast, desc, func
from sqlalchemy.orm import Session

from app.models.enums import (
    InventoryCategoryEnum,
    InventoryTxnTypeEnum,
    OrderStatusEnum,
)
from app.models.expense import Expense
from app.models.inventory import InventoryItem, InventoryTransaction
from app.models.ledger_entry import LedgerEntry
from app.models.order import Order
from app.models.student import Student


class AnalyticsRepository:
    def get_orders_by_status(self, db: Session) -> List[Dict]:
        results = (
            db.query(Order.status, func.count(Order.id)).group_by(Order.status).all()
        )
        return [
            {
                "label": str(r[0].value if hasattr(r[0], "value") else r[0]),
                "value": r[1],
            }
            for r in results
        ]

    def get_orders_by_department(self, db: Session) -> List[Dict]:
        results = (
            db.query(Student.department, func.count(Order.id))
            .join(Order, Student.id == Order.student_id)
            .group_by(Student.department)
            .order_by(desc(func.count(Order.id)))
            .limit(10)
            .all()
        )
        return [{"label": r[0], "value": r[1]} for r in results]

    def get_daily_revenue(self, db: Session, days: int = 30) -> List[Dict]:
        start_date = datetime.now(timezone.utc) - timedelta(days=days)
        results = (
            db.query(
                cast(LedgerEntry.created_at, Date).label("d"),
                func.sum(LedgerEntry.amount),
            )
            .filter(LedgerEntry.amount > 0, LedgerEntry.created_at >= start_date)
            .group_by("d")
            .order_by("d")
            .all()
        )
        return [{"label": str(r[0]), "value": float(r[1])} for r in results]

    def get_monthly_revenue(self, db: Session, months: int = 12) -> List[Dict]:
        # Using string manipulation for YYYY-MM is tricky cross-db.
        # A simpler cross-db approach for month truncation is to fetch dates and group in python if necessary,
        # or use extract('year') and extract('month').
        from sqlalchemy import extract

        start_date = datetime.now(timezone.utc) - timedelta(days=30 * months)
        results = (
            db.query(
                extract("year", LedgerEntry.created_at).label("y"),
                extract("month", LedgerEntry.created_at).label("m"),
                func.sum(LedgerEntry.amount),
            )
            .filter(LedgerEntry.amount > 0, LedgerEntry.created_at >= start_date)
            .group_by("y", "m")
            .order_by("y", "m")
            .all()
        )
        return [
            {"label": f"{int(r[0])}-{int(r[1]):02d}", "value": float(r[2])}
            for r in results
        ]

    def get_binding_type_usage(self, db: Session) -> List[Dict]:
        results = (
            db.query(Order.binding_type, func.count(Order.id))
            .group_by(Order.binding_type)
            .all()
        )
        return [
            {
                "label": str(r[0].value if hasattr(r[0], "value") else r[0]),
                "value": r[1],
            }
            for r in results
        ]

    def get_color_vs_bw(self, db: Session) -> List[Dict]:
        results = (
            db.query(Order.color_mode, func.count(Order.id))
            .group_by(Order.color_mode)
            .all()
        )
        return [
            {
                "label": str(r[0].value if hasattr(r[0], "value") else r[0]),
                "value": r[1],
            }
            for r in results
        ]

    def get_most_active_students(self, db: Session) -> List[Dict]:
        results = (
            db.query(Student.full_name, func.count(Order.id))
            .join(Order, Student.id == Order.student_id)
            .group_by(Student.id)
            .order_by(desc(func.count(Order.id)))
            .limit(10)
            .all()
        )
        return [{"label": r[0], "value": r[1]} for r in results]

    def get_expense_breakdown(self, db: Session) -> List[Dict]:
        results = (
            db.query(Expense.category, func.sum(Expense.amount))
            .group_by(Expense.category)
            .all()
        )
        return [{"label": r[0], "value": float(r[1])} for r in results]

    def get_inventory_consumption(self, db: Session) -> List[Dict]:
        results = (
            db.query(
                InventoryItem.item_name, func.sum(InventoryTransaction.quantity_change)
            )
            .join(
                InventoryTransaction, InventoryItem.id == InventoryTransaction.item_id
            )
            .filter(
                InventoryTransaction.transaction_type
                == InventoryTxnTypeEnum.CONSUMPTION
            )
            .group_by(InventoryItem.item_name)
            .order_by(func.sum(InventoryTransaction.quantity_change))
            .all()
        )
        return [{"label": r[0], "value": float(abs(r[1]))} for r in results]

    def get_average_order_value(self, db: Session) -> float:
        val = db.query(func.avg(Order.total_price)).scalar()
        return float(val) if val else 0.0

    def get_average_pages_per_order(self, db: Session) -> float:
        val = db.query(func.avg(Order.page_count * Order.copies)).scalar()
        return float(val) if val else 0.0

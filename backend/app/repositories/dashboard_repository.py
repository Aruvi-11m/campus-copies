from datetime import datetime, timezone
from typing import Dict
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.order import Order
from app.models.ledger_entry import LedgerEntry
from app.models.student import Student
from app.models.file import OrderFile
from app.models.inventory import InventoryItem
from app.models.enums import OrderStatusEnum

class DashboardRepository:
    def get_dashboard_stats(self, db: Session) -> Dict:
        now = datetime.now(timezone.utc)
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Orders
        total_orders = db.query(func.count(Order.id)).scalar() or 0
        today_orders = db.query(func.count(Order.id)).filter(Order.created_at >= start_of_day).scalar() or 0
        pending_orders = db.query(func.count(Order.id)).filter(Order.status == OrderStatusEnum.PENDING_PAYMENT).scalar() or 0
        printing_orders = db.query(func.count(Order.id)).filter(Order.status == OrderStatusEnum.PRINTING).scalar() or 0
        ready_orders = db.query(func.count(Order.id)).filter(Order.status == OrderStatusEnum.READY_FOR_PICKUP).scalar() or 0
        completed_orders = db.query(func.count(Order.id)).filter(Order.status == OrderStatusEnum.COMPLETED).scalar() or 0

        # Revenue & Expenses (from LedgerEntry)
        total_revenue = db.query(func.sum(LedgerEntry.amount)).filter(LedgerEntry.amount > 0).scalar() or 0.0
        today_revenue = db.query(func.sum(LedgerEntry.amount)).filter(LedgerEntry.amount > 0, LedgerEntry.created_at >= start_of_day).scalar() or 0.0
        monthly_revenue = db.query(func.sum(LedgerEntry.amount)).filter(LedgerEntry.amount > 0, LedgerEntry.created_at >= start_of_month).scalar() or 0.0
        
        # Cash Balance
        cash_balance = db.query(func.sum(LedgerEntry.amount)).filter(LedgerEntry.entry_type.like('%_CASH')).scalar() or 0.0
        
        total_expenses = db.query(func.sum(LedgerEntry.amount)).filter(LedgerEntry.amount < 0).scalar() or 0.0
        net_profit = float(total_revenue) + float(total_expenses)

        # Students
        total_students = db.query(func.count(Student.id)).scalar() or 0
        active_students = db.query(func.count(func.distinct(Order.student_id))).scalar() or 0

        # Files and Pages
        total_files = db.query(func.count(OrderFile.id)).scalar() or 0
        total_pages = db.query(func.sum(Order.page_count * Order.copies)).filter(Order.status == OrderStatusEnum.COMPLETED).scalar() or 0

        # Inventory
        inventory_value = db.query(func.sum(InventoryItem.current_stock * InventoryItem.unit_cost)).scalar() or 0.0
        low_stock_count = db.query(func.count(InventoryItem.id)).filter(InventoryItem.current_stock <= InventoryItem.low_stock_threshold).scalar() or 0

        return {
            "total_orders": total_orders,
            "today_orders": today_orders,
            "pending_orders": pending_orders,
            "printing_orders": printing_orders,
            "ready_orders": ready_orders,
            "completed_orders": completed_orders,
            "total_revenue": float(total_revenue),
            "today_revenue": float(today_revenue),
            "monthly_revenue": float(monthly_revenue),
            "cash_balance": float(cash_balance),
            "total_expenses": float(abs(total_expenses)),
            "net_profit": float(net_profit),
            "total_students": total_students,
            "active_students": active_students,
            "total_files_uploaded": total_files,
            "total_pages_printed": int(total_pages),
            "inventory_value": float(inventory_value),
            "low_stock_count": low_stock_count
        }

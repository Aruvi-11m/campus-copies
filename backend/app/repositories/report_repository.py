from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.student import Student
from app.models.ledger_entry import LedgerEntry
from app.models.expense import Expense
from app.models.inventory import InventoryItem

class ReportRepository:
    def get_orders_report(self, db: Session, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None, status: Optional[str] = None, department: Optional[str] = None) -> List[Dict]:
        query = db.query(
            Order.display_id, Order.status, Order.total_price, Order.created_at,
            Student.full_name.label("student_name"), Student.department
        ).join(Student, Order.student_id == Student.id)
        
        if start_date:
            query = query.filter(Order.created_at >= start_date)
        if end_date:
            query = query.filter(Order.created_at <= end_date)
        if status:
            query = query.filter(Order.status == status)
        if department:
            query = query.filter(Student.department == department)
            
        query = query.order_by(desc(Order.created_at))
        return [dict(row._mapping) for row in query.all()]
        
    def get_payments_report(self, db: Session, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[Dict]:
        query = db.query(
            LedgerEntry.id, LedgerEntry.entry_type, LedgerEntry.amount, LedgerEntry.created_at,
            LedgerEntry.description, Order.display_id
        ).outerjoin(Order, LedgerEntry.order_id == Order.id).filter(LedgerEntry.amount > 0)
        
        if start_date:
            query = query.filter(LedgerEntry.created_at >= start_date)
        if end_date:
            query = query.filter(LedgerEntry.created_at <= end_date)
            
        query = query.order_by(desc(LedgerEntry.created_at))
        return [dict(row._mapping) for row in query.all()]
        
    def get_expenses_report(self, db: Session, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[Dict]:
        query = db.query(
            Expense.id, Expense.category, Expense.amount, Expense.payment_method, Expense.description, Expense.expense_date
        )
        if start_date:
            query = query.filter(Expense.expense_date >= start_date.date())
        if end_date:
            query = query.filter(Expense.expense_date <= end_date.date())
        query = query.order_by(desc(Expense.expense_date))
        return [dict(row._mapping) for row in query.all()]
        
    def get_inventory_report(self, db: Session) -> List[Dict]:
        query = db.query(
            InventoryItem.item_name.label("name"), InventoryItem.category, InventoryItem.current_stock, 
            InventoryItem.unit_cost, InventoryItem.min_threshold.label("low_stock_threshold")
        ).order_by(InventoryItem.item_name)
        return [dict(row._mapping) for row in query.all()]

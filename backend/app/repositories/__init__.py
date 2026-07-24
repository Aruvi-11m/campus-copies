"""
Campus Copies ERP - Repositories Package Root
"""

from app.repositories.admin_repository import AdminRepository
from app.repositories.audit_repository import AuditRepository
from app.repositories.base import BaseRepository
from app.repositories.expense_repository import ExpenseRepository
from app.repositories.file_repository import FileRepository
from app.repositories.inventory_repository import (
    InventoryItemRepository,
    InventoryTransactionRepository,
)
from app.repositories.ledger_repository import LedgerRepository
from app.repositories.notification_repository import NotificationRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.payment_repository import PaymentRepository
from app.repositories.session_repository import SessionRepository
from app.repositories.setting_repository import SettingRepository
from app.repositories.student_repository import StudentRepository

__all__ = [
    "BaseRepository",
    "StudentRepository",
    "AdminRepository",
    "SessionRepository",
    "FileRepository",
    "OrderRepository",
    "PaymentRepository",
    "ExpenseRepository",
    "LedgerRepository",
    "SettingRepository",
    "AuditRepository",
    "NotificationRepository",
    "InventoryItemRepository",
    "InventoryTransactionRepository",
]

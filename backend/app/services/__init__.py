"""
Campus Copies ERP - Services Package Root
"""

from app.services.auth_service import AuthService
from app.services.order_service import OrderService
from app.services.pricing_service import PricingService
from app.services.storage_service import StorageService
from app.services.finance_service import FinanceService
from app.services.inventory_service import InventoryService

__all__ = [
    "AuthService",
    "StorageService",
    "PricingService",
    "OrderService",
    "FinanceService",
    "InventoryService",
]

"""
Campus Copies ERP - API V1 Router Aggregator

Grounding: docs/BackendSpecification.md §1
"""

from fastapi import APIRouter
from app.api.v1.admin_orders import router as admin_orders_router
from app.api.v1.auth import router as auth_router
from app.api.v1.expenses import router as expenses_router
from app.api.v1.files import router as files_router
from app.api.v1.inventory import router as inventory_router
from app.api.v1.orders import router as orders_router
from app.api.v1.payments import router as payments_router
from app.api.v1.students import router as students_router

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(auth_router)
api_v1_router.include_router(files_router)
api_v1_router.include_router(orders_router)
api_v1_router.include_router(admin_orders_router)
api_v1_router.include_router(students_router)
api_v1_router.include_router(payments_router)
api_v1_router.include_router(expenses_router)
api_v1_router.include_router(inventory_router, prefix="/inventory", tags=["inventory"])

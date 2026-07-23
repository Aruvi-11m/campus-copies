"""
Campus Copies ERP - API V1 Router Aggregator

Grounding: docs/BackendSpecification.md §1
"""

from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.students import router as students_router

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(auth_router)
api_v1_router.include_router(students_router)

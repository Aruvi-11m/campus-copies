"""
Campus Copies ERP - Services Package Root
"""

from app.services.auth_service import AuthService
from app.services.storage_service import StorageService

__all__ = ["AuthService", "StorageService"]

"""
Campus Copies ERP - Schemas Package Root
"""

from app.schemas.auth import (
    AdminAuthResponse,
    AdminLoginRequest,
    AdminResponse,
    StudentAuthResponse,
    StudentLoginRequest,
    StudentProfileResponse,
    StudentResponse,
    TokenPayload,
)

__all__ = [
    "StudentLoginRequest",
    "StudentResponse",
    "StudentAuthResponse",
    "StudentProfileResponse",
    "AdminLoginRequest",
    "AdminResponse",
    "AdminAuthResponse",
    "TokenPayload",
]

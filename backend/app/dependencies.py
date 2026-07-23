"""
Campus Copies ERP - FastAPI Authentication & Authorization Dependencies

FastAPI security dependencies for JWT token extraction, role verification, and ownership checks.
Grounding: docs/BackendSpecification.md §3, docs/SecuritySpecification.md §3
"""

import uuid
from typing import Dict, Optional, Union
from fastapi import Depends, Query, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.errors import AuthenticationError, PermissionDeniedError
from app.core.security import decode_jwt_token
from app.database import get_db
from app.models.admin import Admin
from app.models.student import Student
from app.repositories.admin_repository import AdminRepository
from app.repositories.student_repository import StudentRepository

# Optional HTTPBearer instance (auto_error=False to allow fallback query parameter)
security_bearer = HTTPBearer(auto_error=False)


def extract_token_from_request(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer),
    token_query: Optional[str] = Query(None, alias="token"),
) -> str:
    """
    Extracts JWT token string from HTTP Authorization Bearer header or token query parameter.
    """
    if credentials and credentials.credentials:
        return credentials.credentials
    if token_query and token_query.strip():
        return token_query.strip()
    raise AuthenticationError("Authentication token is missing")


def get_current_token_payload(token: str = Depends(extract_token_from_request)) -> Dict:
    """
    Decodes JWT token and returns payload dictionary.
    Raises AuthenticationError if invalid or expired.
    """
    return decode_jwt_token(token)


def get_current_user(
    payload: Dict = Depends(get_current_token_payload),
    db: Session = Depends(get_db),
) -> Union[Student, Admin]:
    """
    Retrieves current authenticated Student or Admin model instance based on JWT claims.
    """
    sub_id_str = payload.get("sub")
    role = payload.get("role")

    if not sub_id_str or not role:
        raise AuthenticationError("Invalid token claims payload")

    try:
        user_uuid = uuid.UUID(sub_id_str)
    except ValueError:
        raise AuthenticationError("Invalid user ID in token claim")

    if role == "student":
        student_repo = StudentRepository(db)
        student = student_repo.get_by_id(user_uuid)
        if not student or student.is_deleted:
            raise AuthenticationError("Student account not found or has been deactivated")
        return student

    elif role == "admin":
        admin_repo = AdminRepository(db)
        admin = admin_repo.get_by_id(user_uuid)
        if not admin:
            raise AuthenticationError("Admin account not found")
        if not admin.is_active:
            raise PermissionDeniedError("Admin account has been disabled")
        return admin

    else:
        raise AuthenticationError(f"Unknown user role '{role}' in token")


def require_student(user: Union[Student, Admin] = Depends(get_current_user)) -> Student:
    """
    FastAPI dependency requiring an authenticated Student user.
    """
    if not isinstance(user, Student):
        raise PermissionDeniedError("Student role access required for this operation")
    return user


def require_admin(user: Union[Student, Admin] = Depends(get_current_user)) -> Admin:
    """
    FastAPI dependency requiring an active authenticated Admin user.
    """
    if not isinstance(user, Admin):
        raise PermissionDeniedError("Admin role access required for this operation")
    if not user.is_active:
        raise PermissionDeniedError("Admin account has been disabled")
    return user


def verify_student_ownership(current_student: Student, target_student_id: uuid.UUID) -> None:
    """
    Helper function to enforce horizontal privilege isolation.
    Ensures student can only view/modify their own resources.
    """
    if current_student.id != target_student_id:
        raise PermissionDeniedError("Access denied: You do not own this resource")

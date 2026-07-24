"""
Campus Copies ERP - Authentication API Endpoints

Handlers for Student auto-registration/login and Admin authentication.
Grounding: docs/API.md §3.1, §4.1, docs/BackendSpecification.md §3
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth import (
    AdminAuthResponse,
    AdminLoginRequest,
    StudentAuthResponse,
    StudentLoginRequest,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])
limiter = Limiter(key_func=get_remote_address)


def build_success_response(
    data: dict, status_code: int = status.HTTP_200_OK
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "success": True,
            "data": data,
            "error": None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


@router.post(
    "/student/login",
    response_model=StudentAuthResponse,
    status_code=status.HTTP_200_OK,
    summary="Student Login / Auto-Registration",
)
@limiter.limit("10/minute")
async def student_login(
    request: Request,
    body: StudentLoginRequest,
    db: Session = Depends(get_db),
) -> JSONResponse:
    """
    Authenticates a student by Name, Mobile, and Department.
    Auto-registers if new student; updates and logs in if existing student.
    """
    service = AuthService(db)
    result: StudentAuthResponse = service.student_login(body)
    return build_success_response(result.model_dump(mode="json"))


@router.post(
    "/admin/login",
    response_model=AdminAuthResponse,
    status_code=status.HTTP_200_OK,
    summary="Admin Login",
)
@limiter.limit("5/minute")
async def admin_login(
    request: Request,
    body: AdminLoginRequest,
    db: Session = Depends(get_db),
) -> JSONResponse:
    """
    Authenticates a shop admin using Username and Password.
    Verifies bcrypt hash and active status; issues 8-hour Admin JWT.
    """
    client_ip = request.client.host if request.client else "127.0.0.1"
    user_agent = request.headers.get("user-agent")

    service = AuthService(db)
    result: AdminAuthResponse = service.admin_login(
        request=body,
        ip_address=client_ip,
        user_agent=user_agent,
    )
    return build_success_response(result.model_dump(mode="json"))

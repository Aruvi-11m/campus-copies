"""
Campus Copies ERP - Authentication Service

Business logic for Student auto-registration/login and Admin authentication.
Grounding: docs/BackendSpecification.md §3, §4, docs/SecuritySpecification.md §2
"""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional
from sqlalchemy.orm import Session

from app.config import settings
from app.core.errors import AuthenticationError, ConflictError, PermissionDeniedError
from app.core.logging import logger
from app.core.security import create_jwt_token, hash_password, verify_password
from app.models.admin import Admin
from app.models.student import Student
from app.repositories.admin_repository import AdminRepository
from app.repositories.session_repository import SessionRepository
from app.repositories.student_repository import StudentRepository
from app.services.dashboard_service import invalidate_dashboard_cache
from app.schemas.auth import (
    AdminAuthResponse,
    AdminLoginRequest,
    AdminResponse,
    StudentAuthResponse,
    StudentLoginRequest,
    StudentResponse,
)


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.student_repo = StudentRepository(db)
        self.admin_repo = AdminRepository(db)
        self.session_repo = SessionRepository(db)

    def student_login(self, request: StudentLoginRequest) -> StudentAuthResponse:
        """
        Student login or auto-registration flow.
        Auto-registers if new student; logs in existing student if found.
        """
        student = self.student_repo.get_by_mobile(request.mobile)

        if student:
            # Update profile details if updated
            student = self.student_repo.update_profile(
                student=student,
                full_name=request.full_name,
                department=request.department,
            )
            logger.info("student_logged_in", student_id=str(student.id), mobile=student.mobile)
        else:
            # Auto-register new student
            student = self.student_repo.create(
                mobile=request.mobile,
                full_name=request.full_name,
                department=request.department,
            )
            invalidate_dashboard_cache()
            logger.info("student_registered", student_id=str(student.id), mobile=student.mobile)

        # Generate 24-hour Student JWT
        expires_delta = timedelta(hours=settings.STUDENT_TOKEN_EXPIRE_HOURS)
        token_claims = {
            "sub": str(student.id),
            "mobile": student.mobile,
            "role": "student",
        }
        token = create_jwt_token(token_claims, expires_delta=expires_delta)

        return StudentAuthResponse(
            token=token,
            student=StudentResponse.model_validate(student),
        )

    def admin_login(
        self,
        request: AdminLoginRequest,
        ip_address: str = "127.0.0.1",
        user_agent: Optional[str] = None,
    ) -> AdminAuthResponse:
        """
        Admin login flow using username and bcrypt password verification.
        Enforces active account checks and creates a session log.
        """
        admin = self.admin_repo.get_by_username(request.username)

        if not admin:
            logger.warning("admin_login_failed_non_existent", username=request.username)
            raise AuthenticationError("Invalid username or password")

        if not admin.is_active:
            logger.warning("admin_login_failed_disabled_account", username=request.username)
            raise PermissionDeniedError("Admin account has been disabled")

        if not verify_password(request.password, admin.password_hash):
            logger.warning("admin_login_failed_invalid_password", username=request.username)
            raise AuthenticationError("Invalid username or password")

        # Generate 8-hour Admin JWT
        jti = str(uuid.uuid4())
        expires_delta = timedelta(hours=settings.ADMIN_TOKEN_EXPIRE_HOURS)
        token_claims = {
            "sub": str(admin.id),
            "username": admin.username,
            "role": "admin",
            "jti": jti,
        }
        token = create_jwt_token(token_claims, expires_delta=expires_delta)

        # Create session record
        expires_at = datetime.now(timezone.utc) + expires_delta
        self.session_repo.create_session(
            admin_id=admin.id,
            jwt_jti=jti,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=expires_at,
        )

        logger.info("admin_logged_in", admin_id=str(admin.id), username=admin.username)

        return AdminAuthResponse(
            token=token,
            admin=AdminResponse.model_validate(admin),
        )

    def bootstrap_initial_admin(
        self,
        username: str,
        password: str,
        full_name: str,
        setup_key: str,
    ) -> AdminResponse:
        """
        Initial admin bootstrap setup method using ADMIN_SETUP_KEY.
        Enforces maximum 3 active admins limit.
        """
        if setup_key != settings.ADMIN_SETUP_KEY:
            raise PermissionDeniedError("Invalid admin bootstrap setup key")

        active_count = self.admin_repo.count_active_admins()
        if active_count >= 3:
            raise ConflictError("Maximum 3 active administrators allowed")

        existing = self.admin_repo.get_by_username(username)
        if existing:
            raise ConflictError("Admin account with this username already exists")

        password_hashed = hash_password(password)
        admin = self.admin_repo.create(
            username=username,
            password_hash=password_hashed,
            full_name=full_name,
            is_active=True,
        )

        logger.info("admin_bootstrapped", admin_id=str(admin.id), username=admin.username)
        return AdminResponse.model_validate(admin)

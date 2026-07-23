"""
Campus Copies ERP - Phase 3 Authentication & Authorization Test Suite

Comprehensive tests for Student Auth, Admin Auth, JWT Infrastructure, and Role Authorization.
Grounding: docs/TestingSpecification.md §4.1, §6, §9
"""

import pytest
from datetime import timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.errors import AuthenticationError, PermissionDeniedError
from app.core.security import create_jwt_token, decode_jwt_token, hash_password, verify_password
from app.models.admin import Admin
from app.models.student import Student
from app.repositories.admin_repository import AdminRepository
from app.repositories.student_repository import StudentRepository
from app.schemas.auth import AdminLoginRequest, StudentLoginRequest
from app.services.auth_service import AuthService


# ============================================================================
# 1. STUDENT AUTHENTICATION TESTS
# ============================================================================

def test_student_auto_registration(db_session: Session, client: TestClient):
    """Test new student auto-registration via POST /api/v1/auth/student/login."""
    payload = {
        "mobile": "9876543210",
        "full_name": "Arun Kumar",
        "department": "CSE",
    }
    response = client.post("/api/v1/auth/student/login", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True
    assert "token" in data["data"]
    assert data["data"]["student"]["mobile"] == "9876543210"
    assert data["data"]["student"]["full_name"] == "Arun Kumar"
    assert data["data"]["student"]["department"] == "CSE"

    # Verify student record created in database
    student_repo = StudentRepository(db_session)
    student = student_repo.get_by_mobile("9876543210")
    assert student is not None
    assert student.full_name == "Arun Kumar"


def test_student_existing_login(db_session: Session, client: TestClient):
    """Test existing student login updates profile if details change."""
    student_repo = StudentRepository(db_session)
    student_repo.create(mobile="9876543210", full_name="Arun Kumar", department="CSE")

    payload = {
        "mobile": "9876543210",
        "full_name": "Arun Kumar Updated",
        "department": "IT",
    }
    response = client.post("/api/v1/auth/student/login", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["data"]["student"]["full_name"] == "Arun Kumar Updated"
    assert data["data"]["student"]["department"] == "IT"


def test_student_invalid_mobile_validation(client: TestClient):
    """Test invalid Indian mobile numbers return 422 Unprocessable Entity."""
    invalid_mobiles = ["12345", "1234567890", "5999999999", "abcdefghij"]
    for mobile in invalid_mobiles:
        payload = {"mobile": mobile, "full_name": "Test User", "department": "CSE"}
        response = client.post("/api/v1/auth/student/login", json=payload)
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "VALIDATION_ERROR"


def test_student_invalid_department_validation(client: TestClient):
    """Test empty department or name returns 422 Validation Error."""
    payload = {"mobile": "9876543210", "full_name": "   ", "department": "CSE"}
    response = client.post("/api/v1/auth/student/login", json=payload)
    assert response.status_code == 422


# ============================================================================
# 2. ADMIN AUTHENTICATION TESTS
# ============================================================================

def test_admin_valid_login(db_session: Session, client: TestClient):
    """Test valid admin login returns token and admin data."""
    admin_repo = AdminRepository(db_session)
    admin_repo.create(
        username="shopowner",
        password_hash=hash_password("SecurePassword123!"),
        full_name="Senior Operator",
        is_active=True,
    )

    payload = {
        "username": "shopowner",
        "password": "SecurePassword123!",
    }
    response = client.post("/api/v1/auth/admin/login", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True
    assert "token" in data["data"]
    assert data["data"]["admin"]["username"] == "shopowner"
    assert data["data"]["admin"]["full_name"] == "Senior Operator"


def test_admin_invalid_password(db_session: Session, client: TestClient):
    """Test admin login with wrong password returns 401 Unauthorized."""
    admin_repo = AdminRepository(db_session)
    admin_repo.create(
        username="shopowner",
        password_hash=hash_password("CorrectPassword"),
        full_name="Operator",
    )

    payload = {"username": "shopowner", "password": "WrongPassword"}
    response = client.post("/api/v1/auth/admin/login", json=payload)
    assert response.status_code == 401
    data = response.json()
    assert data["error"]["code"] == "UNAUTHORIZED"


def test_admin_disabled_account(db_session: Session, client: TestClient):
    """Test login attempt by disabled admin returns 403 Forbidden."""
    admin_repo = AdminRepository(db_session)
    admin_repo.create(
        username="disabledadmin",
        password_hash=hash_password("Password123"),
        full_name="Disabled Operator",
        is_active=False,
    )

    payload = {"username": "disabledadmin", "password": "Password123"}
    response = client.post("/api/v1/auth/admin/login", json=payload)
    assert response.status_code == 403
    data = response.json()
    assert data["error"]["code"] == "FORBIDDEN"


def test_admin_non_existent_account(client: TestClient):
    """Test login with non-existent admin username returns 401 Unauthorized."""
    payload = {"username": "unknownuser", "password": "Password123"}
    response = client.post("/api/v1/auth/admin/login", json=payload)
    assert response.status_code == 401


def test_password_hashing_rounds():
    """Verify password hashing generates valid bcrypt hash."""
    plain = "TestPassword123"
    hashed = hash_password(plain)
    assert hashed.startswith("$2b$") or hashed.startswith("$2a$")
    assert verify_password(plain, hashed) is True


# ============================================================================
# 3. JWT INFRASTRUCTURE TESTS
# ============================================================================

def test_jwt_encoding_decoding():
    """Verify JWT token encoding and payload decoding."""
    claims = {"sub": "user-uuid", "role": "student", "mobile": "9876543210"}
    token = create_jwt_token(claims, expires_delta=timedelta(hours=1))

    decoded = decode_jwt_token(token)
    assert decoded["sub"] == "user-uuid"
    assert decoded["role"] == "student"
    assert decoded["mobile"] == "9876543210"


def test_jwt_expiration():
    """Verify expired JWT token raises AuthenticationError."""
    claims = {"sub": "user-uuid", "role": "student"}
    token = create_jwt_token(claims, expires_delta=timedelta(seconds=-10))

    with pytest.raises(AuthenticationError) as exc_info:
        decode_jwt_token(token)
    assert "expired" in str(exc_info.value).lower()


def test_jwt_invalid_signature():
    """Verify tampering with JWT signature causes decode failure."""
    claims = {"sub": "user-uuid", "role": "student"}
    token = create_jwt_token(claims)
    tampered_token = token[:-5] + "XXXXX"

    with pytest.raises(AuthenticationError):
        decode_jwt_token(tampered_token)


# ============================================================================
# 4. AUTHORIZATION & ROUTE GUARD TESTS
# ============================================================================

def test_student_get_profile_success(db_session: Session, client: TestClient):
    """Test GET /api/v1/students/me with valid Student JWT token."""
    student_repo = StudentRepository(db_session)
    student = student_repo.create(mobile="9876543210", full_name="Arun Kumar", department="CSE")

    token = create_jwt_token({"sub": str(student.id), "role": "student", "mobile": student.mobile})

    response = client.get(
        "/api/v1/students/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["mobile"] == "9876543210"
    assert data["data"]["full_name"] == "Arun Kumar"
    assert data["data"]["department"] == "CSE"


def test_student_get_profile_unauthorized_missing_token(client: TestClient):
    """Test GET /api/v1/students/me without Authorization header returns 401."""
    response = client.get("/api/v1/students/me")
    assert response.status_code == 401
    data = response.json()
    assert data["error"]["code"] == "UNAUTHORIZED"


def test_student_route_accessed_by_admin_forbidden(db_session: Session, client: TestClient):
    """Test accessing Student profile endpoint with Admin JWT returns 403 Forbidden."""
    admin_repo = AdminRepository(db_session)
    admin = admin_repo.create(
        username="shopadmin",
        password_hash=hash_password("Pass123"),
        full_name="Shop Admin",
    )

    admin_token = create_jwt_token({"sub": str(admin.id), "role": "admin", "username": admin.username})

    response = client.get(
        "/api/v1/students/me",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 403
    data = response.json()
    assert data["error"]["code"] == "FORBIDDEN"


def test_query_param_token_authentication(db_session: Session, client: TestClient):
    """Test query parameter token authentication (?token=<jwt>) for GET endpoints."""
    student_repo = StudentRepository(db_session)
    student = student_repo.create(mobile="9876543210", full_name="Arun", department="ECE")

    token = create_jwt_token({"sub": str(student.id), "role": "student", "mobile": student.mobile})

    response = client.get(f"/api/v1/students/me?token={token}")
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["mobile"] == "9876543210"


def test_404_not_found_endpoint(client: TestClient):
    """Test non-existent endpoint returns 404 Not Found."""
    response = client.get("/api/v1/nonexistent/path")
    assert response.status_code == 404

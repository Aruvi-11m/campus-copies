"""
Campus Copies ERP - Phase 1 Foundation Unit Tests

Tests configuration, password security, JWT generation, error handlers, and health check.
"""

import pytest
from datetime import timedelta
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import hash_password, verify_password, create_jwt_token, decode_jwt_token
from app.core.errors import AuthenticationError, PermissionDeniedError, NotFoundError

client = TestClient(app)


def test_password_hashing_and_verification():
    """Verify pwdlib bcrypt hashing and password verification."""
    password = "SuperSecretPassword123!"
    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_jwt_creation_and_decoding():
    """Verify PyJWT HS256 token creation and decoding."""
    payload = {"sub": "student-uuid-123", "role": "student", "mobile": "9876543210"}
    token = create_jwt_token(payload, expires_delta=timedelta(hours=1))

    decoded = decode_jwt_token(token)
    assert decoded["sub"] == "student-uuid-123"
    assert decoded["role"] == "student"
    assert decoded["mobile"] == "9876543210"
    assert "exp" in decoded
    assert "iat" in decoded


def test_expired_jwt_decoding():
    """Verify expired JWT token raises AuthenticationError."""
    payload = {"sub": "expired-user"}
    token = create_jwt_token(payload, expires_delta=timedelta(seconds=-10))

    with pytest.raises(AuthenticationError):
        decode_jwt_token(token)


def test_health_check_endpoint():
    """Verify GET /api/health endpoint structure."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "service" in data
    assert "version" in data
    assert "timestamp" in data

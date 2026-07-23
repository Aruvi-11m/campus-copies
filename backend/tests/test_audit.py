import pytest
from fastapi.testclient import TestClient
from app.models.admin import Admin
from app.core.security import create_jwt_token

@pytest.fixture
def admin_token_headers(db_session):
    admin = Admin(username="testadmin", full_name="Test Admin", password_hash="hash", is_active=True)
    db_session.add(admin)
    db_session.commit()
    token = create_jwt_token({"sub": str(admin.id), "username": admin.username, "role": "admin"})
    return {"Authorization": f"Bearer {token}"}

def test_get_audit_logs(client: TestClient, admin_token_headers):
    response = client.get("/api/v1/admin/audit", headers=admin_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data

def test_get_audit_log_not_found(client: TestClient, admin_token_headers):
    response = client.get("/api/v1/admin/audit/999999", headers=admin_token_headers)
    assert response.status_code == 404

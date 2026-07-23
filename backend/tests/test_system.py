import pytest
from fastapi.testclient import TestClient
from app.models.admin import Admin
from app.models.student import Student
from app.core.security import create_jwt_token

@pytest.fixture
def admin_token_headers(db_session):
    admin = Admin(username="testadmin_sys", full_name="Test Admin", password_hash="hash", is_active=True)
    db_session.add(admin)
    db_session.commit()
    token = create_jwt_token({"sub": str(admin.id), "username": admin.username, "role": "admin"})
    return {"Authorization": f"Bearer {token}"}

def test_system_health(client: TestClient, admin_token_headers):
    response = client.get("/api/v1/admin/system/health", headers=admin_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "active"
    assert "database_status" in data

def test_system_backup(client: TestClient, admin_token_headers):
    response = client.get("/api/v1/admin/system/backup", headers=admin_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert "schema_version" in data
    assert "last_backup_timestamp" in data

def test_system_version(client: TestClient, admin_token_headers):
    response = client.get("/api/v1/admin/system/version", headers=admin_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["application_version"] == "1.0.0"

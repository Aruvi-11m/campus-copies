import pytest
from fastapi.testclient import TestClient
from app.models.admin import Admin
from app.core.security import create_jwt_token

@pytest.fixture
def admin_token_headers(db_session):
    admin = Admin(username="testadmin_set", full_name="Test Admin", password_hash="hash", is_active=True)
    db_session.add(admin)
    db_session.commit()
    token = create_jwt_token({"sub": str(admin.id), "username": admin.username, "role": "admin"})
    return {"Authorization": f"Bearer {token}"}

def test_get_settings(client: TestClient, admin_token_headers):
    response = client.get("/api/v1/admin/settings", headers=admin_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert "bw_single_side" in data
    assert "maintenance_mode" in data

def test_update_settings(client: TestClient, admin_token_headers):
    response = client.patch(
        "/api/v1/admin/settings",
        headers=admin_token_headers,
        json={"maintenance_mode": True, "bw_single_side": 2.0}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["maintenance_mode"] is True
    assert data["bw_single_side"] == 2.0

def test_reset_settings(client: TestClient, admin_token_headers):
    response = client.post("/api/v1/admin/settings/reset", headers=admin_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["maintenance_mode"] is False
    assert data["bw_single_side"] == 1.50

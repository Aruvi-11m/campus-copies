import pytest
from fastapi.testclient import TestClient
from app.models.admin import Admin
from app.models.student import Student
from app.core.security import create_jwt_token

@pytest.fixture
def admin_token_headers(db_session):
    admin = Admin(username="testadmin_notif", full_name="Test Admin", password_hash="hash", is_active=True)
    db_session.add(admin)
    db_session.commit()
    token = create_jwt_token({"sub": str(admin.id), "username": admin.username, "role": "admin"})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def student_token_headers(db_session):
    student = Student(mobile="1234567890", full_name="Test Student", department="CSE")
    db_session.add(student)
    db_session.commit()
    token = create_jwt_token({"sub": str(student.id), "mobile": student.mobile, "role": "student"})
    return {"Authorization": f"Bearer {token}"}

def test_admin_notifications(client: TestClient, admin_token_headers):
    notif_data = {
        "target_user": "ADMIN",
        "type": "INFO",
        "event_type": "test_event",
        "title": "Test Title",
        "message": "Test Message"
    }
    response = client.post("/api/v1/admin/notifications", json=notif_data, headers=admin_token_headers)
    assert response.status_code == 200
    created = response.json()
    assert created["title"] == "Test Title"
    
    notif_id = created["id"]
    
    response = client.get("/api/v1/admin/notifications", headers=admin_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) >= 1
    
    response = client.patch(f"/api/v1/admin/notifications/{notif_id}", json={"is_read": True}, headers=admin_token_headers)
    assert response.status_code == 200
    assert response.json()["is_read"] is True
    
    response = client.delete(f"/api/v1/admin/notifications/{notif_id}", headers=admin_token_headers)
    assert response.status_code == 200

def test_student_notifications(client: TestClient, student_token_headers):
    response = client.get("/api/v1/students/notifications", headers=student_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data

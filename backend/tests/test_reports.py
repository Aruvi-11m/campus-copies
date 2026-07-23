import pytest
from datetime import datetime, timedelta, timezone
from app.core.security import create_jwt_token
from app.models.admin import Admin

@pytest.fixture
def admin_token_headers(db_session):
    admin = Admin(username="testadmin", full_name="Test Admin", password_hash="hash", is_active=True)
    db_session.add(admin)
    db_session.commit()
    token = create_jwt_token({"sub": str(admin.id), "username": admin.username, "role": "admin"})
    return {"Authorization": f"Bearer {token}"}

def test_reports_api_requires_admin(client, db_session):
    response = client.get("/api/v1/admin/reports/?type=orders")
    assert response.status_code == 401
    
    response = client.get("/api/v1/admin/export/orders")
    assert response.status_code == 401

def test_get_reports_orders(client, db_session, admin_token_headers):
    response = client.get("/api/v1/admin/reports/?type=orders", headers=admin_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_get_reports_payments(client, db_session, admin_token_headers):
    response = client.get("/api/v1/admin/reports/?type=payments", headers=admin_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_get_reports_expenses(client, db_session, admin_token_headers):
    response = client.get("/api/v1/admin/reports/?type=expenses", headers=admin_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_get_reports_inventory(client, db_session, admin_token_headers):
    response = client.get("/api/v1/admin/reports/?type=inventory", headers=admin_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_export_orders_csv(client, db_session, admin_token_headers):
    response = client.get("/api/v1/admin/export/orders?format=csv", headers=admin_token_headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    assert "attachment; filename=orders_report.csv" in response.headers["content-disposition"]

def test_export_orders_excel(client, db_session, admin_token_headers):
    response = client.get("/api/v1/admin/export/orders?format=excel", headers=admin_token_headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert "attachment; filename=orders_report.xlsx" in response.headers["content-disposition"]

def test_export_orders_pdf(client, db_session, admin_token_headers):
    response = client.get("/api/v1/admin/export/orders?format=pdf", headers=admin_token_headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert "attachment; filename=orders_report.pdf" in response.headers["content-disposition"]

def test_export_payments_csv(client, db_session, admin_token_headers):
    response = client.get("/api/v1/admin/export/payments?format=csv", headers=admin_token_headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"

def test_export_expenses_csv(client, db_session, admin_token_headers):
    response = client.get("/api/v1/admin/export/expenses?format=csv", headers=admin_token_headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"

def test_export_inventory_csv(client, db_session, admin_token_headers):
    response = client.get("/api/v1/admin/export/inventory?format=csv", headers=admin_token_headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"

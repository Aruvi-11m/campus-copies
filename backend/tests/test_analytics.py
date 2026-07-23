import pytest
from datetime import datetime, timedelta, timezone
from app.models.enums import OrderStatusEnum, BindingTypeEnum, ColorModeEnum, PaymentMethodEnum
from app.core.security import create_jwt_token
from app.models.admin import Admin

@pytest.fixture
def admin_token_headers(db_session):
    admin = Admin(username="testadmin", full_name="Test Admin", password_hash="hash", is_active=True)
    db_session.add(admin)
    db_session.commit()
    token = create_jwt_token({"sub": str(admin.id), "username": admin.username, "role": "admin"})
    return {"Authorization": f"Bearer {token}"}

def test_analytics_api_requires_admin(client, db_session):
    response = client.get("/api/v1/admin/analytics/daily-revenue")
    assert response.status_code == 401

def test_daily_revenue_analytics(client, db_session, admin_token_headers):
    # This should return a list of ChartDataPoint
    response = client.get("/api/v1/admin/analytics/daily-revenue?days=7", headers=admin_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # The structure should be [{"label": ..., "value": ...}]
    if len(data) > 0:
        assert "label" in data[0]
        assert "value" in data[0]

def test_orders_by_status(client, db_session, admin_token_headers):
    response = client.get("/api/v1/admin/analytics/orders-by-status", headers=admin_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_orders_by_department(client, db_session, admin_token_headers):
    response = client.get("/api/v1/admin/analytics/orders-by-department", headers=admin_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_monthly_revenue(client, db_session, admin_token_headers):
    response = client.get("/api/v1/admin/analytics/monthly-revenue?months=6", headers=admin_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_binding_type_usage(client, db_session, admin_token_headers):
    response = client.get("/api/v1/admin/analytics/binding-type-usage", headers=admin_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_color_vs_bw(client, db_session, admin_token_headers):
    response = client.get("/api/v1/admin/analytics/color-vs-bw", headers=admin_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_most_active_students(client, db_session, admin_token_headers):
    response = client.get("/api/v1/admin/analytics/most-active-students", headers=admin_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_expense_breakdown(client, db_session, admin_token_headers):
    response = client.get("/api/v1/admin/analytics/expense-breakdown", headers=admin_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_inventory_consumption(client, db_session, admin_token_headers):
    response = client.get("/api/v1/admin/analytics/inventory-consumption", headers=admin_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_averages(client, db_session, admin_token_headers):
    response = client.get("/api/v1/admin/analytics/averages", headers=admin_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert "average_order_value" in data
    assert "average_pages_per_order" in data

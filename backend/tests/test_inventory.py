"""
Campus Copies ERP - Inventory Test Suite

Tests inventory service logic, concurrency (basic coverage), and API endpoints.
"""

import pytest
import uuid
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.enums import InventoryCategoryEnum, InventoryTxnTypeEnum, OrderStatusEnum, BindingTypeEnum, PrintSideEnum, ColorModeEnum
from app.models.inventory import InventoryItem
from app.models.order import Order
from app.models.student import Student
from app.models.admin import Admin
from app.services.inventory_service import InventoryService
from app.core.security import create_jwt_token, hash_password


def make_student(db: Session, mobile: str = "9876543210", name: str = "Test Student") -> Student:
    student = Student(
        id=uuid.uuid4(),
        mobile=mobile,
        full_name=name,
        department="CSE",
    )
    db.add(student)
    db.flush()
    return student


def make_admin(db: Session, username: str = "testadmin") -> Admin:
    admin = Admin(
        id=uuid.uuid4(),
        username=username,
        password_hash=hash_password("TestPass123!"),
        full_name="Test Admin",
    )
    db.add(admin)
    db.flush()
    return admin


@pytest.fixture
def test_inventory_item(db_session: Session):
    item = InventoryItem(
        item_code="TEST_PAPER_A4",
        item_name="A4 Paper",
        category=InventoryCategoryEnum.PAPER,
        current_stock=1000,
        min_threshold=500,
        unit_cost=Decimal("0.50"),
    )
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)
    return item


@pytest.fixture
def test_inventory_ink(db_session: Session):
    item = InventoryItem(
        item_code="TEST_INK",
        item_name="Black Ink",
        category=InventoryCategoryEnum.INK,
        current_stock=5000,
        min_threshold=1000,
        unit_cost=Decimal("0.10"),
    )
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)
    return item


@pytest.fixture
def test_inventory_binding(db_session: Session):
    item = InventoryItem(
        item_code="TEST_SPIRAL",
        item_name="Spiral Binding",
        category=InventoryCategoryEnum.BINDING,
        sub_category=BindingTypeEnum.SPIRAL,
        current_stock=100,
        min_threshold=20,
        unit_cost=Decimal("5.00"),
    )
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)
    return item


def _setup_admin_token(db_session: Session):
    admin = make_admin(db_session)
    db_session.commit()
    token = create_jwt_token({"sub": str(admin.id), "role": "admin", "username": admin.username})
    return admin, {"Authorization": f"Bearer {token}"}


def test_create_inventory_item_api(client: TestClient, db_session: Session):
    admin, headers = _setup_admin_token(db_session)
    payload = {
        "item_code": "PAPER_A3",
        "item_name": "A3 Paper",
        "category": "PAPER",
        "min_threshold": 100,
        "unit_cost": "1.00",
    }
    response = client.post("/api/v1/inventory", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["item_code"] == "PAPER_A3"
    assert data["current_stock"] == 0


def test_list_inventory_items_api(client: TestClient, db_session: Session, test_inventory_item):
    admin, headers = _setup_admin_token(db_session)
    response = client.get("/api/v1/inventory", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    codes = [item["item_code"] for item in data]
    assert "TEST_PAPER_A4" in codes


def test_adjust_stock_api(client: TestClient, db_session: Session, test_inventory_item):
    admin, headers = _setup_admin_token(db_session)
    payload = {
        "transaction_type": "RESTOCK",
        "quantity_change": 500,
        "reason": "Supplier delivery",
    }
    response = client.post(
        f"/api/v1/inventory/{test_inventory_item.id}/stock", json=payload, headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["quantity_change"] == 500
    assert data["stock_after_txn"] == 1500

    res = client.get(f"/api/v1/inventory/{test_inventory_item.id}", headers=headers)
    assert res.json()["current_stock"] == 1500


def test_remove_stock_insufficient(client: TestClient, db_session: Session, test_inventory_item):
    admin, headers = _setup_admin_token(db_session)
    payload = {
        "transaction_type": "WASTAGE",
        "quantity_change": 2000,
    }
    response = client.post(
        f"/api/v1/inventory/{test_inventory_item.id}/stock", json=payload, headers=headers
    )
    assert response.status_code == 409


def test_low_stock_api(client: TestClient, db_session: Session, test_inventory_item):
    admin, headers = _setup_admin_token(db_session)
    payload = {
        "transaction_type": "WASTAGE",
        "quantity_change": 600,
    }
    client.post(f"/api/v1/inventory/{test_inventory_item.id}/stock", json=payload, headers=headers)
    
    response = client.get("/api/v1/inventory/low-stock", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert any(item["item_code"] == "TEST_PAPER_A4" for item in data)


def test_order_deduction_logic(
    db_session: Session,
    test_inventory_item,
    test_inventory_ink,
    test_inventory_binding,
):
    service = InventoryService(db_session)
    admin = make_admin(db_session, "admin2")
    student = make_student(db_session)

    order = Order(
        student_id=student.id,
        display_id="CC-9999",
        print_side=PrintSideEnum.DOUBLE_SIDE,
        color_mode=ColorModeEnum.BW,
        binding_type=BindingTypeEnum.SPIRAL,
        copies=2,
        page_count=10,
        per_page_price=Decimal("1.00"),
        binding_price=Decimal("10.00"),
        total_price=Decimal("20.00"),
        status=OrderStatusEnum.COMPLETED,
    )
    db_session.add(order)
    db_session.commit()

    service.deduct_order_materials(order, admin.id)
    db_session.commit()

    db_session.refresh(test_inventory_item)
    db_session.refresh(test_inventory_ink)
    db_session.refresh(test_inventory_binding)

    assert test_inventory_item.current_stock == 1000 - 10
    assert test_inventory_ink.current_stock == 5000 - 20
    assert test_inventory_binding.current_stock == 100 - 2

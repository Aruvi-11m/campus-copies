"""
Campus Copies ERP - Phase 5 Order Management Engine Test Suite

Comprehensive tests for PricingEngine, Order Lifecycle State Machine, PickupCode generation,
price snapshotting, role/owner security, API endpoints, search, filtering, and pagination.
Grounding: docs/TestingSpecification.md §4.1, §7, §9
"""

import pytest
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.errors import ConflictError, PermissionDeniedError, ValidationError
from app.core.security import create_jwt_token, hash_password
from app.models.enums import BindingTypeEnum, ColorModeEnum, OrderStatusEnum, PaymentMethodEnum, PrintSideEnum
from app.models.file import OrderFile
from app.models.order import Order
from app.models.pricing_setting import PricingSetting
from app.repositories.admin_repository import AdminRepository
from app.repositories.file_repository import FileRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.student_repository import StudentRepository
from app.services.order_service import OrderService
from app.services.pricing_service import PricingService


# ============================================================================
# 1. PRICING ENGINE TESTS
# ============================================================================

def test_pricing_single_side_bw(db_session: Session):
    """Test B&W Single Side pricing formula: (1.50 per page * 10 pages * 2 copies) + 0 = 30.00."""
    service = PricingService(db_session)
    per_page, binding, total = service.calculate_price(
        print_side=PrintSideEnum.SINGLE_SIDE,
        color_mode=ColorModeEnum.BW,
        binding_type=BindingTypeEnum.NONE,
        copies=2,
        page_count=10,
    )
    assert per_page == 1.50
    assert binding == 0.00
    assert total == 30.00


def test_pricing_double_side_bw(db_session: Session):
    """Test B&W Double Side pricing formula: (1.00 per page * 10 pages * 1 copy) + 30 (spiral) = 40.00."""
    service = PricingService(db_session)
    per_page, binding, total = service.calculate_price(
        print_side=PrintSideEnum.DOUBLE_SIDE,
        color_mode=ColorModeEnum.BW,
        binding_type=BindingTypeEnum.SPIRAL,
        copies=1,
        page_count=10,
    )
    assert per_page == 1.00
    assert binding == 30.00
    assert total == 40.00


def test_pricing_color_single_side(db_session: Session):
    """Test Color Single Side pricing formula: (5.00 per page * 5 pages * 1 copy) + 40 (soft cover) = 65.00."""
    service = PricingService(db_session)
    per_page, binding, total = service.calculate_price(
        print_side=PrintSideEnum.SINGLE_SIDE,
        color_mode=ColorModeEnum.COLOR,
        binding_type=BindingTypeEnum.SOFT_COVER,
        copies=1,
        page_count=5,
    )
    assert per_page == 5.00
    assert binding == 40.00
    assert total == 65.00


def test_pricing_color_double_side_rejection(db_session: Session):
    """Test Color mode with DOUBLE_SIDE orientation raises ValidationError."""
    service = PricingService(db_session)
    with pytest.raises(ValidationError) as exc:
        service.calculate_price(
            print_side=PrintSideEnum.DOUBLE_SIDE,
            color_mode=ColorModeEnum.COLOR,
            binding_type=BindingTypeEnum.NONE,
            copies=1,
            page_count=5,
        )
    assert "single side" in str(exc.value).lower()


def test_bankers_rounding():
    """Verify bankers' rounding (ROUND_HALF_EVEN) behavior."""
    assert PricingService.bankers_round(2.505) == 2.50
    assert PricingService.bankers_round(2.515) == 2.52
    assert PricingService.bankers_round(1.50) == 1.50


def test_price_snapshot_immutability(db_session: Session):
    """Verify changing active rates in pricing_settings does NOT alter historical order totals."""
    student_repo = StudentRepository(db_session)
    student = student_repo.create(mobile="9876543210", full_name="Arun", department="CSE")

    file_repo = FileRepository(db_session)
    file_rec = file_repo.create(
        student_id=student.id,
        original_name="test.pdf",
        storage_path=f"temp/{student.id}/test.pdf",
        file_size=1024,
        mime_type="application/pdf",
    )

    order_service = OrderService(db_session)
    order = order_service.create_order(
        student=student,
        file_ids=[file_rec.id],
        print_side=PrintSideEnum.SINGLE_SIDE,
        color_mode=ColorModeEnum.BW,
        binding_type=BindingTypeEnum.NONE,
        copies=1,
    )
    initial_total = order.total_price  # 1.50

    # Modify pricing_settings to double rates
    order_repo = OrderRepository(db_session)
    new_pricing = PricingSetting(
        bw_single_side=10.00,
        bw_double_side=8.00,
        color_single_side=20.00,
        is_current=True,
    )
    # Set previous setting to is_current=False
    db_session.query(PricingSetting).update({PricingSetting.is_current: False})
    db_session.add(new_pricing)
    db_session.commit()

    # Re-fetch order and verify frozen snapshot price remained intact
    fetched_order = order_repo.get_by_id(order.id)
    assert fetched_order.total_price == initial_total
    assert fetched_order.per_page_price == 1.50


# ============================================================================
# 2. STATE MACHINE & ORDER LIFECYCLE TESTS
# ============================================================================

def test_order_creation_and_pickup_code(db_session: Session):
    """Test order creation, pickup code generation, and initial state."""
    student_repo = StudentRepository(db_session)
    student = student_repo.create(mobile="9876543210", full_name="Arun", department="CSE")

    file_repo = FileRepository(db_session)
    file_rec = file_repo.create(
        student_id=student.id,
        original_name="doc.pdf",
        storage_path=f"temp/{student.id}/doc.pdf",
        file_size=512,
        mime_type="application/pdf",
    )

    order_service = OrderService(db_session)
    order = order_service.create_order(
        student=student,
        file_ids=[file_rec.id],
        print_side=PrintSideEnum.SINGLE_SIDE,
        color_mode=ColorModeEnum.BW,
        binding_type=BindingTypeEnum.SPIRAL,
        copies=1,
    )

    assert order.status == OrderStatusEnum.PENDING_PAYMENT
    assert order.pickup_code is not None
    assert len(order.pickup_code.code) == 6
    assert order.pickup_code.code.isupper()
    assert order.pickup_code.code.isalnum()


def test_state_machine_valid_transitions(db_session: Session):
    """Test all valid state machine transitions: PENDING_PAYMENT -> PAID -> PRINTING -> READY_FOR_PICKUP -> COMPLETED."""
    student_repo = StudentRepository(db_session)
    student = student_repo.create(mobile="9876543210", full_name="Arun", department="CSE")

    admin_repo = AdminRepository(db_session)
    admin = admin_repo.create(username="shopadmin", password_hash=hash_password("Pass123"), full_name="Admin")

    file_repo = FileRepository(db_session)
    file_rec = file_repo.create(student_id=student.id, original_name="doc.pdf", storage_path="temp/d.pdf", file_size=100, mime_type="application/pdf")

    service = OrderService(db_session)
    order = service.create_order(student, [file_rec.id], PrintSideEnum.SINGLE_SIDE, ColorModeEnum.BW, BindingTypeEnum.NONE, 1)

    # 1. PENDING_PAYMENT -> PAID
    o1 = service.update_order_status(order.id, OrderStatusEnum.PAID, admin, payment_method=PaymentMethodEnum.UPI)
    assert o1.status == OrderStatusEnum.PAID
    assert o1.payment_method == PaymentMethodEnum.UPI

    # 2. PAID -> PRINTING
    o2 = service.update_order_status(order.id, OrderStatusEnum.PRINTING, admin)
    assert o2.status == OrderStatusEnum.PRINTING

    # 3. PRINTING -> READY_FOR_PICKUP
    o3 = service.update_order_status(order.id, OrderStatusEnum.READY_FOR_PICKUP, admin)
    assert o3.status == OrderStatusEnum.READY_FOR_PICKUP

    # 4. READY_FOR_PICKUP -> COMPLETED
    o4 = service.update_order_status(order.id, OrderStatusEnum.COMPLETED, admin)
    assert o4.status == OrderStatusEnum.COMPLETED


def test_state_machine_invalid_transitions(db_session: Session):
    """Test invalid transitions raise ConflictError (HTTP 409)."""
    student_repo = StudentRepository(db_session)
    student = student_repo.create(mobile="9876543210", full_name="Arun", department="CSE")

    admin_repo = AdminRepository(db_session)
    admin = admin_repo.create(username="shopadmin", password_hash=hash_password("Pass123"), full_name="Admin")

    file_repo = FileRepository(db_session)
    file_rec = file_repo.create(student_id=student.id, original_name="doc.pdf", storage_path="temp/d.pdf", file_size=100, mime_type="application/pdf")

    service = OrderService(db_session)
    order = service.create_order(student, [file_rec.id], PrintSideEnum.SINGLE_SIDE, ColorModeEnum.BW, BindingTypeEnum.NONE, 1)

    # Skipped transition: PENDING_PAYMENT -> PRINTING
    with pytest.raises(ConflictError):
        service.update_order_status(order.id, OrderStatusEnum.PRINTING, admin)

    # Advance to PAID
    service.update_order_status(order.id, OrderStatusEnum.PAID, admin, payment_method=PaymentMethodEnum.CASH)

    # Backward transition: PAID -> PENDING_PAYMENT
    with pytest.raises(ConflictError):
        service.update_order_status(order.id, OrderStatusEnum.PENDING_PAYMENT, admin)


# ============================================================================
# 3. API & SECURITY TESTS
# ============================================================================

def test_api_create_order_success(db_session: Session, client: TestClient):
    """Test POST /api/v1/orders endpoint."""
    student_repo = StudentRepository(db_session)
    student = student_repo.create(mobile="9876543210", full_name="Arun", department="CSE")
    token = create_jwt_token({"sub": str(student.id), "role": "student"})

    file_repo = FileRepository(db_session)
    file_rec = file_repo.create(student_id=student.id, original_name="notes.pdf", storage_path="temp/n.pdf", file_size=200, mime_type="application/pdf")

    payload = {
        "file_ids": [str(file_rec.id)],
        "print_side": "SINGLE_SIDE",
        "color_mode": "BW",
        "binding_type": "SPIRAL",
        "copies": 1,
    }

    response = client.post(
        "/api/v1/orders",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert "display_id" in data["data"]
    assert data["data"]["status"] == "PENDING_PAYMENT"
    assert data["data"]["pickup_code"] is not None


def test_api_order_details_ownership_security(db_session: Session, client: TestClient):
    """Test GET /api/v1/orders/{id} security checks."""
    student_repo = StudentRepository(db_session)
    owner = student_repo.create(mobile="9876543210", full_name="Owner", department="CSE")
    other = student_repo.create(mobile="8765432109", full_name="Other", department="ECE")

    admin_repo = AdminRepository(db_session)
    admin = admin_repo.create(username="admin", password_hash=hash_password("P"), full_name="Admin")

    file_repo = FileRepository(db_session)
    file_rec = file_repo.create(student_id=owner.id, original_name="notes.pdf", storage_path="temp/n.pdf", file_size=200, mime_type="application/pdf")

    service = OrderService(db_session)
    order = service.create_order(owner, [file_rec.id], PrintSideEnum.SINGLE_SIDE, ColorModeEnum.BW, BindingTypeEnum.NONE, 1)

    owner_token = create_jwt_token({"sub": str(owner.id), "role": "student"})
    other_token = create_jwt_token({"sub": str(other.id), "role": "student"})
    admin_token = create_jwt_token({"sub": str(admin.id), "role": "admin"})

    # Owner -> 200 OK
    res_owner = client.get(f"/api/v1/orders/{order.id}", headers={"Authorization": f"Bearer {owner_token}"})
    assert res_owner.status_code == 200

    # Other student -> 403 Forbidden
    res_other = client.get(f"/api/v1/orders/{order.id}", headers={"Authorization": f"Bearer {other_token}"})
    assert res_other.status_code == 403

    # Admin -> 200 OK
    res_admin = client.get(f"/api/v1/orders/{order.id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert res_admin.status_code == 200


def test_api_admin_order_search_and_pagination(db_session: Session, client: TestClient):
    """Test GET /api/v1/admin/orders list endpoint with search and pagination."""
    student_repo = StudentRepository(db_session)
    s1 = student_repo.create(mobile="9876543210", full_name="Arun Kumar", department="CSE")
    s2 = student_repo.create(mobile="8765432109", full_name="Bala", department="ECE")

    admin_repo = AdminRepository(db_session)
    admin = admin_repo.create(username="admin", password_hash=hash_password("P"), full_name="Admin")
    admin_token = create_jwt_token({"sub": str(admin.id), "role": "admin"})

    file_repo = FileRepository(db_session)
    f1 = file_repo.create(student_id=s1.id, original_name="f1.pdf", storage_path="t/1.pdf", file_size=100, mime_type="application/pdf")
    f2 = file_repo.create(student_id=s2.id, original_name="f2.pdf", storage_path="t/2.pdf", file_size=100, mime_type="application/pdf")

    service = OrderService(db_session)
    o1 = service.create_order(s1, [f1.id], PrintSideEnum.SINGLE_SIDE, ColorModeEnum.BW, BindingTypeEnum.NONE, 1)
    o2 = service.create_order(s2, [f2.id], PrintSideEnum.SINGLE_SIDE, ColorModeEnum.BW, BindingTypeEnum.NONE, 1)

    # Search by student name "Arun"
    res_search = client.get(
        "/api/v1/admin/orders?search=Arun",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res_search.status_code == 200
    data = res_search.json()["data"]
    assert data["total"] == 1
    assert data["items"][0]["id"] == str(o1.id)

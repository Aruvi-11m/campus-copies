"""
Campus Copies ERP - Phase 6 Finance & Payment Tests

Comprehensive test suite covering:
  - Payment model creation
  - Expense model creation
  - LedgerEntry model creation
  - PaymentRepository operations
  - ExpenseRepository operations
  - LedgerRepository operations
  - FinanceService: payment verification
  - FinanceService: duplicate payment prevention
  - FinanceService: amount mismatch rejection
  - FinanceService: wrong state rejection
  - FinanceService: cash balance tracking
  - FinanceService: UPI vs CASH balance isolation
  - FinanceService: expense creation with ledger
  - FinanceService: balance calculation
  - FinanceService: refund processing
  - API: POST /api/v1/payments/verify (admin-only)
  - API: GET /api/v1/payments/balance
  - API: GET /api/v1/payments/ledger
  - API: POST /api/v1/expenses (admin-only)
  - API: GET /api/v1/expenses
"""

import uuid
from datetime import date, datetime, timezone
from decimal import Decimal

import pytest
from sqlalchemy.orm import Session

from app.core.security import create_jwt_token, hash_password
from app.models.admin import Admin
from app.models.enums import (
    BindingTypeEnum,
    ColorModeEnum,
    FileStatusEnum,
    OrderStatusEnum,
    PaymentMethodEnum,
    PrintSideEnum,
)
from app.models.expense import Expense
from app.models.file import OrderFile
from app.models.ledger_entry import LedgerEntry
from app.models.order import Order
from app.models.payment import Payment
from app.models.pickup_code import PickupCode
from app.models.pricing_setting import PricingSetting
from app.models.student import Student
from app.repositories.expense_repository import ExpenseRepository
from app.repositories.ledger_repository import LedgerRepository
from app.repositories.payment_repository import PaymentRepository
from app.services.finance_service import FinanceService


# ════════════════════════════════════════════════════════
# Test Helpers
# ════════════════════════════════════════════════════════


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
        is_active=True,
    )
    db.add(admin)
    db.flush()
    return admin


def make_pricing_setting(db: Session) -> PricingSetting:
    ps = PricingSetting(
        bw_single_side=1.00,
        bw_double_side=0.75,
        bw_multi_page=0.60,
        color_single_side=5.00,
        spiral_binding_price=30.00,
        soft_binding_price=50.00,
        hard_binding_price=100.00,
        stapling_price=5.00,
    )
    db.add(ps)
    db.flush()
    return ps


def make_order(
    db: Session,
    student: Student,
    total_price: float = 105.00,
    status: OrderStatusEnum = OrderStatusEnum.PENDING_PAYMENT,
) -> Order:
    order = Order(
        id=uuid.uuid4(),
        display_id=f"CC-2026-{uuid.uuid4().hex[:4].upper()}",
        student_id=student.id,
        status=status,
        print_side=PrintSideEnum.SINGLE_SIDE,
        color_mode=ColorModeEnum.BW,
        binding_type=BindingTypeEnum.SPIRAL,
        copies=2,
        page_count=25,
        per_page_price=1.00,
        binding_price=30.00,
        total_price=total_price,
    )
    db.add(order)
    db.flush()
    # Add a pickup code
    pickup = PickupCode(
        order_id=order.id,
        code=uuid.uuid4().hex[:6].upper(),
    )
    db.add(pickup)
    db.flush()
    return order


# ════════════════════════════════════════════════════════
# 1. Model Tests
# ════════════════════════════════════════════════════════


class TestPaymentModel:
    def test_create_payment_record(self, db_session: Session):
        student = make_student(db_session)
        admin = make_admin(db_session)
        order = make_order(db_session, student)

        payment = Payment(
            order_id=order.id,
            amount=105.00,
            payment_method=PaymentMethodEnum.CASH,
            verified_by_admin_id=admin.id,
            notes="Cash received at counter",
        )
        db_session.add(payment)
        db_session.commit()

        assert payment.id is not None
        assert float(payment.amount) == 105.00
        assert payment.payment_method == PaymentMethodEnum.CASH
        assert payment.order_id == order.id
        assert payment.verified_by_admin_id == admin.id

    def test_payment_unique_order_constraint(self, db_session: Session):
        """Only one payment per order (unique constraint on order_id)."""
        student = make_student(db_session)
        admin = make_admin(db_session)
        order = make_order(db_session, student)

        payment1 = Payment(
            order_id=order.id,
            amount=105.00,
            payment_method=PaymentMethodEnum.CASH,
            verified_by_admin_id=admin.id,
        )
        db_session.add(payment1)
        db_session.commit()

        payment2 = Payment(
            order_id=order.id,
            amount=105.00,
            payment_method=PaymentMethodEnum.UPI,
            verified_by_admin_id=admin.id,
        )
        db_session.add(payment2)
        with pytest.raises(Exception):
            db_session.commit()


class TestExpenseModel:
    def test_create_expense_record(self, db_session: Session):
        admin = make_admin(db_session)

        expense = Expense(
            amount=250.00,
            category="MATERIALS",
            description="Purchased A4 paper ream",
            expense_date=date.today(),
            payment_method=PaymentMethodEnum.CASH,
            created_by_admin_id=admin.id,
        )
        db_session.add(expense)
        db_session.commit()

        assert expense.id is not None
        assert float(expense.amount) == 250.00
        assert expense.category == "MATERIALS"


class TestLedgerEntryModel:
    def test_create_ledger_entry(self, db_session: Session):
        admin = make_admin(db_session)

        entry = LedgerEntry(
            entry_type="PAYMENT_CASH",
            amount=105.00,
            running_cash_balance=105.00,
            description="Test payment entry",
            admin_id=admin.id,
        )
        db_session.add(entry)
        db_session.commit()

        assert entry.id is not None
        assert entry.entry_type == "PAYMENT_CASH"
        assert float(entry.amount) == 105.00
        assert float(entry.running_cash_balance) == 105.00


# ════════════════════════════════════════════════════════
# 2. Repository Tests
# ════════════════════════════════════════════════════════


class TestPaymentRepository:
    def test_get_by_order_id(self, db_session: Session):
        student = make_student(db_session)
        admin = make_admin(db_session)
        order = make_order(db_session, student)

        repo = PaymentRepository(db_session)

        # No payment initially
        assert repo.get_by_order_id(order.id) is None

        # Create payment
        payment = Payment(
            order_id=order.id,
            amount=105.00,
            payment_method=PaymentMethodEnum.CASH,
            verified_by_admin_id=admin.id,
        )
        db_session.add(payment)
        db_session.commit()

        found = repo.get_by_order_id(order.id)
        assert found is not None
        assert found.id == payment.id


class TestExpenseRepository:
    def test_list_and_filter_expenses(self, db_session: Session):
        admin = make_admin(db_session)
        repo = ExpenseRepository(db_session)

        # Create multiple expenses
        for i in range(5):
            expense = Expense(
                amount=50.00 * (i + 1),
                category="MATERIALS" if i < 3 else "UTILITIES",
                description=f"Expense #{i+1}",
                expense_date=date.today(),
                payment_method=PaymentMethodEnum.CASH,
                created_by_admin_id=admin.id,
            )
            db_session.add(expense)
        db_session.commit()

        # All expenses
        items, total = repo.list_expenses()
        assert total == 5

        # Filtered by category
        items, total = repo.list_expenses(category="MATERIALS")
        assert total == 3

        items, total = repo.list_expenses(category="UTILITIES")
        assert total == 2


class TestLedgerRepository:
    def test_append_entry_and_balance(self, db_session: Session):
        admin = make_admin(db_session)
        repo = LedgerRepository(db_session)

        # Initial balance
        assert repo.get_latest_cash_balance() == 0.0

        # Append entries
        repo.append_entry(
            entry_type="PAYMENT_CASH",
            amount=500.00,
            running_cash_balance=500.00,
            description="Cash payment",
            admin_id=admin.id,
        )
        db_session.commit()
        assert repo.get_latest_cash_balance() == 500.00

        repo.append_entry(
            entry_type="EXPENSE_CASH",
            amount=-100.00,
            running_cash_balance=400.00,
            description="Cash expense",
            admin_id=admin.id,
        )
        db_session.commit()
        assert repo.get_latest_cash_balance() == 400.00

    def test_sum_by_type(self, db_session: Session):
        admin = make_admin(db_session)
        repo = LedgerRepository(db_session)

        repo.append_entry("PAYMENT_CASH", 200.00, 200.00, "Cash payment 1", admin_id=admin.id)
        repo.append_entry("PAYMENT_CASH", 300.00, 500.00, "Cash payment 2", admin_id=admin.id)
        repo.append_entry("PAYMENT_UPI", 150.00, 500.00, "UPI payment", admin_id=admin.id)
        db_session.commit()

        assert repo.sum_by_type("PAYMENT_CASH") == 500.00
        assert repo.sum_by_type("PAYMENT_UPI") == 150.00


# ════════════════════════════════════════════════════════
# 3. FinanceService Tests
# ════════════════════════════════════════════════════════


class TestFinanceServicePaymentVerification:
    def test_verify_cash_payment_success(self, db_session: Session):
        """Successfully verifies a cash payment, transitions order to PAID, creates ledger entry."""
        student = make_student(db_session)
        admin = make_admin(db_session)
        make_pricing_setting(db_session)
        order = make_order(db_session, student, total_price=105.00)
        db_session.commit()

        service = FinanceService(db_session)
        payment = service.verify_payment(
            order_id=order.id,
            amount=105.00,
            payment_method=PaymentMethodEnum.CASH,
            admin=admin,
            notes="Cash at counter",
        )

        assert payment.id is not None
        assert float(payment.amount) == 105.00
        assert payment.payment_method == PaymentMethodEnum.CASH

        # Order should be transitioned to PAID
        db_session.refresh(order)
        assert order.status == OrderStatusEnum.PAID
        assert order.payment_method == PaymentMethodEnum.CASH

        # Cash balance should increase
        ledger_repo = LedgerRepository(db_session)
        assert ledger_repo.get_latest_cash_balance() == 105.00

    def test_verify_upi_payment_no_cash_impact(self, db_session: Session):
        """UPI payment should NOT affect cash-in-hand balance."""
        student = make_student(db_session)
        admin = make_admin(db_session)
        make_pricing_setting(db_session)
        order = make_order(db_session, student, total_price=200.00)
        db_session.commit()

        service = FinanceService(db_session)
        payment = service.verify_payment(
            order_id=order.id,
            amount=200.00,
            payment_method=PaymentMethodEnum.UPI,
            admin=admin,
        )

        assert payment.payment_method == PaymentMethodEnum.UPI

        # Cash balance should remain at 0
        ledger_repo = LedgerRepository(db_session)
        assert ledger_repo.get_latest_cash_balance() == 0.00

    def test_reject_duplicate_payment(self, db_session: Session):
        """Prevents duplicate payment verification for the same order."""
        student = make_student(db_session)
        admin = make_admin(db_session)
        make_pricing_setting(db_session)
        order = make_order(db_session, student, total_price=100.00)
        db_session.commit()

        service = FinanceService(db_session)
        service.verify_payment(
            order_id=order.id,
            amount=100.00,
            payment_method=PaymentMethodEnum.CASH,
            admin=admin,
        )

        # Second attempt should fail - order is now PAID, so status check rejects it
        from app.core.errors import ConflictError
        with pytest.raises(ConflictError, match="expected 'PENDING_PAYMENT'"):
            service.verify_payment(
                order_id=order.id,
                amount=100.00,
                payment_method=PaymentMethodEnum.CASH,
                admin=admin,
            )

    def test_reject_amount_mismatch(self, db_session: Session):
        """Rejects payment when amount does not match order total."""
        student = make_student(db_session)
        admin = make_admin(db_session)
        make_pricing_setting(db_session)
        order = make_order(db_session, student, total_price=105.00)
        db_session.commit()

        from app.core.errors import ValidationError
        service = FinanceService(db_session)
        with pytest.raises(ValidationError, match="does not match"):
            service.verify_payment(
                order_id=order.id,
                amount=100.00,
                payment_method=PaymentMethodEnum.CASH,
                admin=admin,
            )

    def test_reject_wrong_order_status(self, db_session: Session):
        """Rejects payment for orders not in PENDING_PAYMENT state."""
        student = make_student(db_session)
        admin = make_admin(db_session)
        make_pricing_setting(db_session)
        order = make_order(db_session, student, total_price=50.00, status=OrderStatusEnum.PRINTING)
        db_session.commit()

        from app.core.errors import ConflictError
        service = FinanceService(db_session)
        with pytest.raises(ConflictError, match="expected 'PENDING_PAYMENT'"):
            service.verify_payment(
                order_id=order.id,
                amount=50.00,
                payment_method=PaymentMethodEnum.CASH,
                admin=admin,
            )

    def test_reject_nonexistent_order(self, db_session: Session):
        """Rejects payment for a non-existent order."""
        admin = make_admin(db_session)
        db_session.commit()

        from app.core.errors import NotFoundError
        service = FinanceService(db_session)
        with pytest.raises(NotFoundError):
            service.verify_payment(
                order_id=uuid.uuid4(),
                amount=50.00,
                payment_method=PaymentMethodEnum.CASH,
                admin=admin,
            )


class TestFinanceServiceExpenses:
    def test_create_cash_expense_reduces_balance(self, db_session: Session):
        """Cash expense should reduce cash-in-hand balance."""
        admin = make_admin(db_session)
        student = make_student(db_session)
        make_pricing_setting(db_session)

        # First add cash revenue
        order = make_order(db_session, student, total_price=500.00)
        db_session.commit()

        service = FinanceService(db_session)
        service.verify_payment(
            order_id=order.id,
            amount=500.00,
            payment_method=PaymentMethodEnum.CASH,
            admin=admin,
        )

        ledger_repo = LedgerRepository(db_session)
        assert ledger_repo.get_latest_cash_balance() == 500.00

        # Create expense
        expense = service.create_expense(
            amount=100.00,
            category="MATERIALS",
            description="Paper purchase",
            admin=admin,
            payment_method=PaymentMethodEnum.CASH,
        )

        assert expense.id is not None
        assert float(expense.amount) == 100.00

        # Cash balance should be reduced
        assert ledger_repo.get_latest_cash_balance() == 400.00

    def test_create_upi_expense_no_cash_impact(self, db_session: Session):
        """UPI expenses should NOT affect cash balance."""
        admin = make_admin(db_session)
        db_session.commit()

        service = FinanceService(db_session)
        expense = service.create_expense(
            amount=200.00,
            category="UTILITIES",
            description="Electricity bill via UPI",
            admin=admin,
            payment_method=PaymentMethodEnum.UPI,
        )

        assert expense.id is not None
        ledger_repo = LedgerRepository(db_session)
        assert ledger_repo.get_latest_cash_balance() == 0.00


class TestFinanceServiceBalance:
    def test_comprehensive_balance_calculation(self, db_session: Session):
        """Tests complete balance calculation with mixed payments and expenses."""
        student = make_student(db_session)
        admin = make_admin(db_session)
        make_pricing_setting(db_session)

        service = FinanceService(db_session)

        # Create 2 cash orders and 1 UPI order
        order1 = make_order(db_session, student, total_price=100.00)
        order2 = make_order(db_session, student, total_price=200.00)
        order3 = make_order(db_session, student, total_price=300.00)
        db_session.commit()

        service.verify_payment(order1.id, 100.00, PaymentMethodEnum.CASH, admin)
        service.verify_payment(order2.id, 200.00, PaymentMethodEnum.CASH, admin)
        service.verify_payment(order3.id, 300.00, PaymentMethodEnum.UPI, admin)

        # Create expenses
        service.create_expense(50.00, "MATERIALS", "Paper", admin, payment_method=PaymentMethodEnum.CASH)

        balance = service.get_balance()
        assert balance["total_cash_revenue"] == 300.00
        assert balance["total_upi_revenue"] == 300.00
        assert balance["total_revenue"] == 600.00
        assert balance["total_expenses"] == 50.00
        assert balance["net_profit"] == 550.00
        # Cash: 100 + 200 (payments) - 50 (expense) = 250
        assert balance["cash_in_hand"] == 250.00


class TestFinanceServiceRefund:
    def test_refund_reduces_cash_balance(self, db_session: Session):
        """Cash refund should reduce cash-in-hand balance."""
        student = make_student(db_session)
        admin = make_admin(db_session)
        make_pricing_setting(db_session)

        order = make_order(db_session, student, total_price=100.00)
        db_session.commit()

        service = FinanceService(db_session)
        service.verify_payment(order.id, 100.00, PaymentMethodEnum.CASH, admin)

        ledger_repo = LedgerRepository(db_session)
        assert ledger_repo.get_latest_cash_balance() == 100.00

        entry = service.process_refund(order.id, 50.00, "Partial refund", admin)
        assert entry.entry_type == "REFUND_CASH"
        assert float(entry.amount) == -50.00
        assert ledger_repo.get_latest_cash_balance() == 50.00


# ════════════════════════════════════════════════════════
# 4. API Integration Tests
# ════════════════════════════════════════════════════════


class TestPaymentAPI:
    def _setup_admin_token(self, db_session: Session):
        admin = make_admin(db_session)
        make_pricing_setting(db_session)
        db_session.commit()
        token = create_jwt_token({"sub": str(admin.id), "role": "admin", "username": admin.username})
        return admin, token

    def test_verify_payment_api(self, client, db_session: Session):
        admin, token = self._setup_admin_token(db_session)
        student = make_student(db_session)
        order = make_order(db_session, student, total_price=100.00)
        db_session.commit()

        response = client.post(
            "/api/v1/payments/verify",
            json={
                "order_id": str(order.id),
                "amount": 100.00,
                "payment_method": "CASH",
                "notes": "Cash received",
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["amount"] == 100.00
        assert data["data"]["payment_method"] == "CASH"

    def test_verify_payment_requires_admin(self, client, db_session: Session):
        """Student token should be rejected for payment verification."""
        student = make_student(db_session)
        db_session.commit()
        token = create_jwt_token({"sub": str(student.id), "role": "student", "mobile": student.mobile})

        response = client.post(
            "/api/v1/payments/verify",
            json={
                "order_id": str(uuid.uuid4()),
                "amount": 100.00,
                "payment_method": "CASH",
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403

    def test_balance_api(self, client, db_session: Session):
        admin, token = self._setup_admin_token(db_session)

        response = client.get(
            "/api/v1/payments/balance",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "cash_in_hand" in data["data"]
        assert "net_profit" in data["data"]

    def test_ledger_api(self, client, db_session: Session):
        admin, token = self._setup_admin_token(db_session)

        response = client.get(
            "/api/v1/payments/ledger",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "items" in data["data"]
        assert "total" in data["data"]


class TestExpenseAPI:
    def _setup_admin_token(self, db_session: Session):
        admin = make_admin(db_session)
        db_session.commit()
        token = create_jwt_token({"sub": str(admin.id), "role": "admin", "username": admin.username})
        return admin, token

    def test_create_expense_api(self, client, db_session: Session):
        admin, token = self._setup_admin_token(db_session)

        response = client.post(
            "/api/v1/expenses",
            json={
                "amount": 250.00,
                "category": "MATERIALS",
                "description": "Purchased 2 reams A4 paper",
                "payment_method": "CASH",
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["amount"] == 250.00
        assert data["data"]["category"] == "MATERIALS"

    def test_list_expenses_api(self, client, db_session: Session):
        admin, token = self._setup_admin_token(db_session)

        response = client.get(
            "/api/v1/expenses",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "items" in data["data"]

    def test_expense_requires_admin(self, client, db_session: Session):
        """Student token should be rejected for expense creation."""
        student = make_student(db_session)
        db_session.commit()
        token = create_jwt_token({"sub": str(student.id), "role": "student", "mobile": student.mobile})

        response = client.post(
            "/api/v1/expenses",
            json={
                "amount": 100.00,
                "category": "MATERIALS",
                "description": "Test",
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403

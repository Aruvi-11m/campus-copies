"""
Campus Copies ERP - Finance Service

Core business logic for payment verification, expense management,
immutable ledger operations, and balance calculations.
Grounding: docs/BusinessRules.md §5, §9, docs/BackendSpecification.md §4
"""

import uuid
from datetime import date, datetime, timezone
from decimal import Decimal, ROUND_HALF_EVEN
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session

from app.core.errors import ConflictError, NotFoundError, PermissionDeniedError, ValidationError
from app.core.logging import logger
from app.models.admin import Admin
from app.models.enums import OrderStatusEnum, PaymentMethodEnum
from app.models.expense import Expense
from app.models.ledger_entry import LedgerEntry
from app.models.order import Order
from app.models.payment import Payment
from app.repositories.expense_repository import ExpenseRepository
from app.repositories.ledger_repository import LedgerRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.payment_repository import PaymentRepository
from app.services.order_service import OrderService
from app.services.dashboard_service import invalidate_dashboard_cache
from app.services.audit_service import AuditService
from app.repositories.audit_repository import AuditRepository
from app.models.enums import ActorTypeEnum


class FinanceService:
    def __init__(self, db: Session):
        self.db = db
        self.payment_repo = PaymentRepository(db)
        self.expense_repo = ExpenseRepository(db)
        self.ledger_repo = LedgerRepository(db)
        self.order_repo = OrderRepository(db)

    def verify_payment(
        self,
        order_id: uuid.UUID,
        amount: float,
        payment_method: PaymentMethodEnum,
        admin: Admin,
        notes: Optional[str] = None,
    ) -> Payment:
        """
        Verifies and records payment for an order in a single atomic transaction.
        - Validates order exists and is in PENDING_PAYMENT state
        - Prevents duplicate verification (unique order_id constraint)
        - Creates immutable Payment record
        - Advances order to PAID via existing state machine
        - Creates immutable ledger entry
        - Uses row-level locking for concurrency
        """
        # Lock the order row for update to prevent concurrent verification
        order = self.order_repo.get_by_id_for_update(order_id)
        if not order:
            raise NotFoundError(f"Order '{order_id}' was not found")

        # Check order is in PENDING_PAYMENT state
        if order.status != OrderStatusEnum.PENDING_PAYMENT:
            raise ConflictError(
                f"Order '{order.display_id}' is in status '{order.status.value}', "
                f"expected 'PENDING_PAYMENT' for payment verification"
            )

        # BR-PAY: Prevent duplicate payment verification
        existing_payment = self.payment_repo.get_by_order_id(order_id)
        if existing_payment:
            raise ConflictError(
                f"Payment already verified for order '{order.display_id}' "
                f"on {existing_payment.payment_date.isoformat()}"
            )

        # BR-PAY: Validate payment amount matches order total
        order_total = float(Decimal(str(order.total_price)).quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN))
        payment_amount = float(Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN))
        if payment_amount != order_total:
            raise ValidationError(
                f"Payment amount ₹{payment_amount:.2f} does not match order total ₹{order_total:.2f}"
            )

        # Create immutable Payment record
        payment = Payment(
            order_id=order.id,
            amount=payment_amount,
            payment_method=payment_method,
            verified_by_admin_id=admin.id,
            notes=notes,
        )
        self.payment_repo.save(payment)
        self.db.flush()

        # Advance order status to PAID via existing state machine
        order.status = OrderStatusEnum.PAID
        order.payment_method = payment_method
        order.updated_by_admin_id = admin.id
        order.updated_at = datetime.now(timezone.utc)

        # Create order status history entry
        from app.models.order_status_history import OrderStatusHistory
        history = OrderStatusHistory(
            order_id=order.id,
            from_status=OrderStatusEnum.PENDING_PAYMENT,
            to_status=OrderStatusEnum.PAID,
            admin_id=admin.id,
            notes=f"Payment verified: {payment_method.value} ₹{payment_amount:.2f}" + (f" - {notes}" if notes else ""),
        )
        self.db.add(history)

        # Create immutable ledger entry
        entry_type = f"PAYMENT_{payment_method.value}"
        current_cash = self.ledger_repo.get_latest_cash_balance()

        # Only CASH payments affect physical cash balance
        if payment_method == PaymentMethodEnum.CASH:
            new_cash_balance = float(Decimal(str(current_cash + payment_amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN))
        else:
            new_cash_balance = current_cash

        self.ledger_repo.append_entry(
            entry_type=entry_type,
            amount=payment_amount,
            running_cash_balance=new_cash_balance,
            description=f"Payment for order {order.display_id} ({payment_method.value})",
            admin_id=admin.id,
            order_id=order.id,
            payment_id=payment.id,
        )

        self.db.commit()
        self.db.refresh(payment)
        self.db.refresh(order)

        try:
            audit_service = AuditService(AuditRepository(self.db))
            audit_service.log_action(
                action="verify_payment",
                resource_type="payment",
                actor_type=ActorTypeEnum.ADMIN,
                actor_id=admin.id,
                resource_id=payment.id,
                new_value={"amount": payment_amount, "method": payment_method.value},
            )
        except Exception:
            pass

        logger.info(
            "payment_verified_successfully",
            order_id=str(order.id),
            display_id=order.display_id,
            amount=payment_amount,
            payment_method=payment_method.value,
            admin_id=str(admin.id),
        )
        invalidate_dashboard_cache()
        return payment

    def process_refund(
        self,
        order_id: uuid.UUID,
        amount: float,
        reason: str,
        admin: Admin,
    ) -> LedgerEntry:
        """
        Records a refund as a negative ledger entry.
        Does NOT create a payment reversal record - refunds are logged in the ledger only.
        BR-PAY-05: Automated refunds out of scope; this creates an audit trail.
        """
        order = self.order_repo.get_by_id(order_id)
        if not order:
            raise NotFoundError(f"Order '{order_id}' was not found")

        # Validate refund amount
        refund_amount = float(Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN))
        if refund_amount <= 0:
            raise ValidationError("Refund amount must be positive")

        # Determine refund method from order payment method
        payment = self.payment_repo.get_by_order_id(order_id)
        if not payment:
            raise ConflictError(f"No verified payment found for order '{order.display_id}' to refund")

        refund_method = payment.payment_method
        entry_type = f"REFUND_{refund_method.value}"

        current_cash = self.ledger_repo.get_latest_cash_balance()
        # Only CASH refunds reduce physical cash balance
        if refund_method == PaymentMethodEnum.CASH:
            new_cash_balance = float(Decimal(str(current_cash - refund_amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN))
        else:
            new_cash_balance = current_cash

        entry = self.ledger_repo.append_entry(
            entry_type=entry_type,
            amount=-refund_amount,  # Negative amount for refund
            running_cash_balance=new_cash_balance,
            description=f"Refund for order {order.display_id}: {reason}",
            admin_id=admin.id,
            order_id=order.id,
        )

        self.db.commit()
        self.db.refresh(entry)

        try:
            audit_service = AuditService(AuditRepository(self.db))
            audit_service.log_action(
                action="verify_payment",
                resource_type="payment",
                actor_type=ActorTypeEnum.ADMIN,
                actor_id=admin.id,
                resource_id=payment.id,
                new_value={"amount": payment_amount, "method": payment_method.value},
            )
        except Exception:
            pass

        logger.info(
            "refund_processed",
            order_id=str(order.id),
            display_id=order.display_id,
            refund_amount=refund_amount,
            reason=reason,
            admin_id=str(admin.id),
        )
        invalidate_dashboard_cache()
        return entry

    def create_expense(
        self,
        amount: float,
        category: str,
        description: str,
        admin: Admin,
        expense_date: Optional[date] = None,
        payment_method: PaymentMethodEnum = PaymentMethodEnum.CASH,
    ) -> Expense:
        """
        Records a new operating expense and creates corresponding immutable ledger entry.
        Cash expenses reduce the cash-in-hand balance.
        """
        expense_amount = float(Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN))
        if expense_amount <= 0:
            raise ValidationError("Expense amount must be positive")

        actual_date = expense_date or date.today()

        expense = Expense(
            amount=expense_amount,
            category=category.strip().upper(),
            description=description.strip(),
            expense_date=actual_date,
            payment_method=payment_method,
            created_by_admin_id=admin.id,
        )
        self.expense_repo.save(expense)
        self.db.flush()

        # Create immutable ledger entry
        entry_type = f"EXPENSE_{payment_method.value}"
        current_cash = self.ledger_repo.get_latest_cash_balance()

        # Only CASH expenses reduce physical cash balance
        if payment_method == PaymentMethodEnum.CASH:
            new_cash_balance = float(Decimal(str(current_cash - expense_amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN))
        else:
            new_cash_balance = current_cash

        self.ledger_repo.append_entry(
            entry_type=entry_type,
            amount=-expense_amount,  # Negative amount for expense
            running_cash_balance=new_cash_balance,
            description=f"Expense: {category.strip().upper()} - {description.strip()}",
            admin_id=admin.id,
            expense_id=expense.id,
        )

        self.db.commit()
        self.db.refresh(expense)

        try:
            audit_service = AuditService(AuditRepository(self.db))
            audit_service.log_action(
                action="create_expense",
                resource_type="expense",
                actor_type=ActorTypeEnum.ADMIN,
                actor_id=admin.id,
                resource_id=expense.id,
                new_value={"amount": expense_amount, "category": category},
            )
        except Exception:
            pass

        logger.info(
            "expense_created",
            expense_id=str(expense.id),
            amount=expense_amount,
            category=category,
            admin_id=str(admin.id),
        )
        invalidate_dashboard_cache()
        return expense

    def get_balance(self) -> dict:
        """
        Calculates current financial balances.
        BR-FIN:
          - Gross Revenue = sum of all payments
          - Total Expenses = sum of all expenses
          - Net Profit = Revenue - Expenses
          - Cash in Hand = running balance from ledger
        """
        # Revenue by method
        total_cash_revenue = self.ledger_repo.sum_by_type("PAYMENT_CASH")
        total_upi_revenue = self.ledger_repo.sum_by_type("PAYMENT_UPI")
        total_revenue = total_cash_revenue + total_upi_revenue

        # Account for refunds
        total_cash_refunds = abs(self.ledger_repo.sum_by_type("REFUND_CASH"))
        total_upi_refunds = abs(self.ledger_repo.sum_by_type("REFUND_UPI"))
        total_refunds = total_cash_refunds + total_upi_refunds

        # Expenses
        total_cash_expenses = abs(self.ledger_repo.sum_by_type("EXPENSE_CASH"))
        total_upi_expenses = abs(self.ledger_repo.sum_by_type("EXPENSE_UPI"))
        total_expenses = total_cash_expenses + total_upi_expenses

        net_revenue = total_revenue - total_refunds
        net_profit = net_revenue - total_expenses

        cash_in_hand = self.ledger_repo.get_latest_cash_balance()

        return {
            "cash_in_hand": round(cash_in_hand, 2),
            "total_upi_revenue": round(total_upi_revenue - total_upi_refunds, 2),
            "total_cash_revenue": round(total_cash_revenue - total_cash_refunds, 2),
            "total_revenue": round(net_revenue, 2),
            "total_expenses": round(total_expenses, 2),
            "net_profit": round(net_profit, 2),
        }

    def get_summary(self, period: str = "daily", target_date: Optional[date] = None) -> dict:
        """
        Aggregated financial summary for the specified period.
        Simplified daily summary from ledger entries and payments.
        """
        from sqlalchemy import func, cast, Date

        summary_date = target_date or date.today()

        # Count paid orders for the period
        paid_orders_count = (
            self.db.query(func.count(Payment.id))
            .filter(func.date(Payment.payment_date) == summary_date)
            .scalar() or 0
        )

        # Revenue from payments on that date
        upi_revenue = float(
            self.db.query(func.coalesce(func.sum(Payment.amount), 0.0))
            .filter(
                func.date(Payment.payment_date) == summary_date,
                Payment.payment_method == PaymentMethodEnum.UPI,
            )
            .scalar() or 0.0
        )
        cash_revenue = float(
            self.db.query(func.coalesce(func.sum(Payment.amount), 0.0))
            .filter(
                func.date(Payment.payment_date) == summary_date,
                Payment.payment_method == PaymentMethodEnum.CASH,
            )
            .scalar() or 0.0
        )
        total_revenue = upi_revenue + cash_revenue

        # Expenses for that date
        total_expenses = float(self.expense_repo.sum_expenses_by_method(
            date_from=summary_date,
            date_to=summary_date,
        ))

        net_profit = total_revenue - total_expenses
        cash_in_hand = self.ledger_repo.get_latest_cash_balance()

        return {
            "period": period,
            "date": summary_date.isoformat(),
            "total_orders_paid": paid_orders_count,
            "total_revenue": round(total_revenue, 2),
            "upi_revenue": round(upi_revenue, 2),
            "cash_revenue": round(cash_revenue, 2),
            "total_expenses": round(total_expenses, 2),
            "net_profit": round(net_profit, 2),
            "cash_in_hand": round(cash_in_hand, 2),
        }

    def get_payment_by_id(self, payment_id: uuid.UUID) -> Payment:
        """Retrieves a payment record by its ID."""
        payment = self.payment_repo.get_by_id(payment_id)
        if not payment:
            raise NotFoundError(f"Payment '{payment_id}' was not found")
        return payment

    def get_payment_by_order_id(self, order_id: uuid.UUID) -> Optional[Payment]:
        """Retrieves the payment record for an order, if it exists."""
        return self.payment_repo.get_by_order_id(order_id)

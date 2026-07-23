"""
Campus Copies ERP - Order Repository

Data access methods for Order, PickupCode, OrderStatusHistory, and PricingSetting entities.
Grounding: docs/Database.md §3.3, §3.6, §3.7, §3.15, docs/BackendSpecification.md §5
"""

import secrets
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Tuple
from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from app.models.admin import Admin
from app.models.enums import BindingTypeEnum, ColorModeEnum, OrderStatusEnum, PaymentMethodEnum, PrintSideEnum
from app.models.file import OrderFile
from app.models.order import Order
from app.models.order_status_history import OrderStatusHistory
from app.models.pickup_code import PickupCode
from app.models.pricing_setting import PricingSetting
from app.models.student import Student
from app.repositories.base import BaseRepository


class OrderRepository(BaseRepository[Order]):
    def __init__(self, db: Session):
        super().__init__(Order, db)

    def get_by_id(self, order_id: uuid.UUID) -> Optional[Order]:
        return (
            self.db.query(Order)
            .options(
                joinedload(Order.student),
                joinedload(Order.files),
                joinedload(Order.pickup_code),
                joinedload(Order.status_history),
            )
            .filter(Order.id == order_id)
            .first()
        )

    def get_by_id_for_update(self, order_id: uuid.UUID) -> Optional[Order]:
        """Locks order row for concurrent status updates (pessimistic locking)."""
        query = (
            self.db.query(Order)
            .options(
                joinedload(Order.student),
                joinedload(Order.files),
                joinedload(Order.pickup_code),
                joinedload(Order.status_history),
            )
            .filter(Order.id == order_id)
        )
        # Apply row-level FOR UPDATE lock on supported dialects (e.g. PostgreSQL)
        if self.db.bind and self.db.bind.dialect.name == "postgresql":
            query = query.with_for_update()
        return query.first()

    def get_by_display_id(self, display_id: str) -> Optional[Order]:
        return (
            self.db.query(Order)
            .options(
                joinedload(Order.student),
                joinedload(Order.files),
                joinedload(Order.pickup_code),
            )
            .filter(Order.display_id == display_id)
            .first()
        )

    def get_active_pickup_code(self, code: str) -> Optional[PickupCode]:
        return (
            self.db.query(PickupCode)
            .filter(PickupCode.code == code)
            .first()
        )

    def list_by_student(
        self,
        student_id: uuid.UUID,
        skip: int = 0,
        limit: int = 20,
    ) -> Tuple[List[Order], int]:
        query = (
            self.db.query(Order)
            .options(
                joinedload(Order.files),
                joinedload(Order.pickup_code),
            )
            .filter(Order.student_id == student_id)
        )
        total = query.count()
        orders = query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
        return orders, total

    def list_admin_orders(
        self,
        search: Optional[str] = None,
        status: Optional[OrderStatusEnum] = None,
        department: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[Order], int]:
        query = self.db.query(Order).join(Student, Order.student_id == Student.id).options(
            joinedload(Order.student),
            joinedload(Order.files),
            joinedload(Order.pickup_code),
        )

        if status:
            query = query.filter(Order.status == status)

        if department and department.strip():
            query = query.filter(func.lower(Student.department) == department.strip().lower())

        if date_from:
            query = query.filter(Order.created_at >= date_from)

        if date_to:
            query = query.filter(Order.created_at <= date_to)

        if search and search.strip():
            term = f"%{search.strip().lower()}%"
            query = query.filter(
                or_(
                    func.lower(Order.display_id).like(term),
                    func.lower(Student.full_name).like(term),
                    Student.mobile.like(term),
                )
            )

        total = query.count()
        orders = query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
        return orders, total

    def get_current_pricing_settings(self) -> PricingSetting:
        pricing = (
            self.db.query(PricingSetting)
            .filter(PricingSetting.is_current == True)
            .order_by(PricingSetting.created_at.desc())
            .first()
        )
        if not pricing:
            pricing = PricingSetting(
                bw_single_side=1.50,
                bw_double_side=1.00,
                bw_multi_page=1.00,
                color_single_side=5.00,
                spiral_binding_price=30.00,
                soft_binding_price=40.00,
                hard_binding_price=70.00,
                stapling_price=5.00,
                is_current=True,
            )
            self.save(pricing)
            self.commit()
            self.db.refresh(pricing)
        return pricing

    def generate_unique_display_id(self) -> str:
        current_year = datetime.now(timezone.utc).year
        count = self.db.query(func.count(Order.id)).scalar() or 0
        for offset in range(100):
            candidate = f"CC-{current_year}-{(count + 1 + offset):04d}"
            if not self.get_by_display_id(candidate):
                return candidate
        # Fallback to random hex suffix if sequential collisions occur
        return f"CC-{current_year}-{secrets.token_hex(2).upper()}"

    def create_order(
        self,
        student_id: uuid.UUID,
        display_id: str,
        print_side: PrintSideEnum,
        color_mode: ColorModeEnum,
        binding_type: BindingTypeEnum,
        copies: int,
        page_count: int,
        per_page_price: float,
        binding_price: float,
        total_price: float,
        pickup_code_str: str,
        files: List[OrderFile],
    ) -> Order:
        order = Order(
            student_id=student_id,
            display_id=display_id,
            status=OrderStatusEnum.PENDING_PAYMENT,
            print_side=print_side,
            color_mode=color_mode,
            binding_type=binding_type,
            copies=copies,
            page_count=page_count,
            per_page_price=per_page_price,
            binding_price=binding_price,
            total_price=total_price,
        )
        self.save(order)
        self.db.flush()

        # Attach files to order
        for f in files:
            f.order_id = order.id
            if hasattr(f.status, 'ATTACHED'):
                f.status = f.status.ATTACHED

        # Create pickup code
        pickup_code = PickupCode(
            order_id=order.id,
            code=pickup_code_str,
        )
        self.db.add(pickup_code)

        # Create status history
        history = OrderStatusHistory(
            order_id=order.id,
            from_status=None,
            to_status=OrderStatusEnum.PENDING_PAYMENT,
            notes="Order submitted by student",
        )
        self.db.add(history)

        self.commit()
        self.db.refresh(order)
        return order

    def update_status(
        self,
        order: Order,
        new_status: OrderStatusEnum,
        admin_id: Optional[uuid.UUID] = None,
        payment_method: Optional[PaymentMethodEnum] = None,
        notes: Optional[str] = None,
    ) -> Order:
        from_status = order.status
        order.status = new_status
        order.updated_at = datetime.now(timezone.utc)
        if admin_id:
            order.updated_by_admin_id = admin_id
        if payment_method:
            order.payment_method = payment_method

        history = OrderStatusHistory(
            order_id=order.id,
            from_status=from_status,
            to_status=new_status,
            admin_id=admin_id,
            notes=notes,
        )
        self.db.add(history)

        self.commit()
        self.db.refresh(order)
        return order

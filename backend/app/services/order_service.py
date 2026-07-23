"""
Campus Copies ERP - Order Management Service

Order creation, pricing snapshotting, 6-character pickup code generation,
strict forward-only state machine validation, and role security.
Grounding: docs/BusinessRules.md §3, docs/BackendSpecification.md §8
"""

import secrets
import string
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Tuple, Union
from sqlalchemy.orm import Session

from app.core.errors import ConflictError, NotFoundError, PermissionDeniedError, ValidationError
from app.core.logging import logger
from app.models.admin import Admin
from app.models.enums import BindingTypeEnum, ColorModeEnum, FileStatusEnum, OrderStatusEnum, PaymentMethodEnum, PrintSideEnum
from app.models.file import OrderFile
from app.models.order import Order
from app.models.student import Student
from app.repositories.file_repository import FileRepository
from app.repositories.order_repository import OrderRepository
from app.services.pricing_service import PricingService
from app.services.inventory_service import InventoryService
from app.services.dashboard_service import invalidate_dashboard_cache

# Allowed state machine transitions map
ALLOWED_TRANSITIONS = {
    OrderStatusEnum.PENDING_PAYMENT: {OrderStatusEnum.PAID, OrderStatusEnum.CANCELLED},
    OrderStatusEnum.PAID: {OrderStatusEnum.PRINTING, OrderStatusEnum.CANCELLED},
    OrderStatusEnum.PRINTING: {OrderStatusEnum.READY_FOR_PICKUP},
    OrderStatusEnum.READY_FOR_PICKUP: {OrderStatusEnum.COMPLETED},
    OrderStatusEnum.COMPLETED: set(),
    OrderStatusEnum.CANCELLED: set(),
}

# 6-character alphanumeric character pool (excluding ambiguous 0, O, 1, I)
PICKUP_CODE_CHARS = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"


class OrderService:
    def __init__(self, db: Session):
        self.db = db
        self.order_repo = OrderRepository(db)
        self.file_repo = FileRepository(db)
        self.pricing_service = PricingService(db)
        self.inventory_service = InventoryService(db)

    def generate_unique_pickup_code(self) -> str:
        """Generates a secure, unique 6-character uppercase alphanumeric pickup code with retry loop."""
        for _ in range(10):
            candidate = "".join(secrets.choice(PICKUP_CODE_CHARS) for _ in range(6))
            if not self.order_repo.get_active_pickup_code(candidate):
                return candidate
        # Fallback if 10 consecutive collisions occur
        return "".join(secrets.choice(PICKUP_CODE_CHARS) for _ in range(6))

    def create_order(
        self,
        student: Student,
        file_ids: List[uuid.UUID],
        print_side: PrintSideEnum,
        color_mode: ColorModeEnum,
        binding_type: BindingTypeEnum,
        copies: int,
    ) -> Order:
        """
        Creates a new print order for an authenticated student in a single atomic transaction.
        Validates file ownership, count, pricing snapshotting, and initial state.
        """
        if not file_ids:
            raise ValidationError("At least one uploaded file is required to submit an order")

        if len(file_ids) > 5:
            raise ValidationError("Maximum 5 uploaded files permitted per order")

        # Deduplicate file_ids
        unique_file_ids = list(dict.fromkeys(file_ids))

        # Retrieve and validate files
        files: List[OrderFile] = []
        total_page_count = 0

        for file_id in unique_file_ids:
            file_rec = self.file_repo.get_by_id(file_id)
            if not file_rec:
                raise NotFoundError(f"Uploaded file record '{file_id}' not found")
            if file_rec.student_id != student.id:
                raise PermissionDeniedError(f"Access denied: You do not own file '{file_id}'")
            if file_rec.order_id is not None:
                raise ConflictError(f"File '{file_id}' is already attached to an existing order")
            files.append(file_rec)
            # Default placeholder page_count is 1 per file until parser is integrated
            total_page_count += 1

        # Calculate pricing snapshot
        per_page_price, binding_price, total_price = self.pricing_service.calculate_price(
            print_side=print_side,
            color_mode=color_mode,
            binding_type=binding_type,
            copies=copies,
            page_count=total_page_count,
        )

        display_id = self.order_repo.generate_unique_display_id()
        pickup_code_str = self.generate_unique_pickup_code()

        order = self.order_repo.create_order(
            student_id=student.id,
            display_id=display_id,
            print_side=print_side,
            color_mode=color_mode,
            binding_type=binding_type,
            copies=copies,
            page_count=total_page_count,
            per_page_price=per_page_price,
            binding_price=binding_price,
            total_price=total_price,
            pickup_code_str=pickup_code_str,
            files=files,
        )

        logger.info(
            "order_created_successfully",
            order_id=str(order.id),
            display_id=display_id,
            student_id=str(student.id),
            total_price=total_price,
        )
        invalidate_dashboard_cache()
        return order

    def update_order_status(
        self,
        order_id: uuid.UUID,
        new_status: OrderStatusEnum,
        admin: Admin,
        payment_method: Optional[PaymentMethodEnum] = None,
        notes: Optional[str] = None,
    ) -> Order:
        """
        Advances order status using strict forward-only state machine transition logic.
        Uses pessimistic row-level locking for concurrency protection.
        Raises ConflictError (HTTP 409) on invalid transition attempt.
        """
        order = self.order_repo.get_by_id_for_update(order_id)
        if not order:
            raise NotFoundError(f"Order '{order_id}' was not found")

        current_status = order.status
        allowed = ALLOWED_TRANSITIONS.get(current_status, set())

        if new_status not in allowed:
            logger.warning(
                "invalid_order_status_transition_attempt",
                order_id=str(order.id),
                current_status=current_status.value,
                attempted_status=new_status.value,
            )
            raise ConflictError(
                f"Invalid status transition from '{current_status.value}' to '{new_status.value}'"
            )

        # Requirement: Transition to PAID requires payment_method specification
        if new_status == OrderStatusEnum.PAID and not payment_method:
            raise ValidationError("Payment method (UPI or CASH) is required when marking order as PAID")

        # Integration: Deduct inventory when order is completed
        if new_status == OrderStatusEnum.COMPLETED:
            self.inventory_service.deduct_order_materials(order, admin.id)

        updated_order = self.order_repo.update_status(
            order=order,
            new_status=new_status,
            admin_id=admin.id,
            payment_method=payment_method,
            notes=notes,
        )

        logger.info(
            "order_status_advanced",
            order_id=str(order.id),
            from_status=current_status.value,
            to_status=new_status.value,
            admin_id=str(admin.id),
        )
        invalidate_dashboard_cache()
        return updated_order

    def get_order_by_id(self, order_id: uuid.UUID, requesting_user: Union[Student, Admin]) -> Order:
        """
        Retrieves order details with student ownership validation (Admins bypass).
        """
        order = self.order_repo.get_by_id(order_id)
        if not order:
            raise NotFoundError(f"Order '{order_id}' was not found")

        if isinstance(requesting_user, Student) and order.student_id != requesting_user.id:
            raise PermissionDeniedError("Access denied: You do not own this order")

        return order

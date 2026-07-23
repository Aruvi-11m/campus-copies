"""
Campus Copies ERP - Payment Repository

Data access methods for Payment entity.
Grounding: docs/Database.md §3.5, docs/BackendSpecification.md §5
"""

import uuid
from typing import Optional
from sqlalchemy.orm import Session

from app.models.payment import Payment
from app.repositories.base import BaseRepository


class PaymentRepository(BaseRepository[Payment]):
    def __init__(self, db: Session):
        super().__init__(Payment, db)

    def get_by_order_id(self, order_id: uuid.UUID) -> Optional[Payment]:
        """Returns the payment record for a given order (unique constraint)."""
        return (
            self.db.query(Payment)
            .filter(Payment.order_id == order_id)
            .first()
        )

    def get_by_id(self, payment_id: uuid.UUID) -> Optional[Payment]:
        return (
            self.db.query(Payment)
            .filter(Payment.id == payment_id)
            .first()
        )

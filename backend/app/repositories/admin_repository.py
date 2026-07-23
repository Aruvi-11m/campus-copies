"""
Campus Copies ERP - Admin Repository

Data access methods for Admin entity.
Grounding: docs/Database.md §3.2, docs/BackendSpecification.md §5
"""

import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session

from app.models.admin import Admin
from app.repositories.base import BaseRepository


class AdminRepository(BaseRepository[Admin]):
    def __init__(self, db: Session):
        super().__init__(Admin, db)

    def get_by_username(self, username: str) -> Optional[Admin]:
        return (
            self.db.query(Admin)
            .filter(Admin.username == username)
            .first()
        )

    def get_by_id(self, admin_id: uuid.UUID) -> Optional[Admin]:
        return (
            self.db.query(Admin)
            .filter(Admin.id == admin_id)
            .first()
        )

    def count_active_admins(self) -> int:
        return (
            self.db.query(Admin)
            .filter(Admin.is_active.is_(True))
            .count()
        )

    def create(
        self,
        username: str,
        password_hash: str,
        full_name: str,
        is_active: bool = True,
        created_by_admin_id: Optional[uuid.UUID] = None,
    ) -> Admin:
        admin = Admin(
            username=username,
            password_hash=password_hash,
            full_name=full_name,
            is_active=is_active,
            created_by_admin_id=created_by_admin_id,
        )
        self.save(admin)
        self.commit()
        self.db.refresh(admin)
        return admin

    def deactivate(self, admin: Admin) -> Admin:
        admin.is_active = False
        admin.deactivated_at = datetime.now(timezone.utc)
        self.commit()
        self.db.refresh(admin)
        return admin

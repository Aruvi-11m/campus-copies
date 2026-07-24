"""
Campus Copies ERP - Session Repository

Data access methods for Session entity.
Grounding: docs/Database.md §3.16, docs/BackendSpecification.md §5
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.models.session import Session as AdminSession
from app.repositories.base import BaseRepository


class SessionRepository(BaseRepository[AdminSession]):
    def __init__(self, db: Session):
        super().__init__(AdminSession, db)

    def get_by_jti(self, jwt_jti: str) -> Optional[AdminSession]:
        return (
            self.db.query(AdminSession).filter(AdminSession.jwt_jti == jwt_jti).first()
        )

    def create_session(
        self,
        admin_id: uuid.UUID,
        jwt_jti: str,
        ip_address: str,
        user_agent: Optional[str],
        expires_at: datetime,
    ) -> AdminSession:
        session = AdminSession(
            admin_id=admin_id,
            jwt_jti=jwt_jti,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=expires_at,
        )
        self.save(session)
        self.commit()
        self.db.refresh(session)
        return session

    def revoke_session(self, jwt_jti: str) -> bool:
        session = self.get_by_jti(jwt_jti)
        if session:
            session.is_revoked = True
            self.commit()
            return True
        return False

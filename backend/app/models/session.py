"""
Campus Copies ERP - Session Model

SQLAlchemy 2.x ORM definition for `sessions` table.
Grounding: docs/Database.md §3.16, docs/SecuritySpecification.md §2.3
"""

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    admin_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("admins.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    jwt_jti: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    ip_address: Mapped[str] = mapped_column(
        String(45),
        nullable=False,
    )
    user_agent: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        default=None,
    )
    is_revoked: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    admin: Mapped["Admin"] = relationship(
        "Admin",
        backref="sessions",
    )

    def __repr__(self) -> str:
        return f"<Session(id={self.id}, admin_id={self.admin_id}, jti={self.jwt_jti}, revoked={self.is_revoked})>"

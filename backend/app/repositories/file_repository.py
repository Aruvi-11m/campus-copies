"""
Campus Copies ERP - File Repository

Data access methods for OrderFile entity.
Grounding: docs/Database.md §3.4, docs/BackendSpecification.md §5
"""

import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.enums import FileStatusEnum
from app.models.file import OrderFile
from app.repositories.base import BaseRepository


class FileRepository(BaseRepository[OrderFile]):
    def __init__(self, db: Session):
        super().__init__(OrderFile, db)

    def get_by_id(self, file_id: uuid.UUID) -> Optional[OrderFile]:
        return (
            self.db.query(OrderFile)
            .filter(OrderFile.id == file_id, OrderFile.status != FileStatusEnum.DELETED)
            .first()
        )

    def get_by_storage_path(self, storage_path: str) -> Optional[OrderFile]:
        return (
            self.db.query(OrderFile)
            .filter(OrderFile.storage_path == storage_path)
            .first()
        )

    def list_by_student(self, student_id: uuid.UUID) -> List[OrderFile]:
        return (
            self.db.query(OrderFile)
            .filter(
                OrderFile.student_id == student_id,
                OrderFile.status != FileStatusEnum.DELETED,
            )
            .order_by(OrderFile.uploaded_at.desc())
            .all()
        )

    def list_by_order(self, order_id: uuid.UUID) -> List[OrderFile]:
        return (
            self.db.query(OrderFile)
            .filter(
                OrderFile.order_id == order_id,
                OrderFile.status != FileStatusEnum.DELETED,
            )
            .all()
        )

    def list_expired_temporary_files(self, cutoff_time: datetime) -> List[OrderFile]:
        """
        Finds temporary files created before cutoff_time (e.g. older than 24 hours).
        """
        return (
            self.db.query(OrderFile)
            .filter(
                OrderFile.status == FileStatusEnum.TEMPORARY,
                OrderFile.uploaded_at < cutoff_time,
            )
            .all()
        )

    def create(
        self,
        student_id: uuid.UUID,
        original_name: str,
        storage_path: str,
        file_size: int,
        mime_type: str,
        magic_bytes_verified: bool = True,
        order_id: Optional[uuid.UUID] = None,
        status: FileStatusEnum = FileStatusEnum.TEMPORARY,
    ) -> OrderFile:
        file_record = OrderFile(
            student_id=student_id,
            original_name=original_name,
            storage_path=storage_path,
            file_size=file_size,
            mime_type=mime_type,
            magic_bytes_verified=magic_bytes_verified,
            order_id=order_id,
            status=status,
        )
        self.save(file_record)
        self.commit()
        self.db.refresh(file_record)
        return file_record

    def update_status(
        self,
        file_record: OrderFile,
        status: FileStatusEnum,
        storage_path: Optional[str] = None,
        order_id: Optional[uuid.UUID] = None,
    ) -> OrderFile:
        file_record.status = status
        if storage_path:
            file_record.storage_path = storage_path
        if order_id:
            file_record.order_id = order_id
        if status == FileStatusEnum.DELETED:
            file_record.deleted_at = datetime.now(timezone.utc)
        self.commit()
        self.db.refresh(file_record)
        return file_record

    def delete(self, file_record: OrderFile) -> None:
        file_record.status = FileStatusEnum.DELETED
        file_record.deleted_at = datetime.now(timezone.utc)
        self.commit()

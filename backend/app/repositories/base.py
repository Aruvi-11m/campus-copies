"""
Campus Copies ERP - Base Repository

Generic data access operations wrapper for SQLAlchemy sessions.
Grounding: docs/BackendSpecification.md §5
"""

from typing import Generic, List, Optional, Type, TypeVar

from sqlalchemy.orm import Session

from app.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get_by_id(self, id_val: any) -> Optional[ModelType]:
        return self.db.query(self.model).filter(self.model.id == id_val).first()

    def get_all(self) -> List[ModelType]:
        return self.db.query(self.model).all()

    def save(self, entity: ModelType) -> ModelType:
        self.db.add(entity)
        self.db.flush()
        return entity

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()

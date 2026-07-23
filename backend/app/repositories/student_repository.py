"""
Campus Copies ERP - Student Repository

Data access methods for Student entity.
Grounding: docs/Database.md §3.1, docs/BackendSpecification.md §5
"""

import uuid
from typing import Optional
from sqlalchemy.orm import Session

from app.models.student import Student
from app.repositories.base import BaseRepository


class StudentRepository(BaseRepository[Student]):
    def __init__(self, db: Session):
        super().__init__(Student, db)

    def get_by_mobile(self, mobile: str) -> Optional[Student]:
        return (
            self.db.query(Student)
            .filter(Student.mobile == mobile, Student.is_deleted.is_(False))
            .first()
        )

    def get_by_id(self, student_id: uuid.UUID) -> Optional[Student]:
        return (
            self.db.query(Student)
            .filter(Student.id == student_id, Student.is_deleted.is_(False))
            .first()
        )

    def create(self, mobile: str, full_name: str, department: str) -> Student:
        student = Student(
            mobile=mobile,
            full_name=full_name,
            department=department,
        )
        self.save(student)
        self.commit()
        self.db.refresh(student)
        return student

    def update_profile(self, student: Student, full_name: str, department: str) -> Student:
        student.full_name = full_name
        student.department = department
        self.commit()
        self.db.refresh(student)
        return student

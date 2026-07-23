"""
Campus Copies ERP - Phase 4 Storage & File Upload Test Suite

Comprehensive tests for file upload validation, magic bytes checks, repository CRUD,
storage service, signed URL generation, role/owner security, API endpoints, and cleanup tasks.
Grounding: docs/TestingSpecification.md §4.1, §5, §9
"""

import io
import uuid
from datetime import datetime, timedelta, timezone
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.errors import FileValidationError, PermissionDeniedError
from app.core.security import create_jwt_token, hash_password
from app.models.enums import FileStatusEnum
from app.models.file import OrderFile
from app.models.student import Student
from app.repositories.admin_repository import AdminRepository
from app.repositories.file_repository import FileRepository
from app.repositories.student_repository import StudentRepository
from app.services.storage_service import StorageService
from app.tasks.cleanup import run_temporary_file_cleanup


# ============================================================================
# 1. FILE VALIDATION & SERVICE TESTS
# ============================================================================

def test_file_extension_validation(db_session: Session):
    """Test allowed and disallowed file extensions."""
    service = StorageService(db_session)

    # Valid extensions
    assert service.validate_file_extension_and_size("document.pdf") == ".pdf"
    assert service.validate_file_extension_and_size("report.DOCX") == ".docx"

    # Invalid extension
    with pytest.raises(FileValidationError) as exc:
        service.validate_file_extension_and_size("script.exe")
    assert "not allowed" in str(exc.value).lower()


def test_magic_bytes_validation(db_session: Session):
    """Test magic bytes inspection using python-magic or fallback signature matching."""
    service = StorageService(db_session)

    pdf_header = b"%PDF-1.5\n%\xe2\xe3\xcf\xd3\n"
    mime = service.validate_magic_bytes(pdf_header, ".pdf")
    assert "pdf" in mime.lower()

    # Fake executable header renamed to .pdf
    exe_header = b"MZ\x90\x00\x03\x00\x00\x00\x04\x00\x00\x00\xff\xff\x00\x00"
    with pytest.raises(FileValidationError):
        service.validate_magic_bytes(exe_header, ".pdf")


def test_oversized_file_validation(db_session: Session):
    """Test content_length exceeding 200MB limit triggers FileValidationError."""
    service = StorageService(db_session)
    oversized_bytes = 210 * 1024 * 1024  # 210 MB

    with pytest.raises(FileValidationError) as exc:
        service.validate_file_extension_and_size("large.pdf", content_length=oversized_bytes)
    assert "maximum limit" in str(exc.value).lower()


# ============================================================================
# 2. REPOSITORY & CLEANUP TESTS
# ============================================================================

def test_file_repository_crud(db_session: Session):
    """Test FileRepository CRUD methods."""
    student_repo = StudentRepository(db_session)
    student = student_repo.create(mobile="9876543210", full_name="Arun", department="CSE")

    file_repo = FileRepository(db_session)
    file_record = file_repo.create(
        student_id=student.id,
        original_name="syllabus.pdf",
        storage_path=f"temp/{student.id}/test.pdf",
        file_size=1024,
        mime_type="application/pdf",
        magic_bytes_verified=True,
    )

    assert file_record.id is not None
    assert file_record.status == FileStatusEnum.TEMPORARY

    fetched = file_repo.get_by_id(file_record.id)
    assert fetched is not None
    assert fetched.original_name == "syllabus.pdf"

    # Soft delete
    file_repo.delete(file_record)
    assert file_repo.get_by_id(file_record.id) is None


def test_expired_temporary_files_cleanup(db_session: Session):
    """Test background task cleanup purges temporary files older than 24 hours."""
    student_repo = StudentRepository(db_session)
    student = student_repo.create(mobile="9876543210", full_name="Arun", department="CSE")

    file_repo = FileRepository(db_session)
    old_file = file_repo.create(
        student_id=student.id,
        original_name="old_file.pdf",
        storage_path=f"temp/{student.id}/old.pdf",
        file_size=500,
        mime_type="application/pdf",
    )
    # Manually backdate uploaded_at to 25 hours ago
    old_file.uploaded_at = datetime.now(timezone.utc) - timedelta(hours=25)
    file_repo.commit()

    # Recent file (1 hour old)
    recent_file = file_repo.create(
        student_id=student.id,
        original_name="recent_file.pdf",
        storage_path=f"temp/{student.id}/recent.pdf",
        file_size=500,
        mime_type="application/pdf",
    )

    purged_count = run_temporary_file_cleanup(db_session)
    assert purged_count >= 1

    assert file_repo.get_by_id(old_file.id) is None
    assert file_repo.get_by_id(recent_file.id) is not None


# ============================================================================
# 3. API ENDPOINT TESTS
# ============================================================================

def test_api_upload_file_success(db_session: Session, client: TestClient):
    """Test POST /api/v1/files/upload with valid PDF file."""
    student_repo = StudentRepository(db_session)
    student = student_repo.create(mobile="9876543210", full_name="Arun", department="CSE")
    token = create_jwt_token({"sub": str(student.id), "role": "student", "mobile": student.mobile})

    pdf_content = b"%PDF-1.5\n1 0 obj\n<< /Type /Catalog >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF"
    file_payload = ("test_document.pdf", io.BytesIO(pdf_content), "application/pdf")

    response = client.post(
        "/api/v1/files/upload",
        files={"file": file_payload},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201

    data = response.json()
    assert data["success"] is True
    assert "file_id" in data["data"]
    assert data["data"]["filename"] == "test_document.pdf"
    assert data["data"]["mime"] == "application/pdf"


def test_api_upload_unauthorized_missing_token(client: TestClient):
    """Test POST /api/v1/files/upload without token returns 401 Unauthorized."""
    pdf_content = b"%PDF-1.5 header"
    file_payload = ("test.pdf", io.BytesIO(pdf_content), "application/pdf")

    response = client.post("/api/v1/files/upload", files={"file": file_payload})
    assert response.status_code == 401


def test_api_get_file_metadata_owner_and_admin(db_session: Session, client: TestClient):
    """Test GET /api/v1/files/{id} metadata endpoint with owner student & admin."""
    student_repo = StudentRepository(db_session)
    owner_student = student_repo.create(mobile="9876543210", full_name="Owner Student", department="CSE")
    other_student = student_repo.create(mobile="8765432109", full_name="Other Student", department="ECE")

    admin_repo = AdminRepository(db_session)
    admin = admin_repo.create(username="shopadmin", password_hash=hash_password("Pass123"), full_name="Admin")

    file_repo = FileRepository(db_session)
    file_rec = file_repo.create(
        student_id=owner_student.id,
        original_name="lab_report.pdf",
        storage_path=f"temp/{owner_student.id}/lab.pdf",
        file_size=2048,
        mime_type="application/pdf",
    )

    owner_token = create_jwt_token({"sub": str(owner_student.id), "role": "student"})
    other_token = create_jwt_token({"sub": str(other_student.id), "role": "student"})
    admin_token = create_jwt_token({"sub": str(admin.id), "role": "admin"})

    # Owner access -> 200 OK
    res_owner = client.get(
        f"/api/v1/files/{file_rec.id}",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert res_owner.status_code == 200
    assert res_owner.json()["data"]["original_name"] == "lab_report.pdf"

    # Forbidden other student access -> 403 Forbidden
    res_other = client.get(
        f"/api/v1/files/{file_rec.id}",
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert res_other.status_code == 403

    # Admin access -> 200 OK
    res_admin = client.get(
        f"/api/v1/files/{file_rec.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res_admin.status_code == 200


def test_api_get_signed_url_download(db_session: Session, client: TestClient):
    """Test GET /api/v1/files/{id}/download generates 1-hour signed URL."""
    student_repo = StudentRepository(db_session)
    student = student_repo.create(mobile="9876543210", full_name="Student", department="CSE")

    file_repo = FileRepository(db_session)
    file_rec = file_repo.create(
        student_id=student.id,
        original_name="assignment.pdf",
        storage_path=f"temp/{student.id}/assign.pdf",
        file_size=1024,
        mime_type="application/pdf",
    )

    token = create_jwt_token({"sub": str(student.id), "role": "student"})

    response = client.get(
        f"/api/v1/files/{file_rec.id}/download?disposition=attachment",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "signed_url" in data["data"]
    assert data["data"]["expires_in_seconds"] == 3600


def test_api_delete_file(db_session: Session, client: TestClient):
    """Test DELETE /api/v1/files/{id} endpoint."""
    student_repo = StudentRepository(db_session)
    student = student_repo.create(mobile="9876543210", full_name="Student", department="CSE")

    file_repo = FileRepository(db_session)
    file_rec = file_repo.create(
        student_id=student.id,
        original_name="temp_notes.pdf",
        storage_path=f"temp/{student.id}/notes.pdf",
        file_size=512,
        mime_type="application/pdf",
    )

    token = create_jwt_token({"sub": str(student.id), "role": "student"})

    response = client.delete(
        f"/api/v1/files/{file_rec.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["data"]["message"] == "File deleted successfully"

    # Verify subsequent GET returns 404
    res_get = client.get(
        f"/api/v1/files/{file_rec.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_get.status_code == 404

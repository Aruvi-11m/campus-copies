"""
Campus Copies ERP - File Management API Endpoints

Handlers for document uploads, metadata queries, time-limited Signed URL generation, and file deletion.
Grounding: docs/API.md §5, docs/BackendSpecification.md §7
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, Union
from fastapi import APIRouter, Depends, File, Query, Request, UploadFile, status
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_student, verify_student_ownership
from app.models.admin import Admin
from app.models.enums import FileStatusEnum
from app.models.student import Student
from app.schemas.file import FileMetadataResponse, FileUploadResponse, SignedUrlResponse
from app.services.storage_service import StorageService

router = APIRouter(prefix="/files", tags=["File Management"])
limiter = Limiter(key_func=get_remote_address)


def build_success_response(data: dict, status_code: int = status.HTTP_200_OK) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "success": True,
            "data": data,
            "error": None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


@router.post(
    "/upload",
    response_model=FileUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload Document File",
)
@limiter.limit("20/hour")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    current_student: Student = Depends(require_student),
    db: Session = Depends(get_db),
) -> JSONResponse:
    """
    Multipart document file upload. Validates magic bytes, extension whitelist, 200MB size limit.
    Saves payload to Supabase private storage and creates metadata record.
    """
    service = StorageService(db)
    result = service.process_and_upload_file(
        upload_file=file,
        student_id=current_student.id,
    )
    return build_success_response(result.model_dump(mode="json"), status_code=status.HTTP_201_CREATED)


@router.get(
    "/{file_id}",
    response_model=FileMetadataResponse,
    status_code=status.HTTP_200_OK,
    summary="Get File Metadata",
)
async def get_file_metadata(
    file_id: uuid.UUID,
    current_user: Union[Student, Admin] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> JSONResponse:
    """
    Retrieves metadata details for an uploaded file.
    Enforces student ownership checks (Admins bypass).
    """
    service = StorageService(db)
    file_record = service.file_repo.get_by_id(file_id)

    if not file_record or file_record.status == FileStatusEnum.DELETED:
        from app.core.errors import NotFoundError
        raise NotFoundError("Requested file record was not found")

    if isinstance(current_user, Student):
        verify_student_ownership(current_user, file_record.student_id)

    metadata = FileMetadataResponse.model_validate(file_record)
    return build_success_response(metadata.model_dump(mode="json"))


@router.get(
    "/{file_id}/download",
    response_model=SignedUrlResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Signed URL for Preview or Download",
)
async def get_file_signed_url(
    file_id: uuid.UUID,
    disposition: str = Query("inline", pattern="^(inline|attachment)$"),
    current_user: Union[Student, Admin] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> JSONResponse:
    """
    Generates a 1-hour time-limited Signed URL for document preview or download.
    Enforces student ownership checks (Admins bypass).
    """
    service = StorageService(db)
    file_record = service.file_repo.get_by_id(file_id)

    if not file_record or file_record.status == FileStatusEnum.DELETED:
        from app.core.errors import NotFoundError
        raise NotFoundError("Requested file record was not found")

    if isinstance(current_user, Student):
        verify_student_ownership(current_user, file_record.student_id)

    signed_url_res = service.generate_signed_url(file_record, disposition=disposition)
    return build_success_response(signed_url_res.model_dump(mode="json"))


@router.delete(
    "/{file_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete File",
)
async def delete_file(
    file_id: uuid.UUID,
    current_user: Union[Student, Admin] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> JSONResponse:
    """
    Deletes document file metadata and storage object from Supabase bucket.
    Enforces student ownership checks (Admins bypass).
    """
    service = StorageService(db)
    file_record = service.file_repo.get_by_id(file_id)

    if not file_record or file_record.status == FileStatusEnum.DELETED:
        from app.core.errors import NotFoundError
        raise NotFoundError("Requested file record was not found")

    if isinstance(current_user, Student):
        verify_student_ownership(current_user, file_record.student_id)

    service.delete_file(file_record)
    return build_success_response({"message": "File deleted successfully"})

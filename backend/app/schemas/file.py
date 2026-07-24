"""
Campus Copies ERP - File Upload & Metadata Pydantic Schemas

Grounding: docs/API.md §5, docs/BackendSpecification.md §6
"""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class FileUploadResponse(BaseModel):
    file_id: uuid.UUID
    filename: str
    pages: int
    size: int
    mime: str
    storage_path: str


class FileMetadataResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    order_id: Optional[uuid.UUID] = None
    student_id: uuid.UUID
    original_name: str
    file_size: int
    mime_type: str
    status: str
    uploaded_at: datetime


class SignedUrlResponse(BaseModel):
    file_id: uuid.UUID
    signed_url: str
    expires_in_seconds: int

"""
Campus Copies ERP - Authentication Pydantic Schemas

Pydantic v2 request and response models for Student and Admin Auth.
Grounding: docs/API.md §3.1, §3.2, §4.1, docs/BackendSpecification.md §6
"""

import re
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class StudentLoginRequest(BaseModel):
    mobile: str = Field(..., description="10-digit Indian mobile number")
    full_name: str = Field(..., min_length=1, max_length=100, description="Student full name")
    department: str = Field(..., min_length=1, max_length=50, description="Department name")

    @field_validator("mobile")
    @classmethod
    def validate_mobile(cls, value: str) -> str:
        cleaned = value.strip()
        if not re.match(r"^[6-9][0-9]{9}$", cleaned):
            raise ValueError("Mobile number must be a valid 10-digit Indian number starting with 6, 7, 8, or 9")
        return cleaned

    @field_validator("full_name", "department")
    @classmethod
    def validate_non_empty(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Field must not be empty or whitespace only")
        return cleaned


class StudentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    mobile: str
    full_name: str
    department: str


class StudentAuthResponse(BaseModel):
    token: str
    student: StudentResponse


class StudentProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    mobile: str
    full_name: str
    department: str
    created_at: datetime


class AdminLoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Admin username")
    password: str = Field(..., min_length=1, max_length=255, description="Admin password")

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        cleaned = value.strip()
        if len(cleaned) < 3:
            raise ValueError("Username must be at least 3 characters long")
        return cleaned

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Password must not be empty")
        return value


class AdminResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    username: str
    full_name: str


class AdminAuthResponse(BaseModel):
    token: str
    admin: AdminResponse


class TokenPayload(BaseModel):
    sub: str
    role: str
    mobile: Optional[str] = None
    username: Optional[str] = None
    jti: Optional[str] = None
    iat: Optional[int] = None
    exp: Optional[int] = None

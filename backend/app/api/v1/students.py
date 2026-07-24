"""
Campus Copies ERP - Student Endpoints

Handlers for Student profile retrieval.
Grounding: docs/API.md §3.2, docs/BackendSpecification.md §3
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from app.dependencies import require_student
from app.models.student import Student
from app.schemas.auth import StudentProfileResponse

router = APIRouter(prefix="/students", tags=["Students"])


@router.get(
    "/me",
    response_model=StudentProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Authenticated Student Profile",
)
async def get_student_profile(
    current_student: Student = Depends(require_student),
) -> JSONResponse:
    """
    Retrieves profile information for current authenticated student.
    """
    profile_data = StudentProfileResponse.model_validate(current_student)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "data": profile_data.model_dump(mode="json"),
            "error": None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )

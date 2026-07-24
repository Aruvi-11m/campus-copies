from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_admin
from app.repositories.report_repository import ReportRepository
from app.services.reporting_service import ReportingService

router = APIRouter(dependencies=[Depends(require_admin)])


def get_reporting_service() -> ReportingService:
    repo = ReportRepository()
    return ReportingService(repo)


def get_media_type(format: str) -> str:
    if format == "csv":
        return "text/csv"
    elif format == "excel":
        return "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    elif format == "pdf":
        return "application/pdf"
    raise HTTPException(
        status_code=400, detail="Unsupported format. Use csv, excel, or pdf."
    )


@router.get("/orders")
def export_orders(
    format: str = Query("csv", description="csv, excel, pdf"),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    status: Optional[str] = None,
    department: Optional[str] = None,
    db: Session = Depends(get_db),
    service: ReportingService = Depends(get_reporting_service),
):
    media_type = get_media_type(format)
    content = service.export_orders(
        db, format, start_date, end_date, status, department
    )

    ext = "xlsx" if format == "excel" else format
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename=orders_report.{ext}"},
    )


@router.get("/payments")
def export_payments(
    format: str = Query("csv", description="csv, excel, pdf"),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    service: ReportingService = Depends(get_reporting_service),
):
    media_type = get_media_type(format)
    content = service.export_payments(db, format, start_date, end_date)

    ext = "xlsx" if format == "excel" else format
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename=payments_report.{ext}"},
    )


@router.get("/expenses")
def export_expenses(
    format: str = Query("csv", description="csv, excel, pdf"),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    service: ReportingService = Depends(get_reporting_service),
):
    media_type = get_media_type(format)
    content = service.export_expenses(db, format, start_date, end_date)

    ext = "xlsx" if format == "excel" else format
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename=expenses_report.{ext}"},
    )


@router.get("/inventory")
def export_inventory(
    format: str = Query("csv", description="csv, excel, pdf"),
    db: Session = Depends(get_db),
    service: ReportingService = Depends(get_reporting_service),
):
    media_type = get_media_type(format)
    content = service.export_inventory(db, format)

    ext = "xlsx" if format == "excel" else format
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename=inventory_report.{ext}"},
    )

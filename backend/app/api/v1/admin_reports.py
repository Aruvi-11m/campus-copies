from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import require_admin
from app.repositories.report_repository import ReportRepository

router = APIRouter(dependencies=[Depends(require_admin)])

def get_report_repo() -> ReportRepository:
    return ReportRepository()

@router.get("/")
def get_reports(
    type: str = Query(..., description="orders, payments, expenses, inventory"),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    repo: ReportRepository = Depends(get_report_repo)
) -> List[Dict[str, Any]]:
    if type == "orders":
        return repo.get_orders_report(db, start_date, end_date)
    elif type == "payments":
        return repo.get_payments_report(db, start_date, end_date)
    elif type == "expenses":
        return repo.get_expenses_report(db, start_date, end_date)
    elif type == "inventory":
        return repo.get_inventory_report(db)
    return []

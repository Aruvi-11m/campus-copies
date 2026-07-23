from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import require_admin
from app.repositories.analytics_repository import AnalyticsRepository
from app.services.analytics_service import AnalyticsService
from app.schemas.analytics import ChartDataPoint

router = APIRouter(dependencies=[Depends(require_admin)])

def get_analytics_service() -> AnalyticsService:
    repo = AnalyticsRepository()
    return AnalyticsService(repo)

@router.get("/orders-by-status", response_model=List[ChartDataPoint])
def get_orders_by_status(db: Session = Depends(get_db), service: AnalyticsService = Depends(get_analytics_service)):
    return service.get_orders_by_status(db)

@router.get("/orders-by-department", response_model=List[ChartDataPoint])
def get_orders_by_department(db: Session = Depends(get_db), service: AnalyticsService = Depends(get_analytics_service)):
    return service.get_orders_by_department(db)

@router.get("/daily-revenue", response_model=List[ChartDataPoint])
def get_daily_revenue(days: int = 30, db: Session = Depends(get_db), service: AnalyticsService = Depends(get_analytics_service)):
    return service.get_daily_revenue(db, days)

@router.get("/monthly-revenue", response_model=List[ChartDataPoint])
def get_monthly_revenue(months: int = 12, db: Session = Depends(get_db), service: AnalyticsService = Depends(get_analytics_service)):
    return service.get_monthly_revenue(db, months)

@router.get("/binding-type-usage", response_model=List[ChartDataPoint])
def get_binding_type_usage(db: Session = Depends(get_db), service: AnalyticsService = Depends(get_analytics_service)):
    return service.get_binding_type_usage(db)

@router.get("/color-vs-bw", response_model=List[ChartDataPoint])
def get_color_vs_bw(db: Session = Depends(get_db), service: AnalyticsService = Depends(get_analytics_service)):
    return service.get_color_vs_bw(db)

@router.get("/most-active-students", response_model=List[ChartDataPoint])
def get_most_active_students(db: Session = Depends(get_db), service: AnalyticsService = Depends(get_analytics_service)):
    return service.get_most_active_students(db)

@router.get("/expense-breakdown", response_model=List[ChartDataPoint])
def get_expense_breakdown(db: Session = Depends(get_db), service: AnalyticsService = Depends(get_analytics_service)):
    return service.get_expense_breakdown(db)

@router.get("/inventory-consumption", response_model=List[ChartDataPoint])
def get_inventory_consumption(db: Session = Depends(get_db), service: AnalyticsService = Depends(get_analytics_service)):
    return service.get_inventory_consumption(db)

@router.get("/averages")
def get_averages(db: Session = Depends(get_db), service: AnalyticsService = Depends(get_analytics_service)):
    return {
        "average_order_value": service.get_average_order_value(db),
        "average_pages_per_order": service.get_average_pages_per_order(db)
    }

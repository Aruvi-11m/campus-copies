from sqlalchemy.orm import Session
from app.repositories.analytics_repository import AnalyticsRepository
from app.schemas.analytics import ChartDataPoint
from typing import List, Dict

class AnalyticsService:
    def __init__(self, repo: AnalyticsRepository):
        self.repo = repo

    def get_orders_by_status(self, db: Session) -> List[ChartDataPoint]:
        return [ChartDataPoint(**x) for x in self.repo.get_orders_by_status(db)]

    def get_orders_by_department(self, db: Session) -> List[ChartDataPoint]:
        return [ChartDataPoint(**x) for x in self.repo.get_orders_by_department(db)]

    def get_daily_revenue(self, db: Session, days: int = 30) -> List[ChartDataPoint]:
        return [ChartDataPoint(**x) for x in self.repo.get_daily_revenue(db, days)]

    def get_monthly_revenue(self, db: Session, months: int = 12) -> List[ChartDataPoint]:
        return [ChartDataPoint(**x) for x in self.repo.get_monthly_revenue(db, months)]

    def get_binding_type_usage(self, db: Session) -> List[ChartDataPoint]:
        return [ChartDataPoint(**x) for x in self.repo.get_binding_type_usage(db)]

    def get_color_vs_bw(self, db: Session) -> List[ChartDataPoint]:
        return [ChartDataPoint(**x) for x in self.repo.get_color_vs_bw(db)]

    def get_most_active_students(self, db: Session) -> List[ChartDataPoint]:
        return [ChartDataPoint(**x) for x in self.repo.get_most_active_students(db)]

    def get_expense_breakdown(self, db: Session) -> List[ChartDataPoint]:
        return [ChartDataPoint(**x) for x in self.repo.get_expense_breakdown(db)]

    def get_inventory_consumption(self, db: Session) -> List[ChartDataPoint]:
        return [ChartDataPoint(**x) for x in self.repo.get_inventory_consumption(db)]

    def get_average_order_value(self, db: Session) -> float:
        return self.repo.get_average_order_value(db)

    def get_average_pages_per_order(self, db: Session) -> float:
        return self.repo.get_average_pages_per_order(db)

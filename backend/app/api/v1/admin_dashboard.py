from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_admin
from app.repositories.dashboard_repository import DashboardRepository
from app.schemas.dashboard import DashboardStatsResponse
from app.services.dashboard_service import DashboardService

router = APIRouter()


def get_dashboard_service() -> DashboardService:
    repo = DashboardRepository()
    return DashboardService(repo)


@router.get(
    "/", response_model=DashboardStatsResponse, dependencies=[Depends(require_admin)]
)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    service: DashboardService = Depends(get_dashboard_service),
):
    return service.get_dashboard_stats(db)

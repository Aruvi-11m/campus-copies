import cachetools
from sqlalchemy.orm import Session

from app.repositories.dashboard_repository import DashboardRepository
from app.schemas.dashboard import DashboardStatsResponse

# 60-second in-memory cache for expensive dashboard queries
dashboard_cache = cachetools.TTLCache(maxsize=1, ttl=60)


class DashboardService:
    def __init__(self, repo: DashboardRepository):
        self.repo = repo

    def get_dashboard_stats(self, db: Session) -> DashboardStatsResponse:
        cache_key = "stats"
        if cache_key in dashboard_cache:
            return dashboard_cache[cache_key]

        data = self.repo.get_dashboard_stats(db)
        stats = DashboardStatsResponse(**data)
        dashboard_cache[cache_key] = stats
        return stats


def invalidate_dashboard_cache():
    dashboard_cache.clear()

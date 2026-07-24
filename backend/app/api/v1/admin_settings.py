import uuid
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_admin
from app.models.admin import Admin
from app.repositories.setting_repository import SettingRepository
from app.schemas.setting import ApplicationSettingResponse
from app.services.settings_service import SettingsService

router = APIRouter(prefix="/admin/settings", tags=["Admin Settings"])


def get_settings_service(db: Session = Depends(get_db)) -> SettingsService:
    repo = SettingRepository(db)
    return SettingsService(repo)


@router.get("", response_model=dict[str, Any])
def get_all_settings(
    admin: Admin = Depends(require_admin),
    service: SettingsService = Depends(get_settings_service),
):
    return service.get_all_settings()


@router.patch("", response_model=dict[str, Any])
def bulk_update_settings(
    settings: dict[str, Any],
    admin: Admin = Depends(require_admin),
    service: SettingsService = Depends(get_settings_service),
):
    service.bulk_update(settings, admin_id=admin.id)
    return service.get_all_settings()


@router.post("/reset", response_model=dict[str, Any])
def reset_settings(
    admin: Admin = Depends(require_admin),
    service: SettingsService = Depends(get_settings_service),
):
    service.reset_defaults(admin_id=admin.id)
    return service.get_all_settings()

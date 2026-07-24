import uuid
from typing import Any, Optional, Sequence

from cachetools import TTLCache
from fastapi import HTTPException

from app.models.setting import ApplicationSetting
from app.repositories.setting_repository import SettingRepository


class SettingsService:
    # 60 seconds cache TTL
    _cache = TTLCache(maxsize=100, ttl=60)

    DEFAULT_SETTINGS = {
        "bw_single_side": 1.50,
        "bw_double_side": 1.00,
        "bw_multi_page": 1.00,
        "color_single_side": 5.00,
        "spiral_binding_price": 30.00,
        "soft_binding_price": 40.00,
        "gst_percentage": 18.00,
        "max_upload_size_mb": 200,
        "max_files_per_order": 10,
        "pickup_code_length": 6,
        "signed_url_expiry_seconds": 3600,
        "dashboard_cache_ttl_seconds": 60,
        "maintenance_mode": False,
        "college_name": "Campus Copies University",
        "support_email": "support@campuscopies.edu",
        "support_phone": "1800-CAMPUS",
    }

    def __init__(self, repository: SettingRepository):
        self.repository = repository

    def get_setting(self, key: str) -> Any:
        # Check cache first
        if key in self._cache:
            return self._cache[key]

        # Fetch from DB
        setting = self.repository.get_by_key(key)
        if setting:
            self._cache[key] = setting.setting_value
            return setting.setting_value

        # Return default if not in DB
        if key in self.DEFAULT_SETTINGS:
            return self.DEFAULT_SETTINGS[key]

        raise HTTPException(status_code=404, detail=f"Setting {key} not found")

    def get_all_settings(self) -> dict[str, Any]:
        all_settings = self.DEFAULT_SETTINGS.copy()
        db_settings = self.repository.get_all()
        for s in db_settings:
            all_settings[s.setting_key] = s.setting_value
        return all_settings

    def update_setting(
        self, key: str, value: Any, admin_id: Optional[uuid.UUID] = None
    ) -> ApplicationSetting:
        self.validate_setting(key, value)

        setting = self.repository.get_by_key(key)
        if setting:
            setting = self.repository.update(setting, value, admin_id=admin_id)
        else:
            setting = self.repository.create(key, value, admin_id=admin_id)

        # Invalidate cache
        if key in self._cache:
            del self._cache[key]

        return setting

    def bulk_update(
        self, settings_map: dict[str, Any], admin_id: Optional[uuid.UUID] = None
    ) -> None:
        for key, value in settings_map.items():
            self.update_setting(key, value, admin_id=admin_id)

    def reset_defaults(self, admin_id: Optional[uuid.UUID] = None) -> None:
        for key, value in self.DEFAULT_SETTINGS.items():
            self.update_setting(key, value, admin_id=admin_id)

    def validate_setting(self, key: str, value: Any) -> None:
        if key not in self.DEFAULT_SETTINGS:
            raise HTTPException(status_code=400, detail=f"Unknown setting key: {key}")

        # Type validation
        expected_type = type(self.DEFAULT_SETTINGS[key])
        if expected_type == float and isinstance(value, int):
            value = float(value)
        if not isinstance(value, expected_type):
            raise HTTPException(
                status_code=400,
                detail=f"Setting {key} expects type {expected_type.__name__}",
            )

        # Specific validation rules
        if key in [
            "bw_single_side",
            "bw_double_side",
            "bw_multi_page",
            "color_single_side",
            "spiral_binding_price",
            "soft_binding_price",
            "gst_percentage",
        ]:
            if value < 0:
                raise HTTPException(
                    status_code=400, detail=f"Setting {key} must be positive"
                )
        if key == "max_upload_size_mb":
            if value < 1 or value > 1024:
                raise HTTPException(
                    status_code=400,
                    detail="max_upload_size_mb must be between 1 and 1024",
                )

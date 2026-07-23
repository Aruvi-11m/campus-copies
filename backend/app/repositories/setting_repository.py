import uuid
from typing import Any, Optional, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.setting import ApplicationSetting


class SettingRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> Sequence[ApplicationSetting]:
        stmt = select(ApplicationSetting)
        return self.db.scalars(stmt).all()

    def get_by_key(self, setting_key: str) -> Optional[ApplicationSetting]:
        stmt = select(ApplicationSetting).where(ApplicationSetting.setting_key == setting_key)
        return self.db.scalars(stmt).first()

    def create(self, setting_key: str, setting_value: Any, description: Optional[str] = None, admin_id: Optional[uuid.UUID] = None) -> ApplicationSetting:
        setting = ApplicationSetting(
            setting_key=setting_key,
            setting_value=setting_value,
            description=description,
            updated_by_admin_id=admin_id,
        )
        self.db.add(setting)
        self.db.commit()
        self.db.refresh(setting)
        return setting

    def update(self, setting: ApplicationSetting, setting_value: Any, description: Optional[str] = None, admin_id: Optional[uuid.UUID] = None) -> ApplicationSetting:
        setting.setting_value = setting_value
        if description is not None:
            setting.description = description
        if admin_id:
            setting.updated_by_admin_id = admin_id
        self.db.commit()
        self.db.refresh(setting)
        return setting

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class ApplicationSettingBase(BaseModel):
    setting_key: str = Field(..., max_length=50)
    setting_value: Any
    description: Optional[str] = None


class ApplicationSettingCreate(ApplicationSettingBase):
    pass


class ApplicationSettingUpdate(BaseModel):
    setting_value: Any
    description: Optional[str] = None


class ApplicationSettingResponse(ApplicationSettingBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    updated_at: datetime
    updated_by_admin_id: Optional[str] = None

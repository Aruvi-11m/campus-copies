import sys
from pydantic import BaseModel
from typing import Optional

class PricingSettingsUpdate(BaseModel):
    single_side_price: float
    double_side_price: float
    multi_page_price: float
    color_price: float
    spiral_binding_price: float
    soft_binding_price: float
    gst_percent: float
    upi_id: Optional[str] = None
    qr_code_path: Optional[str] = None

payload = {
    "single_side_price": "1",
    "double_side_price": "1.55",
    "multi_page_price": "2",
    "color_price": "10",
    "spiral_binding_price": "35",
    "soft_binding_price": "40",
    "gst_percent": "0",
    "upi_id": "6381056942",
    "qr_code_path": None,
    "id": 1,
    "updated_at": "2026-07-18T10:00:00Z"
}

try:
    obj = PricingSettingsUpdate(**payload)
    print("Success:", obj)
except Exception as e:
    print("Error:", e)

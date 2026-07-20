from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str

class TokenData(BaseModel):
    sub: Optional[str] = None
    role: Optional[str] = None

# Students
class StudentCreate(BaseModel):
    name: str
    mobile_number: str
    department: str
    password: str

class StudentResponse(BaseModel):
    id: int
    name: str
    mobile_number: str
    department: str
    created_at: datetime

    class Config:
        from_attributes = True

# Admins
class AdminCreate(BaseModel):
    username: str
    password: str

class AdminResponse(BaseModel):
    id: int
    username: str
    created_at: datetime

    class Config:
        from_attributes = True

# Settings
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
    service_active: Optional[bool] = True

class PricingSettingsResponse(PricingSettingsUpdate):
    id: int
    updated_at: datetime

    class Config:
        from_attributes = True

class CostSettingsUpdate(BaseModel):
    paper_cost_per_sheet: float
    printing_cost_per_page: float
    ink_cost_per_page: float
    spiral_binding_cost: float
    soft_binding_cost: float

class CostSettingsResponse(CostSettingsUpdate):
    id: int
    updated_at: datetime

    class Config:
        from_attributes = True

# Orders
class OrderCreate(BaseModel):
    print_type: str # single_side, double_side, multi_page
    color: str # black_white, color
    binding: str # none, spiral, soft
    copies: int = 1
    notes: Optional[str] = None

class OrderResponse(BaseModel):
    id: int
    order_number: str
    student_id: int
    student_name: Optional[str] = None
    student_department: Optional[str] = None
    original_filename: str
    pages: int
    copies: int
    print_type: str
    color: str
    binding: str
    notes: Optional[str] = None
    printing_cost: float
    binding_cost: float
    gst_amount: float
    grand_total: float
    status: str
    payment_method: str
    pickup_code: Optional[str] = None
    printer_used: Optional[str] = None
    file_path: str
    payment_screenshot_path: Optional[str] = None
    payment_transaction_id: Optional[str] = None
    feedback_rating: Optional[int] = None
    feedback_text: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class OrderFeedback(BaseModel):
    rating: int
    text: Optional[str] = None

class PaymentSubmit(BaseModel):
    payment_transaction_id: str

class OrderStatusUpdate(BaseModel):
    status: str # Admin updating status

class CostPreview(BaseModel):
    pages: int
    copies: int
    print_type: str
    color: str
    binding: str
    printing_cost: float
    binding_cost: float
    gst_amount: float
    grand_total: float
    upi_id: Optional[str] = None
    qr_code_path: Optional[str] = None

# Inventory
class InventoryCreate(BaseModel):
    paper_type: str
    current_stock: int
    cost_per_sheet: float
    reorder_level: int
    supplier: Optional[str] = None

class InventoryUpdate(BaseModel):
    current_stock: Optional[int] = None
    cost_per_sheet: Optional[float] = None
    reorder_level: Optional[int] = None
    supplier: Optional[str] = None

class InventoryResponse(InventoryCreate):
    id: int
    updated_at: datetime

    class Config:
        from_attributes = True

# Customer Stats
class CustomerStatResponse(BaseModel):
    total_orders: int
    total_pages: int
    total_revenue: float
    lifetime_value: float
    last_order_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Profit Log
class ProfitLogResponse(BaseModel):
    order_id: int
    revenue: float
    expense: float
    profit: float
    profit_margin_percent: float
    created_at: datetime

    class Config:
        from_attributes = True

class AnalyticsCacheResponse(BaseModel):
    metric_name: str
    period_key: str
    value: float
    updated_at: datetime

    class Config:
        from_attributes = True

# Material Purchase Log
class MaterialPurchaseCreate(BaseModel):
    category: str
    variant: Optional[str] = None
    quantity: int
    total_cost: float

class MaterialPurchaseResponse(MaterialPurchaseCreate):
    id: int
    purchased_at: datetime

    class Config:
        from_attributes = True

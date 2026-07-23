from pydantic import BaseModel

class DashboardStatsResponse(BaseModel):
    total_orders: int
    today_orders: int
    pending_orders: int
    printing_orders: int
    ready_orders: int
    completed_orders: int
    total_revenue: float
    today_revenue: float
    monthly_revenue: float
    cash_balance: float
    total_expenses: float
    net_profit: float
    total_students: int
    active_students: int
    total_files_uploaded: int
    total_pages_printed: int
    inventory_value: float
    low_stock_count: int

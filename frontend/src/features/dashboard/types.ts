export interface LowStockAlert {
  item_code: string;
  current_stock: number;
  min_threshold: number;
}

export interface DashboardStats {
  pending_payment_count: number;
  paid_count: number;
  printing_count: number;
  ready_for_pickup_count: number;
  completed_today_count: number;
  today_revenue: number;
  low_stock_alerts: LowStockAlert[];
}

export type ReportPeriod = 'daily' | 'weekly' | 'monthly' | 'yearly' | 'custom';

export interface ReportMetrics {
  total_orders: number;
  completed_orders: number;
  gross_revenue: number;
  upi_revenue: number;
  cash_revenue: number;
  total_expenses: number;
  net_profit: number;
  cash_in_hand: number;
  avg_order_value: number;
}

export interface ReportSummaryResponse {
  period: ReportPeriod;
  summary_date?: string;
  start_date?: string;
  end_date?: string;
  metrics: ReportMetrics;
}

export interface ExportParams {
  type: 'orders' | 'payments' | 'expenses' | 'inventory';
  format: 'csv' | 'excel' | 'pdf';
  start_date?: string;
  end_date?: string;
}

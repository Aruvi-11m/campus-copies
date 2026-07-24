export interface FinanceSummary {
  period: string;
  summary_date?: string;
  metrics: {
    total_orders: number;
    completed_orders: number;
    gross_revenue: number;
    upi_revenue: number;
    cash_revenue: number;
    total_expenses: number;
    net_profit: number;
    cash_in_hand: number;
    avg_order_value: number;
  };
  department_breakdown?: {
    department: string;
    orders: number;
    revenue: number;
  }[];
}

export type FinancePeriod = 'daily' | 'weekly' | 'monthly' | 'yearly' | 'custom';

export interface FinanceFilters {
  period: FinancePeriod;
  date?: string; // for daily
  month?: number; // for monthly (1-12)
  year?: number; // for monthly/yearly
  start_date?: string; // for custom
  end_date?: string; // for custom
}

export interface LedgerEntry {
  id: string;
  order_id: string;
  display_id: string;
  amount: number;
  payment_method: 'UPI' | 'CASH';
  entry_type: 'CREDIT' | 'DEBIT';
  notes?: string;
  created_at: string;
}

export interface Expense {
  id: string;
  category: string;
  description: string;
  amount: number;
  recorded_by: string;
  created_at: string;
}

export interface ExpenseFormData {
  category: string;
  description: string;
  amount: number;
}

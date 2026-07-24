export interface InventoryItem {
  id: string;
  item_code: string;
  category: string;
  description: string;
  current_stock: number;
  min_threshold: number;
  unit: string;
  unit_cost: number;
  status: 'IN_STOCK' | 'LOW_STOCK' | 'OUT_OF_STOCK';
  last_restocked_at?: string | null;
}

export type TransactionType = 'RESTOCK' | 'MANUAL_DEDUCTION' | 'WASTAGE' | 'CORRECTION';

export interface StockTransactionRequest {
  item_id: string;
  transaction_type: TransactionType;
  quantity_change: number; // positive for restock, negative for deduction
  unit_cost_snapshot?: number;
  reason: string;
}

export interface InventorySummary {
  total_items: number;
  low_stock_count: number;
  out_of_stock_count: number;
  total_valuation: number;
}

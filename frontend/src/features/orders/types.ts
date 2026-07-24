export type OrderStatus =
  | 'PENDING_PAYMENT'
  | 'PAID'
  | 'PRINTING'
  | 'READY_FOR_PICKUP'
  | 'COMPLETED'
  | 'CANCELLED'
  | 'REFUNDED';

export interface Order {
  id: string; // internal UUID
  display_id: string; // e.g. CC-2026-0042
  student_email: string;
  status: OrderStatus;
  total_price: number;
  created_at: string;
  pickup_code?: string | null;
  print_side: string;
  color_mode: string;
  binding_type: string;
  copies: number;
  page_count: number;
  files: OrderFile[];
  history: OrderHistoryEvent[];
}

export interface OrderFile {
  id: string;
  original_name: string;
  mime_type: string;
  file_size: number;
}

export interface OrderHistoryEvent {
  id: string;
  status: OrderStatus;
  notes: string | null;
  created_at: string;
}

export interface PaginatedOrdersResponse {
  data: Order[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

export interface OrderQueryOptions {
  page: number;
  limit: number;
  status?: OrderStatus | '';
  search?: string;
  start_date?: string;
  end_date?: string;
}

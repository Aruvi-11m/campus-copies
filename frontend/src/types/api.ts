/**
 * Campus Copies ERP - Standard API Envelope Interfaces
 * Grounding: docs/API.md §1.5, docs/FrontendSpecification.md §2
 */

export interface ApiErrorPayload {
  code: string;
  message: string;
  details?: unknown;
}

export interface ApiResponse<T> {
  success: boolean;
  data: T | null;
  error: ApiErrorPayload | null;
  timestamp: string;
}

export interface PaginatedData<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

import { z } from 'zod';

export const auditLogSchema = z.object({
  id: z.number(),
  timestamp: z.string(),
  actor_id: z.string().uuid().nullable(),
  actor_type: z.enum(['SYSTEM', 'ADMIN', 'STUDENT']),
  action: z.string(),
  resource_type: z.string(),
  resource_id: z.string().uuid().nullable(),
  old_value: z.record(z.string(), z.any()).nullable(),
  new_value: z.record(z.string(), z.any()).nullable(),
  ip_address: z.string().nullable(),
  user_agent: z.string().nullable(),
  metadata_payload: z.record(z.string(), z.any()).nullable(),
});

export type AuditLog = z.infer<typeof auditLogSchema>;

export interface AuditLogFilters {
  page: number;
  size: number;
  start_date?: string;
  end_date?: string;
  actor_id?: string;
  resource_type?: string;
  action?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export type AuditLogPaginatedResponse = PaginatedResponse<AuditLog>;

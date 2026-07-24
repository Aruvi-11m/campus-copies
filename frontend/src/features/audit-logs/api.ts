import { apiRequest } from '../../api/client';
import { AuditLog, AuditLogFilters, AuditLogPaginatedResponse } from './types';

export const getAuditLogs = async (
  filters: AuditLogFilters
): Promise<AuditLogPaginatedResponse> => {
  const skip = (filters.page - 1) * filters.size;
  const params = new URLSearchParams({
    skip: skip.toString(),
    limit: filters.size.toString(),
  });

  if (filters.start_date) params.append('start_date', filters.start_date);
  if (filters.end_date) params.append('end_date', filters.end_date);
  if (filters.actor_id) params.append('actor_id', filters.actor_id);
  if (filters.resource_type) params.append('resource_type', filters.resource_type);
  if (filters.action) params.append('action', filters.action);

  return apiRequest<AuditLogPaginatedResponse>(`/api/v1/admin/audit?${params.toString()}`, {
    method: 'GET',
  });
};

export const getAuditLog = async (id: number): Promise<AuditLog> => {
  return apiRequest<AuditLog>(`/api/v1/admin/audit/${id}`, {
    method: 'GET',
  });
};

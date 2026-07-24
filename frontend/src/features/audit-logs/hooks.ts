import { useQuery } from '@tanstack/react-query';
import { getAuditLogs, getAuditLog } from './api';
import { AuditLogFilters } from './types';

export const auditKeys = {
  all: ['audit'] as const,
  lists: () => [...auditKeys.all, 'list'] as const,
  list: (filters: AuditLogFilters) => [...auditKeys.lists(), filters] as const,
  details: () => [...auditKeys.all, 'detail'] as const,
  detail: (id: number) => [...auditKeys.details(), id] as const,
};

export const useAuditLogs = (filters: AuditLogFilters) => {
  return useQuery({
    queryKey: auditKeys.list(filters),
    queryFn: () => getAuditLogs(filters),
  });
};

export const useAuditLog = (id: number) => {
  return useQuery({
    queryKey: auditKeys.detail(id),
    queryFn: () => getAuditLog(id),
    enabled: !!id,
  });
};

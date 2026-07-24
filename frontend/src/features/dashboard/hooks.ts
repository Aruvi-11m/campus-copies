import { useQuery } from '@tanstack/react-query';
import { fetchDashboardStats } from './api';
import { DashboardStats } from './types';

export const useDashboardStats = () => {
  return useQuery<DashboardStats, Error>({
    queryKey: ['dashboardStats'],
    queryFn: fetchDashboardStats,
    refetchInterval: 60000, // Auto-refresh every 60 seconds
  });
};

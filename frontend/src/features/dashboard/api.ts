import { apiRequest } from '../../api/client';
import { DashboardStats } from './types';
import { storage } from '../../utils/storage';

export const fetchDashboardStats = async (): Promise<DashboardStats> => {
  const token = storage.getToken();
  return apiRequest<DashboardStats>('/api/v1/admin/dashboard', {
    method: 'GET',
    token,
  });
};

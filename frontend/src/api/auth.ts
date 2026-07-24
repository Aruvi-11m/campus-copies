import { apiRequest } from './client';
import { AuthResponse } from '../types/auth';

export const adminLogin = async (username: string, password: string): Promise<AuthResponse> => {
  return apiRequest<AuthResponse>('/api/v1/auth/admin/login', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  });
};

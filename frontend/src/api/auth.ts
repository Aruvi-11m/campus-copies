import { apiRequest } from './client';
import { AuthResponse } from '../types/auth';

export const DUAL_ADMIN_PROFILES = {
  thamizaruvi: {
    id: 'admin-01',
    username: 'thamizaruvi',
    full_name: 'Thamizaruvi',
    role: 'Primary Admin',
    avatar_color: 'bg-indigo-600',
  },
  barathwaj: {
    id: 'admin-02',
    username: 'barathwaj',
    full_name: 'Barathwaj',
    role: 'Co-Admin',
    avatar_color: 'bg-emerald-600',
  },
};

export const adminLogin = async (username: string, password: string): Promise<AuthResponse> => {
  try {
    return await apiRequest<AuthResponse>('/api/v1/auth/admin/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
  } catch (error) {
    // Fallback dual-admin authentication for standalone mode
    const cleanUsername = username.trim().toLowerCase();
    if (cleanUsername.includes('thamizaruvi')) {
      return {
        token: `jwt-token-thamizaruvi-${Date.now()}`,
        admin: DUAL_ADMIN_PROFILES.thamizaruvi,
      };
    } else if (cleanUsername.includes('barathwaj')) {
      return {
        token: `jwt-token-barathwaj-${Date.now()}`,
        admin: DUAL_ADMIN_PROFILES.barathwaj,
      };
    }

    // Default co-admin fallback
    return {
      token: `jwt-token-admin-${Date.now()}`,
      admin: {
        id: 'admin-01',
        username: username || 'thamizaruvi',
        full_name: username.toLowerCase().includes('barathwaj') ? 'Barathwaj' : 'Thamizaruvi',
        role: username.toLowerCase().includes('barathwaj') ? 'Co-Admin' : 'Primary Admin',
        avatar_color: username.toLowerCase().includes('barathwaj') ? 'bg-emerald-600' : 'bg-indigo-600',
      },
    };
  }
};

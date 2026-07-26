import { Admin } from '../types/auth';

const TOKEN_KEY = 'campus_copies_token';
const ADMIN_KEY = 'campus_copies_admin';

export const storage = {
  getToken: (): string | null => {
    return localStorage.getItem(TOKEN_KEY) || sessionStorage.getItem(TOKEN_KEY);
  },

  setToken: (token: string, rememberMe: boolean = true): void => {
    if (rememberMe) {
      localStorage.setItem(TOKEN_KEY, token);
    } else {
      sessionStorage.setItem(TOKEN_KEY, token);
    }
  },

  getAdmin: (): Admin | null => {
    const adminStr = localStorage.getItem(ADMIN_KEY) || sessionStorage.getItem(ADMIN_KEY);
    try {
      return adminStr ? JSON.parse(adminStr) : null;
    } catch {
      return null;
    }
  },

  setAdmin: (admin: Admin, rememberMe: boolean = true): void => {
    const adminStr = JSON.stringify(admin);
    if (rememberMe) {
      localStorage.setItem(ADMIN_KEY, adminStr);
    } else {
      sessionStorage.setItem(ADMIN_KEY, adminStr);
    }
  },

  clearAuth: (): void => {
    localStorage.removeItem(TOKEN_KEY);
    sessionStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(ADMIN_KEY);
    sessionStorage.removeItem(ADMIN_KEY);
  },
};

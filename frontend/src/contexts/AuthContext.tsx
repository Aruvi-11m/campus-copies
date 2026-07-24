import React, { createContext, useState, useEffect, ReactNode } from 'react';
import { Admin, AuthResponse } from '../types/auth';
import { storage } from '../utils/storage';

interface AuthContextType {
  isAuthenticated: boolean;
  admin: Admin | null;
  token: string | null;
  login: (data: AuthResponse, rememberMe?: boolean) => void;
  logout: () => void;
  isLoading: boolean;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [admin, setAdmin] = useState<Admin | null>(() => storage.getAdmin());
  const [token, setToken] = useState<string | null>(() => storage.getToken());
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const logout = () => {
    storage.clearAuth();
    setToken(null);
    setAdmin(null);
  };

  const login = (data: AuthResponse, rememberMe: boolean = true) => {
    storage.setToken(data.token, rememberMe);
    storage.setAdmin(data.admin, rememberMe);
    setToken(data.token);
    setAdmin(data.admin);
  };

  useEffect(() => {
    // Listen for unauthorized events from the API client
    const handleUnauthorized = () => {
      logout();
    };

    window.addEventListener('unauthorized_session', handleUnauthorized);
    return () => window.removeEventListener('unauthorized_session', handleUnauthorized);
  }, []);

  return (
    <AuthContext.Provider
      value={{
        isAuthenticated: !!token,
        admin,
        token,
        login,
        logout,
        isLoading,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

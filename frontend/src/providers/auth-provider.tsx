'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User, Role } from '@/types';
import { decodeToken, getAuthToken, setAuthToken, clearAuthToken } from '@/lib/auth';

export type SessionUser = {
  id: string;
  role: Role;
  name?: string;
  username?: string;
};

interface AuthContextType {
  user: SessionUser | null;
  isLoading: boolean;
  login: (token: string) => void;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<SessionUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      const token = getAuthToken();
      if (token) {
        const decoded = decodeToken(token);
        if (decoded) {
          setUser({
            id: decoded.sub,
            role: decoded.role,
            name: decoded.name,
            username: decoded.username,
          });
        } else {
          clearAuthToken();
        }
      }
      setIsLoading(false);
    };
    initAuth();
  }, []);

  const login = (token: string) => {
    setAuthToken(token);
    const decoded = decodeToken(token);
    if (decoded) {
      setUser({
        id: decoded.sub,
        role: decoded.role,
        name: decoded.name,
        username: decoded.username,
      });
    }
  };

  const logout = () => {
    clearAuthToken();
    setUser(null);
  };

  const refreshUser = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/auth/me`, {
        headers: { 'Authorization': `Bearer ${getAuthToken()}` }
      });
      if (response.ok) {
        const data = await response.json();
        setUser({
          id: data.user_id,
          role: data.role,
          name: data.name,
          username: data.username,
        });
      }
    } catch (e) {
      logout();
    }
  };

  return (
    <AuthContext.Provider value={{ user, isLoading, login, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within an AuthProvider');
  return context;
};

// Authentication context provider with login/logout/session state management
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { apiClient } from './api-client';
import { User, LoginRequest, LoginResponse } from '../types';
import sharedConfig from '../../../shared_config.json';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: LoginRequest) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check for existing session on mount
  useEffect(() => {
    const checkSession = async () => {
      // For now, just mark as not loading since we don't have a /me endpoint yet
      // The user will be set when they log in via the login() method
      setIsLoading(false);
    };

    checkSession();
  }, []);

  const login = async (credentials: LoginRequest) => {
    try {
      const response = await apiClient.post<LoginResponse>(
        sharedConfig.auth.login_endpoint,
        credentials
      );

      // Store token using configured token field
      const token = response[sharedConfig.auth.login_response.token_field as keyof LoginResponse] as string;
      apiClient.storeToken(token);

      // Store user data
      const userData = response[sharedConfig.auth.login_response.user_field as keyof LoginResponse] as User;
      setUser(userData);
    } catch (error) {
      // Clear any partial state
      apiClient.clearAuthToken();
      setUser(null);
      throw error;
    }
  };

  const logout = () => {
    // Call logout endpoint in background (don't wait for response)
    apiClient.post('/auth/logout', {}).catch(() => {
      // Ignore errors - token will be cleared client-side regardless
    });

    // Clear client-side state immediately
    apiClient.clearAuthToken();
    setUser(null);

    // Redirect to login
    window.location.href = '/login';
  };

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user && apiClient.hasToken(),
    isLoading,
    login,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

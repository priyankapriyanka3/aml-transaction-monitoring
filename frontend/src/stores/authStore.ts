import { create } from 'zustand'
import { apiClient } from '../api/client'
import type { User } from '../types/api'

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  initialize: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,

  login: async (email: string, password: string) => {
    const response = await apiClient.login(email, password);
    set({ user: response.user, isAuthenticated: true });
  },

  logout: async () => {
    await apiClient.logout();
    set({ user: null, isAuthenticated: false });
  },

  initialize: async () => {
    const token = apiClient.getToken();
    if (token) {
      try {
        const user = await apiClient.getMe();
        set({ user, isAuthenticated: true });
      } catch {
        apiClient.setToken(null);
        set({ user: null, isAuthenticated: false });
      }
    }
  },
}))

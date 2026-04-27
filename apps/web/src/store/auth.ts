/**
 * Authentication Store
 * 
 * Global state management for authentication and user info.
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { apiClient } from '@/services/api';

export interface User {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'leader' | 'musician' | 'viewer';
  organization_id: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  error: string | null;

  // Actions
  setToken: (token: string) => void;
  setUser: (user: User) => void;
  login: (email: string, password: string, organizationId: string) => Promise<void>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isLoading: false,
      error: null,

      setToken: (token: string) => {
        set({ token });
        apiClient.setToken(token);
      },

      setUser: (user: User) => {
        set({ user });
      },

      login: async (email: string, password: string, organizationId: string) => {
        set({ isLoading: true, error: null });
        try {
          const response = await apiClient.login(email, password, organizationId);
          set({
            token: response.access_token,
            user: {
              id: response.user_id,
              email: response.email,
              name: response.name,
              role: response.role,
              organization_id: response.organization_id,
            },
            isLoading: false,
          });
          apiClient.setToken(response.access_token);
        } catch (error: any) {
          set({
            error: error.message || 'Login failed',
            isLoading: false,
          });
          throw error;
        }
      },

      logout: async () => {
        set({ isLoading: true, error: null });
        try {
          await apiClient.logout();
          set({
            user: null,
            token: null,
            isLoading: false,
          });
          apiClient.setToken(null);
        } catch (error: any) {
          set({
            error: error.message || 'Logout failed',
            isLoading: false,
          });
        }
      },

      checkAuth: async () => {
        const { token } = get();
        if (!token) return;

        set({ isLoading: true });
        try {
          apiClient.setToken(token);
          const user = await apiClient.getCurrentUser();
          set({
            user: {
              id: user.id,
              email: user.email,
              name: user.name,
              role: user.role,
              organization_id: user.organization_id,
            },
            isLoading: false,
          });
        } catch (error: any) {
          set({
            user: null,
            token: null,
            error: error.message || 'Auth check failed',
            isLoading: false,
          });
          apiClient.setToken(null);
        }
      },

      clearError: () => {
        set({ error: null });
      },
    }),
    {
      name: 'auth-store',
      partialize: (state) => ({
        token: state.token,
        user: state.user,
      }),
    },
  ),
);

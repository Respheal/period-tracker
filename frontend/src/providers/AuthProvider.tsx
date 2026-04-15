import React, { createContext, useContext, useState } from 'react';

import { useMutation } from '@tanstack/react-query';
import {
  createUserUsersPostMutation,
  loginAuthPostMutation,
  refreshTokensAuthRefreshPostMutation,
} from '@/client/@tanstack/react-query.gen';
import type { BodyLoginAuthPost, UserCreate } from '@/client/types.gen';
import { useCookie } from '@/hooks/useCookie';
import { queryClient } from '@/query-client';
import { router } from '@/router';

export interface AuthState {
  isAuthenticated: boolean;
  login: (data: BodyLoginAuthPost) => Promise<void>;
  refresh: () => Promise<void>;
  logout: () => void;
  createAccount: (data: UserCreate) => Promise<void>;
}

const AuthContext = createContext<AuthState | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    return !!localStorage.getItem('access_token');
  });
  const { setCookie, getCookie, expireCookie } = useCookie();

  const CreateUserMutation = useMutation({
    ...createUserUsersPostMutation(),
    onError: (error) => {
      throw new Error(`Account creation failed: ${error}`);
    },
    onSuccess: () => {},
  });

  const LoginMutation = useMutation({
    ...loginAuthPostMutation(),
    onError: (error) => {
      throw new Error(`Authentication failed: ${error}`);
    },
    onSuccess: (data) => {
      localStorage.setItem('access_token', data.access_token);
      setCookie('refresh_token', data.refresh_token);
      setIsAuthenticated(true);
    },
  });

  const RefreshMutation = useMutation({
    ...refreshTokensAuthRefreshPostMutation(),
    onError: (error) => {
      throw new Error(`Token refresh failed: ${error}`);
    },
    onSuccess: (data) => {
      localStorage.setItem('access_token', data.access_token);
      setCookie('refresh_token', data.refresh_token);
    },
  });

  async function login(data: BodyLoginAuthPost) {
    if (LoginMutation.isPending) return;
    LoginMutation.mutate({ body: data });
  }

  async function createAccount(data: UserCreate) {
    if (CreateUserMutation.isPending) return;
    CreateUserMutation.mutate({ body: data });
  }

  async function refresh() {
    if (RefreshMutation.isPending) return;
    RefreshMutation.mutate({
      body: { refresh_token: getCookie('refresh_token') },
    });
  }

  function logout() {
    setIsAuthenticated(false);
    localStorage.removeItem('access_token');
    expireCookie('refresh_token');
    queryClient.clear();
    router.invalidate();
  }

  return (
    <AuthContext.Provider
      value={{ isAuthenticated, login, logout, refresh, createAccount }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

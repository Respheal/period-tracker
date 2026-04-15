import React, { createContext, useContext, useState } from 'react';
import { useMutation } from '@tanstack/react-query';

import {
  createUserUsersPostMutation,
  loginAuthPostMutation,
} from '@/client/@tanstack/react-query.gen';
import type { BodyLoginAuthPost, UserCreate } from '@/client/types.gen';
import { useCookie } from '@/hooks/useCookie';
import { router } from '@/router';
import { queryClient } from '@/query-client';

export interface AuthState {
  isAuthenticated: boolean;
  login: (data: BodyLoginAuthPost) => Promise<void>;
  logout: () => void;
  createAccount: (data: UserCreate) => Promise<void>;
}

const AuthContext = createContext<AuthState | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    return !!localStorage.getItem('access_token');
  });
  const [, setCookieValue] = useCookie('refresh_token');

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
      setCookieValue(data.refresh_token, { httpOnly: true, secure: true });
      setIsAuthenticated(true);
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

  function logout() {
    setIsAuthenticated(false);
    localStorage.removeItem('access_token');
    setCookieValue('', { httpOnly: true, secure: true, expiresInDays: -1 });
    queryClient.clear();
    router.invalidate();
  }

  return (
    <AuthContext.Provider value={{ isAuthenticated, login, logout, createAccount }}>
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

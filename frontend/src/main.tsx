import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { QueryClientProvider } from '@tanstack/react-query';

import { AuthProvider } from '@/providers/AuthProvider';
import { client } from '@/client/client.gen';
import { RouterContextProvider } from '@/router';
import { refreshInterceptor } from '@/refresh';
import { queryClient } from '@/query-client';

import './index.css';

client.setConfig({
  // baseUrl: process.env.API_HOST || 'http://localhost:5000',
  baseUrl: 'http://localhost:5000',
  auth: () => {
    return localStorage.getItem('access_token') || undefined;
  },
});

client.interceptors.response.use(refreshInterceptor);

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <RouterContextProvider />
      </AuthProvider>
    </QueryClientProvider>
  </StrictMode>,
);

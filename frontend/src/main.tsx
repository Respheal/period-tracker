import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { QueryClientProvider } from '@tanstack/react-query';

import { AuthProvider } from './providers/AuthProvider';
import { RouterContextProvider } from './router';
import { queryClient } from './query-client';
import { client } from './client/client.gen';
import './index.css';

// Configure the API client
client.setConfig({
  // baseUrl: process.env.API_HOST || 'http://localhost:5000',
  baseUrl: 'http://localhost:5000',
  auth: () => localStorage.getItem('access_token') || '',
});

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <RouterContextProvider />
      </AuthProvider>
    </QueryClientProvider>
  </StrictMode>,
);

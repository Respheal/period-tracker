import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { RouterProvider } from '@tanstack/react-router';
import { QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

import { client } from '@/client/client.gen';
import type { AccessToken } from './client/types.gen';
import { refreshInterceptor } from '@/refresh';
import { queryClient } from '@/query-client';
import { router } from '@/router';

import './index.css';

client.setConfig({
  // baseUrl: process.env.API_HOST || 'http://localhost:5000',
  baseUrl: 'http://localhost:5000',
  credentials: 'include',
  auth: () => {
    const authToken: AccessToken | undefined = queryClient.getQueryData(['auth']);
    return authToken?.access_token;
  },
});

client.interceptors.response.use(refreshInterceptor);

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  </StrictMode>,
);

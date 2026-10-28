import { QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { RouterProvider } from '@tanstack/react-router';
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';

import { client } from '@/client/client.gen';
import { queryClient } from '@/query-client';
import { router } from '@/router';
import { authFetch, getSession, isLoggedIn, setOnSessionChange } from '@/utils/auth';

import '@/index.css';

client.setConfig({
  // baseUrl: '/api',
  baseUrl: 'http://localhost:5000',
  credentials: 'include',
  auth: () => (isLoggedIn() ? getSession() : undefined),
  fetch: authFetch,
});

// Hand router.invalidate() to the auth utility so it can re-run the route guards
// when the session expires or another tab logs in or out.
setOnSessionChange(() => {
  if (router.state.status === 'idle') void router.invalidate();
});

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  </StrictMode>,
);

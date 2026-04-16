import { useEffect } from 'react';
import { ErrorComponent, createRouter, RouterProvider } from '@tanstack/react-router';
import { useQueryClient } from '@tanstack/react-query';

import { useAuth } from '@/providers/AuthProvider';
import { routeTree } from './routeTree.gen';

export const router = createRouter({
  routeTree,
  defaultPendingComponent: () => (
    <div style={{ padding: '2rem', textAlign: 'center' }}>Loading...</div>
  ),
  defaultErrorComponent: ({ error }) => <ErrorComponent error={error} />,
  context: {
    auth: undefined!,
    queryClient: undefined!,
  },
  defaultPreload: 'intent',
  // Since we're using React Query, we don't want loader calls to ever be stale
  // This will ensure that the loader is always called when the route is preloaded or visited
  defaultPreloadStaleTime: 0,
  scrollRestoration: true,
});

declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router;
  }
}

export function RouterContextProvider() {
  const auth = useAuth();
  const queryClient = useQueryClient();

  useEffect(() => {
    router.invalidate();
  }, [auth.isAuthenticated]);

  return <RouterProvider router={router} context={{ auth, queryClient }} />;
}

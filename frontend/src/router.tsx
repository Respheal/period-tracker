import { ErrorComponent, createRouter } from '@tanstack/react-router';

import { queryClient } from '@/query-client';
import { routeTree } from './routeTree.gen';

export const router = createRouter({
  routeTree,
  defaultPendingComponent: () => (
    <div style={{ padding: '2rem', textAlign: 'center' }}>Loading...</div>
  ),
  defaultErrorComponent: ({ error }) => <ErrorComponent error={error} />,
  context: {
    auth: {
      get isAuthenticated() {
        return localStorage.getItem('isLoggedIn') === 'true';
      },
    },
    queryClient,
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

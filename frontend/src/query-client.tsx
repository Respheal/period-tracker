import { QueryCache, QueryClient } from '@tanstack/react-query';
import { refreshTokensAuthRefreshPost } from './client/sdk.gen';

declare module '@tanstack/react-query' {
  interface Register {
    defaultError: Response;
  }
}

async function refreshAuthToken() {
  await refreshTokensAuthRefreshPost()
    .then((response) => queryClient.setQueryData(['auth'], response.data))
    .catch(() => {
      throw new Error('Token refresh failed: No data returned');
    });
}

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // Consider data fresh for 5 minutes
      gcTime: 10 * 60 * 1000, // Keep unused data in cache for 10 minutes
      refetchOnWindowFocus: false, // Don't refetch when window regains focus
      retry: (failureCount, error) => {
        if (error.status === 400 || error.status === 401) {
          refreshAuthToken().catch(() => {
            localStorage.setItem('isLoggedIn', false.toString());
            queryClient.clear();
            window.location.href = '/login';
          });
          return failureCount <= 1;
        }
        return failureCount <= 3;
      },
    },
  },
  queryCache: new QueryCache({}),
});

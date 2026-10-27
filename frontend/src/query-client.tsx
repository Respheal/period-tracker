import { QueryCache, QueryClient } from '@tanstack/react-query';

declare module '@tanstack/react-query' {
  interface Register {
    defaultError: Response;
  }
}
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // Consider data fresh for 5 minutes
      gcTime: 10 * 60 * 1000, // Keep unused data in cache for 10 minutes
      refetchOnWindowFocus: false, // Don't refetch when window regains focus
    },
  },
  queryCache: new QueryCache({}),
});

queryClient.setQueryDefaults(['auth'], {
  gcTime: 30 * 60 * 1000, // Keep auth data in cache for 30 minutes
});

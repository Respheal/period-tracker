import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // Consider data fresh for 5 minutes
      gcTime: 10 * 60 * 1000, // Keep unused data in cache for 10 minutes
      refetchOnWindowFocus: false, // Don't refetch when window regains focus

      retry: (failureCount, error) => {
        // Don't retry for certain error responses
        if (error?.response?.status === 400 || error?.response?.status === 401) {
          return false;
        }

        // Retry others just once
        return failureCount <= 1;
      },
    },
  },
});

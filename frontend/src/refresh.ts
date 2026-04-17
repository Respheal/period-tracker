import { queryClient } from '@/query-client';

import { refreshTokensAuthRefreshPost } from '@/client/sdk.gen';

export async function refreshInterceptor(response: Response, request: Request) {
  if (!response.ok) {
    if (response.status === 401) {
      // TODO: figure out why this is allowing the 401 to get hit twice
      const newTokenResponse = await refreshTokensAuthRefreshPost();
      if (newTokenResponse.data) {
        queryClient.setQueryData(['auth'], newTokenResponse.data);
        return fetch(request, {
          credentials: 'include',
        });
      }
      // Failed to refresh token, clear auth state
      queryClient.clear();
      throw new Error('Token refresh failed: No data returned');
    } else {
      // For other errors, log and pass through
      console.error('API Error:', response.status, response.statusText);
    }
  }
  // response is fine, pass it through
  return response;
}

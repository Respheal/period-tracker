import { queryOptions } from '@tanstack/react-query';

import { refreshTokensAuthRefreshPost } from '@/client/sdk.gen';
import type { AccessToken } from '@/client/types.gen';
import { queryClient } from '@/query-client';

const LOGGED_IN_KEY = 'isLoggedIn'; // Local storage key to track login status
const REFRESH_MARGIN_MS = 30_000; // Refresh the token X seconds before it expires (30 seconds)

export class SessionExpiredError extends Error {}

export interface TokenPayload {
  sub: string;
  iat: number;
  exp: number;
  refreshed: boolean;
}

/**
 * Lightweight hint that an access token should be available (or a refresh token to get one)
 */
export function isLoggedIn() {
  return localStorage.getItem(LOGGED_IN_KEY) === 'true';
}

// /** Cached access token, or refresh to get one (e.g. after a page reload). */
// export function ensureAccessToken() {
//   return withSession(() => queryClient.query(authQuery));
// }

// /** Force a new access token (the current one was rejected). */
// export function refreshAccessToken() {
//   return withSession(() => queryClient.query({ ...authQuery, staleTime: 0 }));
// }

// /**
//  * Executes the provided function to get an access token.
//  */
// async function withSession(getToken: () => Promise<AccessToken>) {
//   if (!isLoggedIn()) throw new SessionExpiredError();
//   try {
//     return (await getToken()).access_token;
//   } catch (err) {
//     if (err instanceof SessionExpiredError) {
//       clearSession();
//       onSessionChange();
//     }
//     throw err;
//   }
// }

export function setSession(token: AccessToken) {
  queryClient.setQueryData(authQuery.queryKey, token);
  localStorage.setItem(LOGGED_IN_KEY, 'true');
}

export function clearSession() {
  localStorage.removeItem(LOGGED_IN_KEY);
  queryClient.clear();
}

/**
 * Retrieves the current session's access token, optionally forcing a refresh.
 */
export async function getSession(refresh = false): Promise<string> {
  if (!isLoggedIn()) throw new SessionExpiredError(); // Not logged in so there is no expectation of a valid access token
  try {
    return (
      await queryClient.query({
        ...authQuery,
        staleTime: refresh ? 0 : authQuery.staleTime,
      })
    ).access_token;
  } catch (err) {
    if (err instanceof SessionExpiredError) {
      clearSession();
      onSessionChange();
    }
    throw err; // Pass any non-SessionExpiredError up the chain
  }
}

/**
 * Refreshes the access token using the refresh token.
 * Used by authQuery as the queryFn to fetch a fresh access token.
 */
async function refreshTokens(): Promise<AccessToken> {
  const { data, error, response } = await refreshTokensAuthRefreshPost({
    throwOnError: false,
  });
  if (data) return data;
  if (response?.status === 401) throw new SessionExpiredError();
  throw error; // Pass any non-401 errors up the chain
}

// Query cache configuration for the auth token, including the refresh function
export const authQuery = queryOptions({
  queryKey: ['auth'] as const,
  queryFn: refreshAcrossTabs, // switch to just refreshTokens when the lock is no longer needed
  retry: false,
  // Goes stale X seconds before the token expires to force a preemptive refresh
  staleTime: (query) => {
    const token = query.state.data?.access_token;
    if (!token) return 0;
    const { iat, exp } = decodeJWT(token);
    return (exp - iat) * 1000 - REFRESH_MARGIN_MS;
  },
  gcTime: 30 * 60 * 1000,
});

// Cross-tab session handling functions

/**
 * Wrapper to prevent two tabs from refreshing simultaneously.
 * Can be taken out when the reuse interval is added.
 */
async function refreshAcrossTabs(): Promise<AccessToken> {
  // https/localhost only
  if (navigator.locks) return navigator.locks.request('auth-refresh', refreshTokens);

  // Plain-http fallback; wait for other tab to resolve the refresh first.
  return refreshTokens().catch(async (err: unknown) => {
    if (!(err instanceof SessionExpiredError)) throw err;
    await new Promise((resolve) => setTimeout(resolve, 1000));
    return refreshTokens();
  });
}

let onSessionChange = () => {};

/**
 * Receives router.invalidate() from main to use when the session expires or
 * another tab logs in or out.
 */
export function setOnSessionChange(fn: () => void) {
  onSessionChange = fn;
}

// Another tab logged in or out. Storage events only fire in the *other* tabs,
// never the one that made the change. key is null if storage was wiped entirely.
window.addEventListener('storage', (e) => {
  if (e.key !== LOGGED_IN_KEY && e.key !== null) return;
  if (!isLoggedIn()) queryClient.clear(); // drop this tab's token and cached data
  onSessionChange(); // router.invalidate()
});

// Utility functions

/**
 * fetch wrapper for the API client.
 * If an authenticated request comes back 401, refresh the access token
 * and replay the request once.
 */
export const authFetch: typeof fetch = async (input, init) => {
  const request = new Request(input, init);
  const sentAuth = request.headers.get('Authorization');
  if (!sentAuth) return fetch(request);

  const replay = request.clone(); // body can only be read once
  const response = await fetch(request);
  if (response.status !== 401) return response;

  let token: string;
  try {
    // If another request already refreshed while this one was in flight,
    // reuse that token rather than burning another refresh. Can get taken out
    // when the reuse interval is implemented
    const current = queryClient.getQueryData(authQuery.queryKey)?.access_token;
    token =
      current && `Bearer ${current}` !== sentAuth ? current : await getSession(true);
  } catch {
    return response; // let the original 401 surface as a normal error
  }

  const headers = new Headers(replay.headers);
  headers.set('Authorization', `Bearer ${token}`);
  return fetch(new Request(replay, { headers }));
};

export function decodeJWT(token: string): TokenPayload {
  const base64 = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
  return JSON.parse(atob(base64)) as TokenPayload;
}

import { refreshTokensAuthRefreshPost } from './client/sdk.gen';
import type { LoginResponse, RefreshTokensAuthRefreshPostData } from './client/types.gen';
// TODO: the refresh-token cookie should be httpOnly

let refreshPromise: Promise<LoginResponse> | null = null;

async function setCookie(
  name: string,
  value: string,
  exdays?: number | null,
  secure: boolean = true,
) {
  const d = new Date();
  if (!exdays) {
    exdays = import.meta.env.REFRESH_TOKEN_EXPIRE_DAYS
      ? parseInt(import.meta.env.REFRESH_TOKEN_EXPIRE_DAYS)
      : 7;
  }
  d.setTime(d.getTime() + exdays * 24 * 60 * 60 * 1000);
  const expires = `expires=${d.toUTCString()}`;
  const secureFlag = secure ? 'Secure; ' : '';
  const cookie = `${name}=${value}; ${expires}; ${secureFlag}SameSite=Strict; path=/`;
  document.cookie = cookie;
}

function getCookie(name: string) {
  const cname = `${name}=`;
  const decodedCookie = decodeURIComponent(document.cookie);
  const ca = decodedCookie.split(';');
  for (let i = 0; i < ca.length; i++) {
    let c = ca[i];
    while (c.charAt(0) == ' ') {
      c = c.substring(1);
    }
    if (c.indexOf(cname) == 0) {
      return c.substring(cname.length, c.length);
    }
  }
  return '';
}

async function refresh(
  body: RefreshTokensAuthRefreshPostData['body'],
): Promise<LoginResponse> {
  const response = await refreshTokensAuthRefreshPost({ body });
  if (!response.data) {
    throw new Error('Token refresh failed: No data returned');
  }
  return response.data;
}

export async function refreshInterceptor(response: Response, request: Request) {
  if (!response.ok) {
    if (response.status === 401 && request.headers.get('_retry') !== 'true') {
      if (!refreshPromise) {
        refreshPromise = refresh({ refresh_token: getCookie('refresh_token') });
      }

      if (refreshPromise) {
        await refreshPromise
          .then((data) => {
            localStorage.setItem('access_token', data.access_token);
            setCookie('refresh_token', data.refresh_token);
            request.headers.set('Authorization', `Bearer ${data.access_token}`);
            request.headers.set('_retry', 'true');
            return fetch(request);
          })
          .catch((e) => {
            // Refresh failed, log out
            console.error('refresh failed:', e);
            // localStorage.removeItem('access_token');
            // setCookie('refresh_token', '', -1, true);
            // window.location.href = '/login';
            // return null;
          })
          .finally(() => {
            refreshPromise = null;
          });
      }
    }
    // Throw any other errors
    throw response;
  }
  // response is fine, pass it through
  return response;
}

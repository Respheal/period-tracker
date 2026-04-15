// Hook to manage cookies (specifically the refresh_token cookie)
import { useState } from 'react';

type Options = {
  expiresInDays?: number;
  path?: string;
  secure?: boolean;
  httpOnly?: boolean;
};

export function useCookie(
  key: string,
): [string | undefined, (value: string, options?: Options) => void] {
  const [cookieValue, setCookieValue] = useState<string | undefined>(() => {
    const cookie = document.cookie.split('; ').find((row) => row.startsWith(`${key}=`));

    if (cookie) {
      return cookie.split('=')[1];
    }

    return undefined;
  });

  function setCookie(value: string, options?: Options) {
    const d = new Date();
    let exdays = options?.expiresInDays;
    if (!exdays) {
      exdays = import.meta.env.REFRESH_TOKEN_EXPIRE_DAYS
        ? parseInt(import.meta.env.REFRESH_TOKEN_EXPIRE_DAYS)
        : 7;
    }
    d.setTime(d.getTime() + exdays * 24 * 60 * 60 * 1000);
    const expires = `expires=${d.toUTCString()}`;
    const domain = import.meta.env.FRONTEND_DOMAIN || undefined;
    const secureFlag = options?.secure ? 'Secure; ' : '';
    // const httpOnlyFlag = options?.httpOnly ? 'HttpOnly; ' : '';
    // TODO: troubleshooting this
    const httpOnlyFlag = '';
    const domainFlag = domain ? `Domain=${domain}; ` : '';
    const cookie = `${key}=${value}; ${expires}; ${secureFlag}${httpOnlyFlag}${domainFlag}SameSite=Strict; path=/`;
    document.cookie = cookie;
    setCookieValue(value);
  }

  return [cookieValue, setCookie];
}

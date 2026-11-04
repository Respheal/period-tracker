import { ZxcvbnFactory, type ZxcvbnResult } from '@zxcvbn-ts/core';
import { matcherPwnedFactory } from '@zxcvbn-ts/matcher-pwned';
import { useEffect, useRef, useState } from 'react';

const DEBOUNCE_MS = 300;
const matcherPwned = matcherPwnedFactory(fetch);
const customMatcher = { pwned: matcherPwned };

export function usePasswordStrength(password: string) {
  const [result, setResult] = useState<ZxcvbnResult | null>(null);
  const [loading, setLoading] = useState(true);
  const zxcvbnInstanceRef = useRef<ZxcvbnFactory | null>(null);

  useEffect(() => {
    async function loadOptions() {
      const { dictionary: commonDict, adjacencyGraphs } =
        await import('@zxcvbn-ts/language-common');
      const { dictionary: enDict, translations } = await import('@zxcvbn-ts/language-en');
      return {
        dictionary: { ...commonDict, ...enDict },
        graphs: adjacencyGraphs,
        useLevenshteinDistance: true,
        translations: translations,
      };
    }
    loadOptions()
      .then((options) => {
        zxcvbnInstanceRef.current = new ZxcvbnFactory(options, customMatcher);
      })
      .catch((error) => {
        console.error('Failed to load password strength library:', error);
      })
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    let ignore = false;
    const timeout = setTimeout(() => {
      zxcvbnInstanceRef.current
        ?.checkAsync(password)
        .then((response) => {
          if (!ignore) setResult(response);
        })
        .catch((error) => console.error(error));
    }, DEBOUNCE_MS);
    return () => {
      ignore = true;
      clearTimeout(timeout);
    };
  }, [password]);

  return { result, loading };
}

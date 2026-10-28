import { useMutation, useQuery } from '@tanstack/react-query';
import { useNavigate, useRouter } from '@tanstack/react-router';

import {
  createUserUsersPostMutation,
  loginAuthPostMutation,
} from '@/client/@tanstack/react-query.gen';
import type { BodyLoginAuthPost, UserCreate } from '@/client/types.gen';
import { authQuery, clearSession, decodeJWT, setSession } from '@/utils/auth';

export function useTokenPayload() {
  return useQuery({
    ...authQuery,
    enabled: false, // don't refetch from here, only read from the cache
    select: (token) => decodeJWT(token.access_token),
  }).data;
}

export function useAuth() {
  const router = useRouter();
  const navigate = useNavigate();

  const CreateUserMutation = useMutation({
    ...createUserUsersPostMutation(),
  });

  async function createAccount(data: UserCreate) {
    if (CreateUserMutation.isPending) return;
    await CreateUserMutation.mutateAsync({ body: data }).catch((err) => {
      throw new Error(`Account creation failed: ${err}`);
    });
  }

  const LoginMutation = useMutation({
    ...loginAuthPostMutation(),
  });

  async function login(data: BodyLoginAuthPost) {
    if (LoginMutation.isPending) return;
    await LoginMutation.mutateAsync({ body: data })
      .catch((err) => {
        throw new Error(`Authentication failed: ${err}`);
      })
      .then(setSession);
  }

  function logout() {
    // invalidate the token on the backend first
    // insert function here
    clearSession();
    void router.invalidate();
    void navigate({
      to: '/login',
      search: { redirect: location.href },
    });
  }

  return {
    createAccount,
    login,
    logout,
  };
}

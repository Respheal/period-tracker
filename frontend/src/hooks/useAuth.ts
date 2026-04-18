import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate, useRouter } from '@tanstack/react-router';

import type { BodyLoginAuthPost, UserCreate } from '@/client/types.gen';
import {
  createUserUsersPostMutation,
  loginAuthPostMutation,
} from '@/client/@tanstack/react-query.gen';

export function useAuth() {
  const router = useRouter();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

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
      .then(() => {
        queryClient.setQueryData(['auth'], data);
        localStorage.setItem('isLoggedIn', true.toString());
      });
  }

  function logout() {
    localStorage.setItem('isLoggedIn', false.toString());
    queryClient.clear();
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

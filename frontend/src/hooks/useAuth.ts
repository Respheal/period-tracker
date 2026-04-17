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
    onError: (error: Error) => {
      throw new Error(`Account creation failed: ${error}`);
    },
  });

  async function createAccount(data: UserCreate) {
    if (CreateUserMutation.isPending) return;
    await CreateUserMutation.mutateAsync({ body: data });
  }

  const LoginMutation = useMutation({
    ...loginAuthPostMutation(),
    onError: (error: Error) => {
      throw new Error(`Authentication failed: ${error}`);
    },
    onSuccess: (data) => {
      queryClient.setQueryData(['auth'], data);
      localStorage.setItem('isLoggedIn', true.toString());
    },
  });

  async function login(data: BodyLoginAuthPost) {
    if (LoginMutation.isPending) return;
    await LoginMutation.mutateAsync({ body: data });
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

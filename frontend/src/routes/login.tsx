import { createFileRoute, useNavigate } from '@tanstack/react-router';
import useAuth from '@/hooks/useAuth';

import { LoginForm } from '@/components/LoginForm';
import type { BodyLoginAuthPost } from '@/client/types.gen';

export const Route = createFileRoute('/login')({
  component: RouteComponent,
});

function RouteComponent() {
  const navigate = useNavigate();
  const { login } = useAuth();

  return (
    <LoginForm navigateFn={navigate} loginFn={(data: BodyLoginAuthPost) => login(data)} />
  );
}

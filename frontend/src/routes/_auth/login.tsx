import { createFileRoute, useNavigate } from '@tanstack/react-router';

import { LoginForm } from '@/components/LoginForm';
import type { BodyLoginAuthPost } from '@/client/types.gen';

export const Route = createFileRoute('/_auth/login')({
  component: RouteComponent,
});

function RouteComponent() {
  const search: { redirect?: string } = Route.useSearch();
  const navigate = useNavigate();
  const { auth } = Route.useRouteContext();

  async function handleLogin(data: BodyLoginAuthPost) {
    await auth.login(data);
    navigate({ to: search.redirect || '/dashboard', search: {}, replace: true });
  }

  return <LoginForm navigateFn={navigate} loginFn={handleLogin} />;
}

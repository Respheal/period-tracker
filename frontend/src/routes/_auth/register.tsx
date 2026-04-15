import { createFileRoute, useNavigate } from '@tanstack/react-router';

import { RegistrationForm } from '@/components/RegistrationForm';

export const Route = createFileRoute('/_auth/register')({
  component: RouteComponent,
});

function RouteComponent() {
  const navigate = useNavigate();
  const { auth } = Route.useRouteContext();

  return <RegistrationForm navigateFn={navigate} registerFn={auth.createAccount} />;
}

import { createFileRoute, useNavigate } from '@tanstack/react-router';

import { RegistrationForm } from '@/components/RegistrationForm';
import { useAuth } from '@/hooks/useAuth';
import type { UserCreate } from '@/client/types.gen';

export const Route = createFileRoute('/_auth/register')({
  component: RouteComponent,
});

function RouteComponent() {
  const navigate = useNavigate();
  const { createAccount } = useAuth();

  async function handleRegister(data: UserCreate) {
    await createAccount(data);
    void navigate({ to: '/dashboard', search: {}, replace: true });
  }

  return <RegistrationForm navigateFn={navigate} registerFn={handleRegister} />;
}

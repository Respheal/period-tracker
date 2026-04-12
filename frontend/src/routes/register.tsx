import { createFileRoute, useNavigate } from '@tanstack/react-router';

import useAuth from '@/hooks/useAuth';

import { type UserCreate } from '@/client/types.gen';
import { RegistrationForm } from '@/components/RegistrationForm';

export const Route = createFileRoute('/register')({
  component: RouteComponent,
});

function RouteComponent() {
  const navigate = useNavigate();
  const { createAccount } = useAuth();

  return (
    <RegistrationForm
      navigateFn={navigate}
      registerFn={(data: UserCreate) =>
        createAccount(data.username, data.password, data.display_name)
      }
    />
  );
}

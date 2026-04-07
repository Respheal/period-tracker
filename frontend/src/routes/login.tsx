import { createFileRoute, useNavigate } from '@tanstack/react-router';
import useAuth from '@hooks/useAuth';

import Login from '@/stories/pages/Login/Login';

export const Route = createFileRoute('/login')({
  component: RouteComponent,
});

function RouteComponent() {
  const navigate = useNavigate();
  const { login } = useAuth();

  return <Login navigateFn={navigate} loginFn={(data) => login(data)} />;
}

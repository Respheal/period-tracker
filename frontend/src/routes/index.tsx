import { createFileRoute, redirect } from '@tanstack/react-router';

export const Route = createFileRoute('/')({
  beforeLoad: ({ context, location }) => {
    if (!context.auth.isAuthenticated) {
      redirect({
        throw: true,
        to: '/login',
        search: { redirect: location.href },
      });
    } else {
      redirect({
        throw: true,
        to: '/dashboard',
      });
    }
  },
});

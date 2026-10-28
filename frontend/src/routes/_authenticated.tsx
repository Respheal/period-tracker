import { createFileRoute, Outlet, redirect } from '@tanstack/react-router';

export const Route = createFileRoute('/_authenticated')({
  beforeLoad: async ({ context, location }) => {
    try {
      await context.auth.getSession();
    } catch {
      // Failed to get a valid session, redirect to login
      redirect({
        throw: true,
        to: '/login',
        search: { redirect: location.href },
      });
    }
  },
  component: () => <Outlet />,
});

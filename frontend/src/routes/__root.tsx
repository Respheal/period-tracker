import { healthCheckHealthGetOptions } from '@/client/@tanstack/react-query.gen';
import { useQuery, useQueryClient, type QueryClient } from '@tanstack/react-query';
import { createRootRouteWithContext, Link, Outlet } from '@tanstack/react-router';
import { TanStackRouterDevtools } from '@tanstack/react-router-devtools';

interface RouterContext {
  queryClient: QueryClient;
  auth: { isAuthenticated: boolean };
}

function RootLayout() {
  const queryClient = useQueryClient();
  // Auth status held in memory, not retained between page refreshes
  const isAuthenticated = !!queryClient.getQueryData(['auth']) || false;
  const { data, isLoading, error } = useQuery({ ...healthCheckHealthGetOptions() });

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (error instanceof Error) {
    return <div>Error: {error.message}</div>;
  }

  return (
    <>
      <div className='p-2 flex gap-2'>
        <Link to='/' className='[&.active]:font-bold'>
          Home
        </Link>
      </div>
      <div className='p-2 flex gap-2'>
        <h1>API Check</h1>
        <p>Authenticated: {isAuthenticated ? 'Authenticated' : 'Not Authenticated'}</p>
        <p>Status: {data?.status}</p>
        <p>Timestamp: {data?.timestamp?.toISOString()}</p>
      </div>
      <hr />
      <Outlet />
      <TanStackRouterDevtools />
    </>
  );
}

export const Route = createRootRouteWithContext<RouterContext>()({
  component: RootLayout,
});

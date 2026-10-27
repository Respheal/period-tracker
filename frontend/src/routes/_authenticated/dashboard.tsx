import {
  healthCheckHealthGetOptions,
  readMeUsersMeGetOptions,
} from '@/client/@tanstack/react-query.gen';
import { Link as ChakraLink } from '@chakra-ui/react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { createFileRoute, Link } from '@tanstack/react-router';

export const Route = createFileRoute('/_authenticated/dashboard')({
  component: RouteComponent,
});

function RouteComponent() {
  // API test
  const queryClient = useQueryClient();
  const healthcheck = useQuery({ ...healthCheckHealthGetOptions() });
  const user = useQuery({ ...readMeUsersMeGetOptions() });
  const isAuthenticated = !!queryClient.getQueryData(['auth']) || false;

  if (healthcheck.isLoading || user.isLoading) {
    return <div>Loading...</div>;
  }

  if (healthcheck.error instanceof Error) {
    return <div>Error: {healthcheck.error.message}</div>;
  }
  if (user.error instanceof Error) {
    return <div>Error: {user.error.message}</div>;
  }

  return (
    <div>
      <div className='p-2 flex gap-2'>
        <ChakraLink asChild key='home'>
          <Link to='/' activeProps={{ style: { fontWeight: 'bold' } }}>
            Home
          </Link>
        </ChakraLink>
      </div>
      <div className='p-2 flex gap-2'>
        <h1>API Check</h1>
        <p>Authenticated: {isAuthenticated ? 'Authenticated' : 'Not Authenticated'}</p>
        <p>Status: {healthcheck.data?.status}</p>
        <p>Timestamp: {healthcheck.data?.timestamp?.toISOString()}</p>
        <p>User: {user.data?.username}</p>
      </div>
      <hr />
    </div>
  );
}

import { Link as ChakraLink, Container } from '@chakra-ui/react';
import { useQuery, useQueryClient, type QueryClient } from '@tanstack/react-query';
import { createRootRouteWithContext, Link, Outlet } from '@tanstack/react-router';
import { TanStackRouterDevtools } from '@tanstack/react-router-devtools';
import { useState } from 'react';

import { healthCheckHealthGetOptions } from '@/client/@tanstack/react-query.gen';
import { Provider } from '@/components/chakra-ui/provider';
import { PalettePicker } from '@/components/PalettePicker/PalettePicker';

interface RouterContext {
  queryClient: QueryClient;
  auth: { isAuthenticated: boolean };
}

function getPallete() {
  const storedPalette = localStorage.getItem('user-palette');
  return storedPalette;
}

function RootLayout() {
  const [palette, setPalette] = useState(() => getPallete() || 'gray');

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
    <Provider palette={palette}>
      <Container
        fluid
        centerContent={true}
        maxWidth={{ base: '100dvw', md: '90dvw', lg: '3xl' }}>
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
          <p>Status: {data?.status}</p>
          <p>Timestamp: {data?.timestamp?.toISOString()}</p>
        </div>
        <hr />
        <PalettePicker setPalette={setPalette} />
        <Outlet />
      </Container>
      <TanStackRouterDevtools />
    </Provider>
  );
}

export const Route = createRootRouteWithContext<RouterContext>()({
  component: RootLayout,
});

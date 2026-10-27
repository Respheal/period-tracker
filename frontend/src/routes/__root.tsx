import { AbsoluteCenter, Link as ChakraLink, Container, Spinner } from '@chakra-ui/react';
import { useQueryClient, type QueryClient } from '@tanstack/react-query';
import { createRootRouteWithContext, Outlet } from '@tanstack/react-router';
import { TanStackRouterDevtools } from '@tanstack/react-router-devtools';
import { useState } from 'react';

import { ColorModeButton } from '@/components/chakra-ui/color-mode';
import { Provider } from '@/components/chakra-ui/provider';
import { PalettePicker } from '@/components/PalettePicker/PalettePicker';
import { useAuth } from '@/hooks/useAuth';

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
  // const [isLoading, setIsLoading] = useState(true);
  const isLoading = false;
  const queryClient = useQueryClient();
  // Auth status held in memory, not retained between page refreshes
  const isAuthenticated = !!queryClient.getQueryData(['auth']) || false;
  const { logout } = useAuth();

  if (isLoading) {
    return (
      <Provider>
        <AbsoluteCenter>
          <Spinner size='xl' />
        </AbsoluteCenter>
      </Provider>
    );
  }

  if (!isAuthenticated) {
    // Display the bare login/registration page
    return (
      <Provider>
        <AbsoluteCenter>
          <Container>
            <Outlet />
          </Container>
        </AbsoluteCenter>
        <TanStackRouterDevtools />
      </Provider>
    );
  } else {
    return (
      <Provider palette={palette}>
        <Container
          fluid
          centerContent={true}
          maxWidth={{ base: '100dvw', md: '90dvw', lg: '3xl' }}>
          stuff
          <ChakraLink onClick={logout}>Log Out</ChakraLink>
          <PalettePicker setPalette={setPalette} />
          <ColorModeButton />
          <Outlet />
        </Container>
        <TanStackRouterDevtools />
      </Provider>
    );
  }
}

export const Route = createRootRouteWithContext<RouterContext>()({
  component: RootLayout,
});

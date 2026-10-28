import { AbsoluteCenter, Link as ChakraLink, Container } from '@chakra-ui/react';
import { type QueryClient } from '@tanstack/react-query';
import {
  createRootRouteWithContext,
  Outlet,
  useRouterState,
} from '@tanstack/react-router';
import { TanStackRouterDevtools } from '@tanstack/react-router-devtools';
import { useState } from 'react';

import { ColorModeButton } from '@/components/chakra-ui/color-mode';
import { Provider } from '@/components/chakra-ui/provider';
import { PalettePicker } from '@/components/PalettePicker/PalettePicker';
import { useAuth } from '@/hooks/useAuth';

interface RouterContext {
  queryClient: QueryClient;
  auth: { isAuthenticated: boolean; getSession: () => Promise<string> };
}

function getPallete() {
  const storedPalette = localStorage.getItem('user-palette');
  return storedPalette;
}

function RootLayout() {
  const [palette, setPalette] = useState(() => getPallete() || 'gray');
  // _authenticated's beforeLoad guarantees a valid token for anything under it
  const isAuthenticated = useRouterState({
    select: (s) => s.matches.some((m) => m.routeId === '/_authenticated'),
  });
  const { logout } = useAuth(); //put wherever the navbar goes (or pass as a prop)

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

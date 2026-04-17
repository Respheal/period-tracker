import { useState } from 'react';
import { Outlet, createRootRouteWithContext } from '@tanstack/react-router';
import { TanStackRouterDevtools } from '@tanstack/react-router-devtools';
import type { QueryClient } from '@tanstack/react-query';

import { ChakraUIProvider } from '@/providers/ChakraUIProvider';
import { ColorModeButton } from '@/components/chakra-ui/color-mode';
import {
  AbsoluteCenter,
  Box,
  Container,
  Flex,
  SkipNavContent,
  SkipNavLink,
  Spacer,
} from '@chakra-ui/react';
import { MobileDrawer } from '@/components/Navigation/MobileDrawer';
import { MenuLinks } from '@/components/Navigation/MenuLinks';
import { PalettePicker } from '@/components/PalettePicker';
import { useAuth } from '@/hooks/useAuth';

interface RouterContext {
  queryClient: QueryClient;
  auth: { isAuthenticated: boolean };
}

export const Route = createRootRouteWithContext<RouterContext>()({
  component: RootComponent,
});

function getPallete() {
  const storedPalette = localStorage.getItem('user-palette');
  return storedPalette;
}

function RootComponent() {
  const [palette, setPalette] = useState(() => getPallete() || 'gray');
  const { auth } = Route.useRouteContext();
  const isAuthenticated = auth.isAuthenticated;
  const { logout } = useAuth();
  const nav_items = [
    ['/dashboard', 'Home'],
    ['/api', 'API Test'],
  ] as const;

  if (!isAuthenticated) {
    // Display the bare login/registration page
    return (
      <ChakraUIProvider>
        <AbsoluteCenter>
          <Container>
            <Outlet />
          </Container>
        </AbsoluteCenter>
        <TanStackRouterDevtools />
      </ChakraUIProvider>
    );
  } else {
    // Display the main dashboard with sidebar
    return (
      <ChakraUIProvider palette={palette}>
        <Container
          fluid
          centerContent={true}
          maxWidth={{ base: '100dvw', md: '90dvw', lg: '3xl' }}>
          <SkipNavLink id='main'>Skip to Content</SkipNavLink>
          <Flex direction='row' align='center' width='full' py={4}>
            <Box display={{ base: 'none', md: 'block' }}>
              <MenuLinks nav_items={nav_items} logoutFn={logout} />
            </Box>

            {/* Mobile Drawer */}
            <Box display={{ base: 'block', md: 'none' }}>
              <MobileDrawer nav_items={nav_items} logoutFn={logout} />
            </Box>

            <Spacer />
            <PalettePicker setPalette={setPalette} />
            <ColorModeButton />
          </Flex>
          <SkipNavContent id='main'>
            <Outlet />
          </SkipNavContent>
        </Container>
        <TanStackRouterDevtools />
      </ChakraUIProvider>
    );
  }
}

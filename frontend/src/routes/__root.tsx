import { useState } from 'react';
import { Outlet, createRootRouteWithContext } from '@tanstack/react-router';
import { QueryClient } from '@tanstack/react-query';

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
import type { AuthState } from '@/providers/AuthProvider';

interface MyRouterContext {
  auth: AuthState;
  queryClient: QueryClient;
}

export const Route = createRootRouteWithContext<MyRouterContext>()({
  component: RootComponent,
});

function RootComponent() {
  const { auth } = Route.useRouteContext();
  const [palette, setPalette] = useState(localStorage.getItem('user-palette') || 'gray');
  const nav_items = [
    ['/dashboard', 'Home'],
    ['/api', 'API Test'],
  ] as const;

  if (!auth.isAuthenticated) {
    // Display the bare login/registration page
    return (
      <ChakraUIProvider>
        <AbsoluteCenter>
          <Container>
            <Outlet />
          </Container>
        </AbsoluteCenter>
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
              <MenuLinks nav_items={nav_items} logoutFn={auth.logout} />
            </Box>

            {/* Mobile Drawer */}
            <Box display={{ base: 'block', md: 'none' }}>
              <MobileDrawer nav_items={nav_items} logoutFn={auth.logout} />
            </Box>

            <Spacer />
            <PalettePicker setPalette={setPalette} />
            <ColorModeButton />
          </Flex>
          <SkipNavContent id='main'>
            <Outlet />
          </SkipNavContent>
        </Container>
      </ChakraUIProvider>
    );
  }
}

import { useEffect, useState } from 'react';
import { Outlet, createRootRouteWithContext, useNavigate } from '@tanstack/react-router';
import { TanStackRouterDevtools } from '@tanstack/react-router-devtools';
import { useQueryClient, type QueryClient } from '@tanstack/react-query';

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
  Spinner,
} from '@chakra-ui/react';
import { MobileDrawer } from '@/components/Navigation/MobileDrawer';
import { MenuLinks } from '@/components/Navigation/MenuLinks';
import { PalettePicker } from '@/components/PalettePicker';
import { useAuth } from '@/hooks/useAuth';
import { refreshTokensAuthRefreshPost } from '@/client/sdk.gen';

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
  const [isLoading, setIsLoading] = useState(true);
  const queryClient = useQueryClient();
  // Auth status held in memory, not retained between page refreshes
  const isAuthenticated = !!queryClient.getQueryData(['auth']) || false;
  // to pass to the menu link
  const { logout } = useAuth();
  // for redirecting on a failed token refresh
  const navigate = useNavigate();
  const nav_items = [
    ['/dashboard', 'Home'],
    ['/api', 'API Test'],
  ] as const;

  // Check and reload auth state
  useEffect(() => {
    const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true';
    if (!isAuthenticated && isLoggedIn) {
      // The user logged in but the auth state is not in memory. Attempt a refresh.
      async function refreshAuthToken() {
        await refreshTokensAuthRefreshPost()
          .then((response) => {
            queryClient.setQueryData(['auth'], response.data);
            setIsLoading(false);
          })
          .catch(() => {
            localStorage.removeItem('isLoggedIn');
            queryClient.clear();
            navigate({ to: '/login', search: { redirect: location.href } });
          });
      }
      refreshAuthToken();
    } else {
      setIsLoading(false);
    }
  }, []);

  if (isLoading) {
    return (
      <ChakraUIProvider>
        <AbsoluteCenter>
          <Spinner size='xl' />
        </AbsoluteCenter>
      </ChakraUIProvider>
    );
  }

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

import { useState } from 'react';
import {
  createRootRoute,
  useRouterState,
  Outlet,
  useNavigate,
} from '@tanstack/react-router';
import { TanStackRouterDevtools } from '@tanstack/react-router-devtools';

import { Provider } from '@/components/ui/provider';
import { ColorModeButton } from '@/components/ui/color-mode';
import useAuth, { isLoggedIn } from '@/hooks/useAuth';
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

export const Route = createRootRoute({
  component: RootComponent,
});

function RootComponent() {
  const [palette, setPalette] = useState(localStorage.getItem('user-palette') || 'gray');
  const nav_items = [
    ['/dashboard', 'Home'],
    ['/api', 'API Test'],
  ] as const;
  const navigate = useNavigate();
  const router = useRouterState();
  const { logout } = useAuth();

  if (!isLoggedIn()) {
    // If the user is not logged in, redirect to the register page if
    // they are doing anything but visiting the register or login page
    if (
      router.location.pathname !== '/register' &&
      router.location.pathname !== '/login'
    ) {
      navigate({ to: '/register' });
    }
    // Display the register or login page
    return (
      <Provider>
        <AbsoluteCenter>
          <Container>
            <Outlet />
          </Container>
        </AbsoluteCenter>
      </Provider>
    );
  } else {
    // If a logged-in user tries to visit the register or login page,
    // redirect them to the dashboard
    if (
      router.location.pathname === '/' ||
      router.location.pathname === '/register' ||
      router.location.pathname === '/login'
    ) {
      navigate({ to: '/dashboard' });
    }
    // Display the main dashboard with sidebar
    return (
      <Provider palette={palette}>
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
      </Provider>
    );
  }
}

import { createRootRoute, Outlet } from '@tanstack/react-router';
import { TanStackRouterDevtools } from '@tanstack/react-router-devtools';
import { Provider } from '@/components/ui/provider';
import { ColorModeButton } from '@/components/ui/color-mode';

export const Route = createRootRoute({
  component: RootComponent,
});

function RootComponent() {
  return (
    <>
      <Provider>
        <ColorModeButton />
        <Outlet />
        <TanStackRouterDevtools />
      </Provider>
    </>
  );
}

import { forwardRef } from "react";
import {
  createRootRoute,
  useRouterState,
  Outlet,
  createLink,
  useNavigate,
} from "@tanstack/react-router";
import type { LinkComponent } from "@tanstack/react-router";
import { TanStackRouterDevtools } from "@tanstack/react-router-devtools";

import DashboardIcon from "@mui/icons-material/Dashboard";
import ListItemButton from "@mui/material/ListItemButton";
import type { ListItemProps } from "@mui/material";

import Sidebar from "../stories/organisms/Sidebar/Sidebar";
import { isLoggedIn } from "@/hooks/useAuth";

interface MUIButtonLinkProps extends ListItemProps<"a"> {
  onClick?: React.MouseEventHandler<HTMLAnchorElement>;
}

const MUIButtonLinkComponent = forwardRef<
  HTMLAnchorElement,
  MUIButtonLinkProps
>((props, ref) => <ListItemButton ref={ref} component="a" {...props} />);

const CreatedListItemLinkComponent = createLink(MUIButtonLinkComponent);

const ListItemLink: LinkComponent<typeof MUIButtonLinkComponent> = (props) => {
  return <CreatedListItemLinkComponent preload={"intent"} {...props} />;
};

export const Route = createRootRoute({
  component: RootComponent,
});

function RootComponent() {
  const nav_items = [
    ["/dashboard", "Home", <DashboardIcon />],
    ["/api", "API Test", <DashboardIcon />],
  ] as const;
  const navigate = useNavigate();
  const router = useRouterState();

  if (!isLoggedIn()) {
    if (
      router.location.pathname !== "/register" &&
      router.location.pathname !== "/login"
    ) {
      navigate({ to: "/register" });
    }
    // Display the register or login page
    return (
      <>
        <Outlet />
        <TanStackRouterDevtools />
      </>
    );
  } else {
    if (router.location.pathname === "/") {
      navigate({ to: "/dashboard" });
    }
    // Display the main dashboard with sidebar
    return (
      <Sidebar
        title="Period Tracker"
        nav_items={nav_items}
        active={router.location.pathname}
        NavItemComponent={ListItemLink}
      >
        <Outlet />
        <TanStackRouterDevtools />
      </Sidebar>
    );
  }
}

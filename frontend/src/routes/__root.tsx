import * as React from "react";
import { createRootRoute, useRouterState } from "@tanstack/react-router";
import { Sidebar } from "../components/Sidebar";
import DashboardIcon from "@mui/icons-material/Dashboard";

export const Route = createRootRoute({
  component: RootComponent,
});

function RootComponent() {
  const nav_items = [
    ["/", "Home", <DashboardIcon />],
    ["/login", "Login", <DashboardIcon />],
    ["/api", "API Test", <DashboardIcon />],
  ] as const;
  const router = useRouterState();
  return (
    <React.Fragment>
      <Sidebar
        title="My Sidebar"
        nav_items={nav_items}
        active={router.location.pathname}
      />
    </React.Fragment>
  );
}

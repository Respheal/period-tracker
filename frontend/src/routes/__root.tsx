import * as React from "react";
import { createRootRoute } from "@tanstack/react-router";
import { Sidebar } from "../components/Sidebar";
import DashboardIcon from "@mui/icons-material/Dashboard";

export const Route = createRootRoute({
  component: RootComponent,
});

function RootComponent() {
  const nav_items = [
    ["/", "Home", <DashboardIcon />, true],
    ["/login", "Login", <DashboardIcon />],
    ["/api", "API Test", <DashboardIcon />],
  ] as const;

  return (
    <React.Fragment>
      <Sidebar title="My Sidebar" nav_items={nav_items} />
    </React.Fragment>
  );
}

import * as React from "react";
import { Outlet, createLink } from "@tanstack/react-router";
import type { LinkComponent } from "@tanstack/react-router";
import ListItemButton from "@mui/material/ListItemButton";
import type { ListItemProps } from "@mui/material";
import SidebarLayout from "../stories/organisms/Sidebar/SidebarLayout";
import { TanStackRouterDevtools } from "@tanstack/react-router-devtools";

interface MUIButtonLinkProps extends ListItemProps<"a"> {
  onClick?: React.MouseEventHandler<HTMLAnchorElement>;
}

const MUIButtonLinkComponent = React.forwardRef<
  HTMLAnchorElement,
  MUIButtonLinkProps
>((props, ref) => <ListItemButton ref={ref} component="a" {...props} />);

const CreatedListItemLinkComponent = createLink(MUIButtonLinkComponent);

const ListItemLink: LinkComponent<typeof MUIButtonLinkComponent> = (props) => {
  return <CreatedListItemLinkComponent preload={"intent"} {...props} />;
};

export function Sidebar({
  title,
  nav_items,
  active,
}: {
  title: string;
  nav_items: readonly (readonly [string, string, React.ReactNode, boolean?])[];
  active: string;
}) {
  return (
    <SidebarLayout
      title={title}
      nav_items={nav_items}
      active={active}
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      NavItemComponent={ListItemLink as React.ComponentType<any>}
    >
      <Outlet />
      <TanStackRouterDevtools />
    </SidebarLayout>
  );
}

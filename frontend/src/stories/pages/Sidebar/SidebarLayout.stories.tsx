import type { Meta, StoryObj } from "@storybook/react-vite";
import DashboardIcon from "@mui/icons-material/Dashboard";
import SidebarLayout from "./SidebarLayout";

const meta = {
  title: "Organisms/SidebarLayout",
  component: SidebarLayout,
  tags: ["autodocs"],
  parameters: {
    layout: "fullscreen",
  },
} satisfies Meta<typeof SidebarLayout>;

export default meta;

type Story = StoryObj<typeof meta>;

const nav_items = [
  ["#", "Home", <DashboardIcon />],
  ["#login", "Login", <DashboardIcon />],
  ["#api", "API Test", <DashboardIcon />],
] as const;

export const WithDashboard: Story = {
  args: {
    title: "Period Tracker",
    nav_items: nav_items,
    active: "#",
    children: <div>Dashboard content here</div>,
  },
};

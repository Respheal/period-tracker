import type { Meta, StoryObj } from "@storybook/react-vite";
import DashboardIcon from "@mui/icons-material/Dashboard";
import Sidebar from "./Sidebar";

const meta = {
  title: "Organisms/Sidebar",
  component: Sidebar,
  tags: ["autodocs"],
  parameters: {
    layout: "fullscreen",
  },
} satisfies Meta<typeof Sidebar>;

export default meta;

type Story = StoryObj<typeof meta>;

const nav_items = [
  ["#", "Home", <DashboardIcon />],
  ["#login", "Login", <DashboardIcon />],
  ["#api", "API Test", <DashboardIcon />],
] as const;

export const Dashboard: Story = {
  args: {
    title: "Period Tracker",
    nav_items: nav_items,
    active: "#",
    children: <div style={{ height: "20vh" }}>Dashboard content here</div>,
  },
};

export const LongDashboard: Story = {
  args: {
    title: "Period Tracker",
    nav_items: nav_items,
    active: "#",
    children: <div style={{ height: "50vh" }}>Long scrollable content</div>,
  },
};

export const APIDashboard: Story = {
  args: {
    title: "Period Tracker",
    nav_items: nav_items,
    active: "#api",
    children: <div style={{ height: "20vh" }}>API Dashboard content here</div>,
  },
};

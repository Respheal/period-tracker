import type { Meta, StoryObj } from '@storybook/react-vite';
// import { expect } from "storybook/test";
import { fn } from 'storybook/test';
import DashboardIcon from '@mui/icons-material/Dashboard';

import Sidebar from './Sidebar';

const MockLogoutFn = fn(async () => {
  return new Promise((resolve) => setTimeout(resolve, 1000));
}).mockName('logoutFn');

const meta = {
  title: 'Organisms/Sidebar',
  component: Sidebar,
  tags: ['autodocs'],
  parameters: {
    layout: 'fullscreen',
  },
} satisfies Meta<typeof Sidebar>;

export default meta;

type Story = StoryObj<typeof meta>;

const nav_items = [['/', 'Home', <DashboardIcon />]] as const;

export const Dashboard: Story = {
  args: {
    title: 'Period Tracker',
    nav_items: nav_items,
    active: '/',
    children: <div style={{ height: '20vh' }}>Dashboard content here</div>,
    logoutFn: MockLogoutFn,
  },
  // play: async ({ page, canvas, userEvent }) => {
  //   const desktopSidebar = canvas.getByLabelText("desktop sidebar");
  //   await expect(desktopSidebar).toBeInTheDocument();
  //   // const submitButton = canvas.getByRole('button', { name: 'Plan event' });
  //   // await userEvent.click(submitButton);

  //   await page.setViewportSize({ width: 320, height: 568 });
  //   const mobileSidebar = canvas.getByLabelText("mobile sidebar");
  //   await expect(mobileSidebar).toBeInTheDocument();
  // },
};

export const LongDashboard: Story = {
  args: {
    title: 'Period Tracker',
    nav_items: nav_items,
    active: '/',
    children: <div style={{ height: '50vh' }}>Long scrollable content</div>,
    logoutFn: MockLogoutFn,
  },
};

import type { Meta, StoryObj } from "@storybook/react-vite";

import Dashboard from "./Dashboard";

const meta = {
  component: Dashboard,
  title: "Templates/Dashboard",
  tags: ["autodocs"],
  parameters: {
    layout: "centered",
  },
} satisfies Meta<typeof Dashboard>;
export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {};

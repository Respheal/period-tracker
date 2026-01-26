import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";

import Register from "./Register";

const MockRegistrationFn = fn(async () => {
  return new Promise((resolve) => setTimeout(resolve, 1000));
}).mockName("registerFn");

const MockNavigateFn = fn(() => {}).mockName("navigateFn");

const meta = {
  component: Register,
  title: "Pages/Register",
  tags: ["autodocs"],
  parameters: {
    layout: "fullscreen",
  },
  args: { registerFn: MockRegistrationFn, navigateFn: MockNavigateFn },
} satisfies Meta<typeof Register>;
export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    registerFn: MockRegistrationFn,
    navigateFn: MockNavigateFn,
  },
};

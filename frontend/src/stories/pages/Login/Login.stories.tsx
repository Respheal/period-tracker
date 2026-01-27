import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";

import Login from "./Login";

const MockLoginFn = fn(async () => {
  return new Promise((resolve) => setTimeout(resolve, 1000));
}).mockName("loginFn");

const MockNavigateFn = fn(() => {}).mockName("navigateFn");

const meta = {
  component: Login,
  title: "Pages/Login",
  tags: ["autodocs"],
  parameters: {
    layout: "fullscreen",
  },
  args: { loginFn: MockLoginFn, navigateFn: MockNavigateFn },
} satisfies Meta<typeof Login>;
export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    loginFn: MockLoginFn,
    navigateFn: MockNavigateFn,
  },
};

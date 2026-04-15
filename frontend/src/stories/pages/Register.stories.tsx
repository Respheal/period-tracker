import type { Meta, StoryObj } from '@storybook/react-vite';
import { type ToOptions } from '@tanstack/react-router';

import { RegistrationForm } from '@/components/RegistrationForm';

async function MockRegistrationFn() {
  console.log('Registering account...');
}

async function MockNavigateFn(opts: ToOptions) {
  console.log('Navigating to:', opts.to);
}

const meta = {
  component: RegistrationForm,
  title: 'Pages/Register',
  tags: ['autodocs'],
  parameters: { layout: 'fullscreen' },
  args: { registerFn: MockRegistrationFn, navigateFn: MockNavigateFn },
} satisfies Meta<typeof RegistrationForm>;
export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    registerFn: MockRegistrationFn,
    navigateFn: MockNavigateFn,
  },
};

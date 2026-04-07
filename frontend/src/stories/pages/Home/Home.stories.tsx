import type { Meta, StoryObj } from '@storybook/react-vite';

import Home from './Home';

const meta = {
  component: Home,
  title: 'Pages/Home',
  tags: ['autodocs'],
  parameters: {
    layout: 'fullscreen',
  },
} satisfies Meta<typeof Home>;
export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {};

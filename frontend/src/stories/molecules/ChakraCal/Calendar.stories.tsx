import type { Meta, StoryObj } from '@storybook/react-vite';

import ChakraCal from './Calendar';

const meta = {
  component: ChakraCal,
  title: 'Molecules/ChakraCal',
  tags: ['autodocs'],
  parameters: {
    layout: 'centered',
  },
} satisfies Meta<typeof ChakraCal>;
export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {};

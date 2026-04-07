import type { Meta, StoryObj } from '@storybook/react-vite';

import ReactCalendar from './Calendar';

const meta = {
  component: ReactCalendar,
  title: 'Molecules/ReactCalendar',
  tags: ['autodocs'],
  parameters: {
    layout: 'centered',
  },
} satisfies Meta<typeof ReactCalendar>;
export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {};

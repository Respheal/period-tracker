import type { Meta, StoryObj } from '@storybook/react-vite';

import PeriodLogger from './PeriodLogger';

const meta = {
  component: PeriodLogger,
  title: 'Organisms/PeriodLogger',
  tags: ['autodocs'],
  parameters: {
    layout: 'centered',
  },
} satisfies Meta<typeof PeriodLogger>;
export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {};

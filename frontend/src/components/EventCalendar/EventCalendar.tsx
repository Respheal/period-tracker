import { DatePicker } from '@chakra-ui/react';

import type { Response } from '@/client/types.gen';
import { DayTable } from './DayTable';

export function EventCalendar(props: { events: Response }) {
  const { events } = props;
  return (
    <DatePicker.Root readOnly inline fixedWeeks>
      <DatePicker.Content unstyled>
        <DatePicker.View view='day'>
          <DatePicker.Header />
          <DayTable events={events} />
        </DatePicker.View>
        <DatePicker.View view='month'>
          <DatePicker.Header />
          <DatePicker.MonthTable />
        </DatePicker.View>
        <DatePicker.View view='year'>
          <DatePicker.Header />
          <DatePicker.YearTable />
        </DatePicker.View>
      </DatePicker.Content>
    </DatePicker.Root>
  );
}

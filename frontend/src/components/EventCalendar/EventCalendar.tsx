import { useEffect, useState } from 'react';
import { DatePicker } from '@chakra-ui/react';
import { keepPreviousData, useQuery, useQueryClient } from '@tanstack/react-query';
import dayjs from 'dayjs';

import { DayTable } from './DayTable';
import { Toaster, toaster } from '@/components/chakra-ui/toaster';
import type { Response as EventResponse } from '@/client/types.gen';
import { getMyEventsUsersMeEventsGetOptions } from '@/client/@tanstack/react-query.gen';

function startDateBuffer(startDate: dayjs.Dayjs, buffer: number = 14) {
  return startDate.subtract(buffer, 'day').format('YYYY-MM-DD');
}

function endDateBuffer(endDate: dayjs.Dayjs, buffer: number = 14) {
  return endDate.add(buffer, 'day').format('YYYY-MM-DD');
}

export function EventCalendar() {
  const queryClient = useQueryClient();
  const initialRange: { start: dayjs.Dayjs; end: dayjs.Dayjs } = {
    start: dayjs().startOf('month'),
    end: dayjs().endOf('month'),
  };
  const [renderedRange, setRenderedRange] = useState(initialRange);
  const { data, isLoading, error } = useQuery({
    ...getMyEventsUsersMeEventsGetOptions({
      query: {
        start_date: startDateBuffer(renderedRange.start),
        end_date: endDateBuffer(renderedRange.end),
      },
    }),
    placeholderData: keepPreviousData,
  });

  useEffect(() => {
    if (isLoading) return;
    // Once the current month is loaded, prefetch the previous month
    async function prefetchPrevMonth() {
      const prevMonth = renderedRange.start.subtract(1, 'month');
      const prevMonthPromise = () =>
        queryClient.prefetchQuery({
          ...getMyEventsUsersMeEventsGetOptions({
            query: {
              start_date: startDateBuffer(prevMonth.startOf('month')),
              end_date: endDateBuffer(prevMonth.endOf('month')),
            },
          }),
        });
      await prevMonthPromise();
    }
    prefetchPrevMonth().catch((err) => console.error(err));
  }, [isLoading, renderedRange, queryClient]);

  function renderEvents(data: EventResponse | undefined) {
    if (data) {
      return <DayTable events={data} />;
    }
    // Render the default DayTable until we have events to display
    return <DatePicker.DayTable />;
  }

  if (error instanceof Error) {
    toaster.create({
      description: error.message,
      type: 'error',
    });
  }

  return (
    <>
      <DatePicker.Root
        fixedWeeks
        inline
        onVisibleRangeChange={(details) => {
          // string conversion required to parse the date correctly (to my frustration)
          const start = dayjs(details.visibleRange.start.toString());
          const end = dayjs(details.visibleRange.end.toString());
          setRenderedRange({ start, end });
        }}>
        <DatePicker.Content unstyled>
          <DatePicker.View view='day'>
            <DatePicker.Header />
            {renderEvents(data)}
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
      <Toaster />
    </>
  );
}

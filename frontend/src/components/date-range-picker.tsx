'use client';

import { Button, DatePicker, Portal, Stack, Heading } from '@chakra-ui/react';
import { LuCalendar } from 'react-icons/lu';

export const RangePicker = () => {
  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        const form = new FormData(e.currentTarget);
        alert(
          JSON.stringify({
            start_date: form.get('dateRangeStart'),
            end_date: form.get('dateRangeEnd'),
          }),
        );
      }}>
      <Stack gap='2' align='flex-start' maxW='sm'>
        <Heading>Log Period</Heading>
        <DatePicker.Root selectionMode='range' name='dateRange' maxWidth={72}>
          <DatePicker.Control>
            <DatePicker.Input index={0} name='dateRangeStart' required /> -
            <DatePicker.Input index={1} name='dateRangeEnd' />
            <DatePicker.IndicatorGroup>
              <DatePicker.Trigger>
                <LuCalendar />
              </DatePicker.Trigger>
            </DatePicker.IndicatorGroup>
          </DatePicker.Control>
          <Portal>
            <DatePicker.Positioner>
              <DatePicker.Content>
                <DatePicker.View view='day'>
                  <DatePicker.Header />
                  <DatePicker.DayTable />
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
            </DatePicker.Positioner>
          </Portal>
        </DatePicker.Root>
        <Button size='sm' type='submit'>
          Submit
        </Button>
      </Stack>
    </form>
  );
};

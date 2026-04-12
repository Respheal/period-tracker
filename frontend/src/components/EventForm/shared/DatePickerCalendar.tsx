import { DatePicker, Portal } from '@chakra-ui/react';

export function DatePickerCalendar() {
  return (
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
  );
}

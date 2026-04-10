'use client';

import {
  DatePickerTable,
  DatePickerTableBody,
  DatePickerTableCellTrigger,
  DatePickerTableHead,
  DatePickerTableHeader,
  DatePickerTableRow,
  DatePickerWeekNumberCell,
  DatePickerWeekNumberHeaderCell,
  useDatePickerContext,
  DatePickerWeekNumberCellText,
  DatePickerTableCell,
  Float,
  Badge,
  Circle,
  type DatePickerTableProps,
  Popover,
  For,
  Stack,
  type DateValue,
} from '@chakra-ui/react';
import dayjs from 'dayjs';
import LocalizedFormat from 'dayjs/plugin/localizedFormat';

export interface DatePickerDayTableProps extends DatePickerTableProps {
  offset?: number;
  weekNumberLabel?: string;
  events: Event[];
}

interface Event {
  startDate: dayjs.Dayjs;
  symptoms: string[];
}

function formatDate({ day }: { day: DateValue }) {
  dayjs.extend(LocalizedFormat);
  return dayjs(new Date(day.year, day.month - 1, day.day)).format('ll');
}

function TableCell({ day, events }: { day: DateValue; events?: Event[] }) {
  console.log(dayjs(new Date(day.year, day.month - 1, day.day)));
  const hasEvents =
    events?.some((obj) =>
      obj.startDate.isSame(dayjs(new Date(day.year, day.month - 1, day.day)), 'day'),
    ) || false;

  if (hasEvents) {
    console.log('aaaaa');
    return (
      <Popover.Root lazyMount unmountOnExit>
        <Popover.Trigger asChild>
          <DatePickerTableCellTrigger>
            <DayCell day={day.day} hasEvents={hasEvents} />
          </DatePickerTableCellTrigger>
        </Popover.Trigger>
        <Popover.Positioner>
          <Popover.Content>
            <Popover.Arrow />
            <Popover.Body>
              <Popover.Title fontWeight='bold'>{formatDate({ day })}</Popover.Title>
              <Stack direction='row'>
                <For each={['weh']}>
                  {(symptom) => (
                    <Badge size='md' variant='surface'>
                      {symptom}
                    </Badge>
                  )}
                </For>
              </Stack>
            </Popover.Body>
          </Popover.Content>
        </Popover.Positioner>
      </Popover.Root>
    );
  }
  return <DatePickerTableCellTrigger>{day.day}</DatePickerTableCellTrigger>;
}

function DayCell({ day, hasEvents }: { day: number; hasEvents: boolean }) {
  if (hasEvents) {
    return (
      <>
        {day}
        <Float placement='bottom-end' offsetX='1' offsetY='1'>
          <Circle bg='green.500' size='8px' outline='0.2em solid' outlineColor='bg' />
        </Float>
      </>
    );
  }
  return <>{day}</>;
}

export const DatePickerDayTable = (props: DatePickerDayTableProps) => {
  const { offset, weekNumberLabel = '#', events, ...rest } = props;

  const ctx = useDatePickerContext();

  const offsetDays = offset ? ctx.getOffset({ months: offset }) : undefined;
  const weeks = offsetDays ? offsetDays.weeks : ctx.weeks;

  return (
    <DatePickerTable {...rest}>
      <DatePickerTableHead>
        <DatePickerTableRow>
          {ctx.showWeekNumbers && (
            <DatePickerWeekNumberHeaderCell>
              {weekNumberLabel}
            </DatePickerWeekNumberHeaderCell>
          )}
          {ctx.weekDays.map((weekDay, id) => (
            <DatePickerTableHeader key={id}>{weekDay.narrow}</DatePickerTableHeader>
          ))}
        </DatePickerTableRow>
      </DatePickerTableHead>
      <DatePickerTableBody>
        {weeks.map((week, weekIndex) => (
          <DatePickerTableRow key={weekIndex}>
            {ctx.showWeekNumbers && (
              <DatePickerWeekNumberCell weekIndex={weekIndex} week={week}>
                <DatePickerWeekNumberCellText>
                  {ctx.getWeekNumber(week)}
                </DatePickerWeekNumberCellText>
              </DatePickerWeekNumberCell>
            )}
            {week.map((day, id) => (
              <DatePickerTableCell
                key={id}
                value={day}
                visibleRange={offsetDays?.visibleRange}>
                <TableCell day={day} events={events} />
              </DatePickerTableCell>
            ))}
          </DatePickerTableRow>
        ))}
      </DatePickerTableBody>
    </DatePickerTable>
  );
};

'use client';

import type { Period, Response, SymptomEvent, Temperature } from '@/client/types.gen';
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
  Heading,
  Stack,
  type DateValue,
} from '@chakra-ui/react';
import dayjs from 'dayjs';
import LocalizedFormat from 'dayjs/plugin/localizedFormat';

export interface DatePickerDayTableProps extends DatePickerTableProps {
  offset?: number;
  weekNumberLabel?: string;
  events?: Response;
}

function formatDate({ day }: { day: DateValue }): string {
  dayjs.extend(LocalizedFormat);
  return dayjs(new Date(day.year, day.month - 1, day.day)).format('ll');
}

/**
 * Determine if the calendar day matches a provided event's date
 */
function isSameDay(calDay: DateValue, eventDate: Date): boolean {
  return dayjs(eventDate).isSame(
    dayjs(new Date(calDay.year, calDay.month - 1, calDay.day)),
    'day',
  );
}

function formatSymptomEvent(event: SymptomEvent) {
  return (
    <Stack gap='2'>
      <Heading>Symptoms</Heading>
      {formatBadgeList(event.symptoms)}
      <Heading>Mood</Heading>
      {formatBadgeList(event.mood)}
    </Stack>
  );
}

function formatBadgeList(symptoms: string[] | null) {
  if (symptoms) {
    return (
      <Stack direction='row'>
        <For each={symptoms}>
          {(symptom) => (
            <Badge size='md' variant='surface'>
              {symptom}
            </Badge>
          )}
        </For>
      </Stack>
    );
  }
}

function formatTemperatures(temps: Temperature[]) {
  return (
    <Stack direction='row'>
      <For each={temps}>
        {(temp) => (
          <Badge size='md' variant='surface'>
            {temp.temperature}
          </Badge>
        )}
      </For>
    </Stack>
  );
}

function TableCell({ day, events }: { day: DateValue; events?: Response }) {
  const eventData = events?.data || { periods: [], symptoms: [], temperatures: [] };
  // Extract only events matching the calendar day in question
  const dayEvents = Object.fromEntries(
    Object.entries(eventData).map(([key, items]) => {
      const filteredItems = items.filter((item) => {
        switch (key) {
          case 'periods':
            return isSameDay(day, (item as Period).start_date);
          case 'temperatures':
            return isSameDay(day, (item as Temperature).timestamp);
          case 'symptoms':
            return isSameDay(day, (item as SymptomEvent).date);
          default:
            return false;
        }
      });
      return [key, filteredItems];
    }),
  ) as Response['data'];

  if (Object.values(dayEvents).some((arr) => arr.length > 0)) {
    return (
      <Popover.Root lazyMount unmountOnExit>
        <Popover.Trigger asChild>
          <DatePickerTableCellTrigger>
            {day.day}
            <Float placement='bottom-end' offsetX='1' offsetY='1'>
              <Circle bg='green.500' size='8px' outline='0.2em solid' outlineColor='bg' />
            </Float>
          </DatePickerTableCellTrigger>
        </Popover.Trigger>
        <Popover.Positioner>
          <Popover.Content>
            <Popover.Arrow />
            <Popover.Body>
              <Popover.Title fontWeight='bold'>{formatDate({ day })}</Popover.Title>
              <For each={dayEvents['symptoms']}>
                {(event) => formatSymptomEvent(event as SymptomEvent)}
              </For>
              {formatTemperatures(dayEvents['temperatures'] as Temperature[])}
            </Popover.Body>
          </Popover.Content>
        </Popover.Positioner>
      </Popover.Root>
    );
  }
  return <DatePickerTableCellTrigger>{day.day}</DatePickerTableCellTrigger>;
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

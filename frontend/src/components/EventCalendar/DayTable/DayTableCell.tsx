'use client';

import {
  type Period,
  type Response,
  type SymptomEvent,
  type Temperature,
} from '@/client/types.gen';
import {
  DatePickerTableCellTrigger,
  Float,
  ScrollArea,
  Badge,
  Circle,
  Button,
  FormatNumber,
  Flex,
  Popover,
  DataList,
  For,
  Stack,
  type DateValue,
} from '@chakra-ui/react';
import dayjs from 'dayjs';
import LocalizedFormat from 'dayjs/plugin/localizedFormat';
import { EventSummary } from './EventSummary';

/**
 * Returns the style props for a calendar day based on whether it is a period day
 */
function periodDayStyle(periodDay: boolean) {
  return {
    variant: 'surface',
    rounded: 'xl',
    bg: periodDay ? 'red.muted' : undefined,
    color: periodDay ? 'red.fg' : undefined,
    _hover: periodDay ? { bg: 'red.emphasized' } : undefined,
    _selected: periodDay
      ? { bg: 'red.fg', color: 'red.muted', _hover: { color: 'red.fg' } }
      : undefined,
  };
}

export function DayTableCell({ day, events }: { day: DateValue; events?: Response }) {
  const eventData = events?.data || { periods: [], symptoms: [], temperatures: [] };
  const periodDay = isPeriodDay(day, events?.data.periods as Period[]);
  // Extract only events matching the calendar day in question
  const dayEvents = Object.fromEntries(
    Object.entries(eventData).map(([key, items]) => {
      const filteredItems = items.filter((item) => {
        switch (key) {
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
      <Popover.Root lazyMount unmountOnExit size='xs'>
        <Popover.Trigger asChild>
          <DatePickerTableCellTrigger {...periodDayStyle(periodDay)}>
            {day.day}
            <Float placement='bottom-end' offsetX='1' offsetY='1'>
              <Circle
                bg='green.solid'
                size='{3}'
                outline='0.2em solid'
                outlineColor='bg'
              />
            </Float>
          </DatePickerTableCellTrigger>
        </Popover.Trigger>
        <Popover.Positioner>
          <Popover.Content>
            <Popover.Arrow />
            <Popover.Header>
              <Popover.Title fontSize='lg' fontWeight='bold'>
                <Flex justify='space-between'>
                  {formatDate({ day })}
                  <Button size='xs' asChild>
                    <a href='#'>Edit</a>
                  </Button>
                </Flex>
              </Popover.Title>
            </Popover.Header>
            <Popover.Body pt={2}>
              <ScrollArea.Root maxHeight='12rem'>
                <ScrollArea.Viewport>
                  <ScrollArea.Content>
                    <DataList.Root orientation='horizontal' variant={'bold'}>
                      {EventSummary(dayEvents['symptoms'] as SymptomEvent[])}
                      {formatTemperatures(dayEvents['temperatures'] as Temperature[])}
                    </DataList.Root>
                  </ScrollArea.Content>
                </ScrollArea.Viewport>
                <ScrollArea.Scrollbar>
                  <ScrollArea.Thumb />
                </ScrollArea.Scrollbar>
                <ScrollArea.Corner />
              </ScrollArea.Root>
            </Popover.Body>
          </Popover.Content>
        </Popover.Positioner>
      </Popover.Root>
    );
  }
  return (
    <DatePickerTableCellTrigger {...periodDayStyle(periodDay)}>
      {day.day}
    </DatePickerTableCellTrigger>
  );
}

function dateValueToDate(date: DateValue): Date {
  return new Date(date.year, date.month - 1, date.day);
}

function formatDate({ day }: { day: DateValue }): string {
  dayjs.extend(LocalizedFormat);
  return dayjs(dateValueToDate(day)).format('ll');
}

/**
 * Determine if the calendar day matches a provided event's date
 */
function isSameDay(calDay: DateValue, eventDate: Date): boolean {
  return dayjs(eventDate).isSame(dayjs(dateValueToDate(calDay)), 'day');
}

function formatTemperatures(temps: Temperature[]) {
  if (temps.length > 0) {
    return (
      <DataList.Item key='temperatures'>
        <DataList.ItemLabel>Temperatures</DataList.ItemLabel>
        <DataList.ItemValue>
          <Stack direction={'row'}>
            <For each={temps}>
              {(temp, index) => (
                <Badge key={index} size='md' variant='surface'>
                  <FormatNumber
                    style='unit'
                    unit='celsius'
                    maximumFractionDigits={1}
                    value={temp.temperature}
                  />
                </Badge>
              )}
            </For>
          </Stack>
        </DataList.ItemValue>
      </DataList.Item>
    );
  }
}

function isPeriodDay(day: DateValue, periods: Period[]): boolean {
  return periods.some(
    (period) =>
      isSameDay(day, period.start_date) ||
      (dateValueToDate(day) > period.start_date &&
        period.end_date &&
        dateValueToDate(day) <= period.end_date),
  );
}

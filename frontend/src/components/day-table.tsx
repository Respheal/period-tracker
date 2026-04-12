'use client';

import {
  type Period,
  type Response,
  type SymptomEvent,
  type Temperature,
} from '@/client/types.gen';
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
  ScrollArea,
  Text,
  Badge,
  Circle,
  Wrap,
  Button,
  FormatNumber,
  Flex,
  Popover,
  For,
  Stack,
  type DatePickerTableProps,
  type DateValue,
} from '@chakra-ui/react';
import dayjs from 'dayjs';
import LocalizedFormat from 'dayjs/plugin/localizedFormat';
import type { JSX } from 'react';

export interface DatePickerDayTableProps extends DatePickerTableProps {
  offset?: number;
  weekNumberLabel?: string;
  events?: Response;
}

const summaryHeaderStyle = { textStyle: 'md', fontWeight: 'bold' };
const periodDayStyle = (periodDay: boolean) => {
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
};

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

function dateValueToDate(date: DateValue): Date {
  return new Date(date.year, date.month - 1, date.day);
}

interface EventSummary {
  symptoms: string[];
  mood: string[];
  flowIntensity: number;
  ovulationTest: boolean;
  discharge: string[];
  sex: string[];
}

/**
 * Map all events into simplified and combined lists
 * @param events An array of SymptomEvent objects to be formatted
 * @returns An EventSummary object summarizing the provided events
 */
function summarizeSymptomEvents(events: SymptomEvent[]): EventSummary {
  const symptoms = [...new Set(events.flatMap((obj) => obj.symptoms || []))];
  const mood = [...new Set(events.flatMap((obj) => obj.mood || []))];
  const flowIntensity = Math.max(
    ...events.map((event) => parseInt(event.flow_intensity || '0')),
  );
  const ovulationTest = events.some(
    (event) => event.ovulation_test && event.ovulation_test === true,
  );
  const discharge = [...new Set(events.flatMap((obj) => obj.discharge || []))];
  const sex = [...new Set(events.flatMap((obj) => obj.sex || []))];
  return { symptoms, mood, flowIntensity, ovulationTest, discharge, sex };
}

function EventSummaryPopover(events: SymptomEvent[]): (JSX.Element | undefined)[] {
  const summary = summarizeSymptomEvents(events);
  let symptomNode: JSX.Element | undefined = undefined;
  let moodNode: JSX.Element | undefined = undefined;
  let flowIntensityNode: JSX.Element | undefined = undefined;
  let ovulationTestNode: JSX.Element | undefined = undefined;
  let dischargeNode: JSX.Element | undefined = undefined;
  let sexNode: JSX.Element | undefined = undefined;

  if (summary.symptoms.length > 0) {
    symptomNode = (
      <Stack direction='row' align='top'>
        <Text css={summaryHeaderStyle}>Symptoms</Text>
        {formatBadgeList(summary.symptoms)}
      </Stack>
    );
  }
  if (summary.mood.length > 0) {
    moodNode = (
      <Stack direction='row' align='top'>
        <Text css={summaryHeaderStyle}>Mood</Text>
        {formatBadgeList(summary.mood)}
      </Stack>
    );
  }
  if (summary.flowIntensity > 0) {
    const icons = Array.from({ length: summary.flowIntensity }, (_, i) => (
      <Circle key={i} bg='red' size={3} />
    ));
    flowIntensityNode = (
      <Stack direction='row' align='center'>
        <Text css={summaryHeaderStyle}>Flow Intensity</Text>
        {icons}
      </Stack>
    );
  }
  if (typeof summary.ovulationTest !== 'undefined') {
    ovulationTestNode = (
      <Stack direction='row' align='top'>
        <Text css={summaryHeaderStyle}>Ovulation Test</Text>
        <Badge colorPalette={summary.ovulationTest ? 'green' : 'gray'}>
          {summary.ovulationTest ? 'Positive' : 'Negative'}
        </Badge>
      </Stack>
    );
  }
  if (summary.discharge.length > 0) {
    dischargeNode = (
      <Stack direction='row' align='top'>
        <Text css={summaryHeaderStyle}>Discharge</Text>
        {formatBadgeList(summary.discharge)}
      </Stack>
    );
  }
  if (summary.sex.length > 0) {
    sexNode = (
      <Stack direction='row' align='top'>
        <Text css={summaryHeaderStyle}>Sex</Text>
        {formatBadgeList(summary.sex)}
      </Stack>
    );
  }
  return [
    symptomNode,
    moodNode,
    flowIntensityNode,
    ovulationTestNode,
    dischargeNode,
    sexNode,
  ];
}

function formatBadgeList(items: string[]) {
  return (
    <Wrap align='top'>
      <For each={items}>
        {(item) => (
          <Badge size='md' variant='surface'>
            {item}
          </Badge>
        )}
      </For>
    </Wrap>
  );
}

function formatTemperatures(temps: Temperature[]) {
  return (
    <Stack direction='row'>
      <Text css={summaryHeaderStyle}>Temperatures</Text>
      <For each={temps}>
        {(temp) => (
          <Badge size='md' variant='surface'>
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
  );
}

function TableCell({ day, events }: { day: DateValue; events?: Response }) {
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
                    <Stack direction='column'>
                      {EventSummaryPopover(dayEvents['symptoms'] as SymptomEvent[])}
                      {formatTemperatures(dayEvents['temperatures'] as Temperature[])}
                    </Stack>
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

function isPeriodDay(day: DateValue, periods: Period[]): boolean {
  return periods.some(
    (period) =>
      isSameDay(day, period.start_date) ||
      (dateValueToDate(day) > period.start_date &&
        period.end_date &&
        dateValueToDate(day) <= period.end_date),
  );
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
                visibleRange={offsetDays?.visibleRange}
                textAlign='center'>
                <TableCell day={day} events={events} />
              </DatePickerTableCell>
            ))}
          </DatePickerTableRow>
        ))}
      </DatePickerTableBody>
    </DatePickerTable>
  );
};

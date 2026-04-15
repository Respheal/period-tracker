'use client';

import {
  DatePickerTable,
  DatePickerTableBody,
  DatePickerTableHead,
  DatePickerTableHeader,
  DatePickerTableRow,
  DatePickerWeekNumberCell,
  DatePickerWeekNumberHeaderCell,
  useDatePickerContext,
  DatePickerWeekNumberCellText,
  DatePickerTableCell,
  type DatePickerDayTableProps,
} from '@chakra-ui/react';

import { type Response } from '@/client/types.gen';
import { DayTableCell } from './DayTableCell';

interface EventCalendarDayTableProps extends DatePickerDayTableProps {
  events?: Response;
}

export function DayTable(props: EventCalendarDayTableProps) {
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
                <DayTableCell day={day} events={events} />
              </DatePickerTableCell>
            ))}
          </DatePickerTableRow>
        ))}
      </DatePickerTableBody>
    </DatePickerTable>
  );
}

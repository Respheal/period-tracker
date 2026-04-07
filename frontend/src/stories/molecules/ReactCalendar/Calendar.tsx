import dayjs from 'dayjs';
import { useState } from 'react';
import Calendar from 'react-calendar';
import 'react-calendar/dist/Calendar.css';

type ValuePiece = Date | null;

type Value = ValuePiece | [ValuePiece, ValuePiece];

type Range = { startDate: string | null; endDate?: string | null | undefined };

export default function ReactCalendar() {
  const [range, onChange] = useState<Range>({ startDate: null, endDate: null });

  function toDayString(e: Date): string {
    const formatted = dayjs(e).format('YYYY-MM-DD');
    return formatted;
  }

  function setRange(e: Value): Range {
    if (Array.isArray(e)) {
      return {
        ...range,
        startDate: e[0] ? toDayString(e[0]) : null,
        endDate: e[1] ? toDayString(e[1]) : null,
      };
    }
    return { startDate: e ? toDayString(e) : null };
  }

  return (
    <>
      <Calendar
        selectRange={true}
        allowPartialRange={true}
        onChange={(e: Value) => onChange(setRange(e))}
        value={[range.startDate, range.endDate ? range.endDate : null]}
      />
      <input
        type='date'
        id='start'
        name='end'
        value={range.startDate ? range.startDate : undefined}
        onChange={(e) => onChange({ ...range, startDate: e.target.value })}
      />
      <input
        type='date'
        id='end'
        name='end'
        value={range.endDate ? range.endDate : undefined}
        onChange={(e) => onChange({ ...range, endDate: e.target.value })}
      />
    </>
  );
}

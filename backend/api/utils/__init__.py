from datetime import UTC, datetime, time

from fastapi import HTTPException, status


def convert_dates_to_range(
    start_date: str | None, end_date: str | None
) -> tuple[datetime | None, datetime | None]:
    start_datetime = None
    end_datetime = None
    try:
        if start_date:
            min_date = datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=UTC)
            start_datetime = datetime.combine(min_date, time.min)
        if end_date:
            max_date = datetime.strptime(end_date, "%Y-%m-%d").replace(tzinfo=UTC)
            end_datetime = datetime.combine(max_date, time.max)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD.",
        )
    return start_datetime, end_datetime

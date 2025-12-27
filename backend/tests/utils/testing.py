from datetime import UTC, datetime, timedelta

from api.db import models
from api.utils import convert_dates_to_range, stats

user = models.User(
    user_id="test-user-id",
    is_disabled=False,
    is_admin=False,
    username="testuser",
    display_name="Test User",
    hashed_password="hashedpassword",
    temp_state=None,
    cycle_state=None,
)
periods: list[models.Period] = []
period_dates = [
    (["2025-05-01", "2025-05-04", None]),
    (["2025-06-01", None]),
    (["2025-08-01", "2025-08-04", 14]),
    (["2025-09-01", "2025-09-05", 14]),
    (["2025-10-01", "2025-10-05", 14]),
    (["2025-11-01", "2025-11-04", None]),
    (["2025-12-01", "2025-12-03", None]),
]
for start_str, end_str, length in period_dates:
    start_date, end_date = convert_dates_to_range(start_str, end_str)
    period = models.Period(
        user_id=user.user_id,
        start_date=start_date,
        end_date=end_date,
        duration=(end_date - start_date).days if end_date else None,
        luteal_length=length,
    )
    periods.append(period)

readings: list[models.Temperature] = []
temps = [
    36.5,
    36.6,
    36.7,
    36.8,
    36.9,
    37.0,
    36.8,
    36.7,
    36.6,
    36.5,
    36.5,
    36.6,
    36.7,
    36.8,
    36.9,
    37.0,
    36.8,
    36.7,
    36.6,
    36.5,
    38.0,
    38.1,
    38.2,
    38.3,
    38.4,
    38.5,
    38.3,
    38.2,
    38.1,
    38.0,
]
start_date = datetime(2025, 4, 25, tzinfo=UTC)
for i, temp in enumerate(temps):
    timestamp = start_date - timedelta(days=len(temps) - i - 1)
    reading = models.Temperature(
        user_id=user.user_id,
        temperature=temp,
        timestamp=timestamp,
    )
    readings.append(reading)

df = stats.temperatures_to_frame(readings)
smoothed = stats.compute_smoothed_temperature(df)
baseline_series = stats.compute_baseline(df)
baseline_value = baseline_series.iloc[-1]

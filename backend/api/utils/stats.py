from datetime import UTC, date, datetime, timedelta
from typing import Sequence

import pandas as pd

from api.db import models
from api.utils.dependencies import get_settings

settings = get_settings()


###
# Temperature
###
def temperatures_to_frame(
    temps: Sequence[models.Temperature], index: bool = True
) -> pd.DataFrame:
    """Convert Temperatures to a time-indexed DataFrame."""
    df = pd.DataFrame(
        [
            {"timestamp": pd.to_datetime(t.timestamp), "temperature": t.temperature}
            for t in temps
        ]
    )
    if df.empty:
        return df
    df = df.sort_values("timestamp").set_index("timestamp").resample("D").mean()
    if not index:
        df = df.reset_index()
    return df


def compute_smoothed_temperature(df: pd.DataFrame) -> pd.Series:
    return df["temperature"].ewm(span=settings.SMOOTHING_SPAN_DAYS, adjust=False).mean()


def compute_baseline(df: pd.DataFrame) -> pd.Series:
    return df["temperature"].ewm(span=settings.BASELINE_SPAN_DAYS, adjust=False).mean()


def has_long_gap(df: pd.DataFrame) -> bool:
    if len(df) < 2:
        return False
    gaps = df.dropna().index.to_series().diff().dt.days  # type: ignore
    return bool(gaps.max() is not None and gaps.max() > settings.MAX_MISSING_DAYS)


def detect_elevated_phase(smoothed: pd.Series, baseline: float) -> bool:
    """
    Detects a sustained relative rise above baseline.
    """
    if len(smoothed) < settings.ELEVATION_DAYS_REQUIRED:
        return False
    delta = smoothed - baseline
    threshold = max(settings.ELEVATION_MIN_DELTA, delta.std() or 0)
    recent = delta.tail(settings.ELEVATION_DAYS_REQUIRED)
    return bool((recent > threshold).all())


def evaluate_temperature_state(
    temperatures: Sequence[models.Temperature],
    previous_state: models.TemperatureState | None = None,
) -> models.TemperatureState:
    """
    Given all known temperatures for a user and their previous TemperatureState,
    return an updated TemperatureState.
    """
    df = temperatures_to_frame(temperatures)

    # Initialize state if missing
    state = previous_state or models.TemperatureState(phase=models.TempPhase.LEARNING)
    state.last_evaluated = datetime.now(UTC)

    if df.empty:
        state.phase = models.TempPhase.LEARNING
        return state

    # Guardrail: long gaps break interpretation
    if has_long_gap(df):
        state.phase = models.TempPhase.UNKNOWN
        return state

    smoothed = compute_smoothed_temperature(df)

    # Establish baseline only after enough data
    if len(smoothed) < settings.MIN_POINTS_FOR_BASELINE:
        state.phase = models.TempPhase.LEARNING
        return state

    baseline_series = compute_baseline(df)
    baseline_value = baseline_series.iloc[-1]

    state.baseline = baseline_value

    if detect_elevated_phase(smoothed, baseline_value):
        state.phase = models.TempPhase.ELEVATED
    else:
        state.phase = models.TempPhase.LOW

    return state


###
# Period
###
def periods_to_frame(periods: Sequence[models.Period]) -> pd.DataFrame:
    """Convert Periods to a DataFrame."""
    df = pd.DataFrame(
        [
            {"start": p.start_date, "end": p.end_date, "luteal_length": p.luteal_length}
            for p in periods
        ]
    )
    if df.empty:
        return df
    return df.sort_values("start")


def compute_cycle_lengths(df: pd.DataFrame) -> pd.Series:
    return pd.to_datetime(df["start"]).diff().dt.days


def compute_period_lengths(df: pd.DataFrame) -> pd.Series:
    return (pd.to_datetime(df["end"]) - pd.to_datetime(df["start"])).dt.days


def classify_cycle_lengths(cycle_lengths: pd.Series) -> pd.Series:
    """
    Generate a Series of booleans indicating whether each cycle length is valid.
    This will be used to filter out outliers when computing averages.
    """
    # Immediately filter out cycles with biologically implausible lengths.
    # These are likely missing data or input errors.
    valid = cycle_lengths.between(
        settings.MIN_PLAUSIBLE_CYCLE, settings.MAX_PLAUSIBLE_CYCLE, inclusive="both"
    )
    # Grab the most recent cycles to check for cycles that are longer than expected
    # based on the user's actual entered data to filter out outliers.
    # Outliers may be caused by stress, illness, or other factors and should not be
    # used to compute the typical cycle length for a user.
    recent = cycle_lengths.dropna().tail(settings.CYCLE_EWM_SPAN)
    if len(recent) >= 3:
        mean = recent.mean()
        max_allowed = mean * settings.LONG_GAP_MULTIPLIER
        # Mark cycles that are implausibly long for anyone and also longer than expected
        # for this specific user as invalid. Everything else is valid.
        # Because cycles are stored regardless of current validity, the system may later
        # reclassify longer-than-usual cycles as valid if the trend continues.
        valid &= cycle_lengths <= max_allowed
    return valid


def compute_cycle_average(cycle_lengths: pd.Series, valid_mask: pd.Series) -> int | None:
    """
    With the mask generated from classify_cycle_lengths,
    compute the EWM average of valid cycle lengths in days.
    """
    usable = cycle_lengths[valid_mask].dropna()
    if len(usable) < 1:
        return None
    avg_cycle: int | None = (
        usable.ewm(span=settings.CYCLE_EWM_SPAN, adjust=False)
        .mean()
        .iloc[-1]
        .round()
        .astype(int)
    )
    return avg_cycle


def compute_period_average(period_lengths: pd.Series) -> int | None:
    """
    Compute the EWM average of period lengths in days.
    Periods with no end dates are ignored as data entry errors.
    """
    usable = period_lengths.dropna()
    if len(usable) < 1:
        return None
    avg_period: int | None = (
        usable.ewm(span=settings.CYCLE_EWM_SPAN, adjust=False)
        .mean()
        .iloc[-1]
        .round()
        .astype(int)
    )
    return avg_period


def evaluate_cycle_state(
    periods: Sequence[models.Period],
    previous_state: models.Cycle | None = None,
) -> models.Cycle:
    df = periods_to_frame(periods)
    cycle_data = previous_state or models.Cycle(state=models.CycleState.LEARNING)
    cycle_data.last_evaluated = datetime.now(UTC)

    if df.empty or len(df) <= settings.MIN_CYCLES_FOR_STABLE:
        cycle_data.state = models.CycleState.LEARNING
        return cycle_data

    cycle_lengths = compute_cycle_lengths(df)
    valid_mask = classify_cycle_lengths(cycle_lengths)
    avg_cycle = compute_cycle_average(cycle_lengths, valid_mask)

    period_lengths = compute_period_lengths(df)
    avg_period = compute_period_average(period_lengths)

    cycle_data.avg_cycle_length = int(avg_cycle) if avg_cycle is not None else None
    cycle_data.avg_period_length = int(avg_period) if avg_period is not None else None

    if avg_cycle is None:  # pragma: no cover
        # We likely already hit this case above, but just in case
        cycle_data.state = models.CycleState.LEARNING
    elif (
        valid_mask.tail(settings.MIN_CYCLES_FOR_STABLE).sum()
        >= settings.MIN_CYCLES_FOR_STABLE
    ):
        cycle_data.state = models.CycleState.STABLE
    else:
        cycle_data.state = models.CycleState.UNSTABLE

    return cycle_data


def detect_elevated_phase_start(
    temperatures: Sequence[models.Temperature],
    period: models.Period,
) -> date | None:
    """
    Returns the first day of an elevated phase preceding the given period,
    or None if not found.
    """
    df = temperatures_to_frame(temperatures, index=False)
    if df.empty:
        return None
    # Get the subset of data before the period, within the lookback window
    window_start = period.start_date - timedelta(days=settings.MAX_LOOKBACK_DAYS)
    subset = df[
        (df["timestamp"] < period.start_date) & (df["timestamp"] >= window_start)
    ].copy()
    if subset.empty:  # pragma: no cover
        return None

    # With the computed temperature baseline, find the first day of a sustained
    # elevation above the baseline within the subset.
    baseline_series = compute_baseline(df)
    subset["baseline"] = baseline_series.loc[subset.index]
    subset["is_elevated"] = (
        subset["temperature"] >= subset["baseline"] + settings.ELEVATION_MIN_DELTA
    )

    # Find consecutive elevated runs
    consecutive = 0
    for _, row in subset.iterrows():
        if row["is_elevated"]:
            consecutive += 1
            if consecutive == settings.ELEVATION_DAYS_REQUIRED:
                # First day of the elevated run
                first_day: date = (
                    row["timestamp"]
                    - timedelta(days=settings.ELEVATION_DAYS_REQUIRED - 1)
                ).date()
                return first_day
        else:
            consecutive = 0
    return None


def compute_luteal_length(elevated_phase_start: date, period_start: datetime) -> int:
    luteal_start = elevated_phase_start - timedelta(days=1)
    return (period_start.date() - luteal_start).days


def is_valid_luteal_length(length: int) -> bool:
    return settings.MIN_LUTEAL_DAYS <= length <= settings.MAX_LUTEAL_DAYS


def compute_average_luteal_length(df: pd.DataFrame) -> int | None:
    """
    Returns EWM-smoothed average luteal length, or None if insufficient data.
    """
    if (
        "luteal_length" not in df.columns
        or len(df) < 2
        or df["luteal_length"].isna().all()
    ):
        return None
    return int(df["luteal_length"].ewm(span=3).mean().iloc[-1].round())


def predict_next_period(
    cycle_state: models.Cycle, periods: Sequence[models.Period]
) -> models.PredictedPeriod | None:
    # If we have the temperature data, use that and the historical luteal length to
    # predict the next period start date. If not, fall back to cycle averages.
    df = periods_to_frame(periods)
    last_period: datetime | None = df["start"].iloc[-1].date() if not df.empty else None
    if not last_period:
        return None
    if cycle_state.state == models.CycleState.UNSTABLE:
        # Don't make an attempt if the state is unstable
        return None
    # Check if we can get an average luteal length from provided data
    avg_luteal = compute_average_luteal_length(df)
    if avg_luteal and cycle_state.avg_cycle_length:
        expected_start = last_period + timedelta(
            days=cycle_state.avg_cycle_length - avg_luteal
        )
        confidence = 0.8  # High confidence with luteal-based prediction
    elif cycle_state.avg_cycle_length:
        # Fallback to cycle-based prediction
        expected_start = last_period + timedelta(days=round(cycle_state.avg_cycle_length))
        confidence = 0.5  # Lower confidence without luteal data
    else:
        # Fallback to a statistically average cycle length
        expected_start = last_period + timedelta(days=28)
        confidence = 0.2  # Low confidence with generic average
    expected_end = expected_start + timedelta(days=cycle_state.avg_period_length or 0)

    return models.PredictedPeriod(
        start_date=expected_start, end_date=expected_end, confidence=confidence
    )


def combine_events(
    periods: Sequence[models.Period],
    temperatures: Sequence[models.Temperature],
    symptoms: Sequence[models.SymptomEvent],
) -> pd.DataFrame:  # pragma: no cover
    """Combine period, temperature, and symptom events into a single DataFrame."""
    # Get periods and reformat to fit logically with the rest of the data
    period_df = periods_to_frame(periods)
    period_df["period_start"] = period_df["start"]
    period_df = period_df.rename(columns={"start": "date", "end": "period_end"})
    period_df["period_end"] = period_df["period_end"].dt.date
    period_df = period_df[["date", "period_start", "period_end", "luteal_length"]]
    # Get temperatures
    temp_df = temperatures_to_frame(temperatures, index=False)
    temp_df = temp_df.rename(columns={"timestamp": "date"})
    # For symptoms, we'll need to group the fields by date.
    # For each date, we'll aggregate the symptoms, mood, sex, and discharge lists.
    # For ovulation_test, any True on that date overrides any Falses on that date
    # For flow_intensity, we'll take the max intensity on that date.
    symptom_records: dict[str, models.SymptomSummary] = {}
    for symptom in symptoms:
        date_str = symptom.date.date().isoformat()
        if date_str not in symptom_records:
            symptom_records[date_str] = models.SymptomSummary()
        symptom_records[date_str].symptoms.update(symptom.symptoms or [])
        symptom_records[date_str].mood.update(symptom.mood or [])
        symptom_records[date_str].sex.update(symptom.sex or [])
        symptom_records[date_str].discharge.update(symptom.discharge or [])
        if symptom.ovulation_test:
            symptom_records[date_str].ovulation_test = True
        if symptom.flow_intensity is not None:
            symptom_records[date_str].flow_intensity = max(
                symptom_records[date_str].flow_intensity, symptom.flow_intensity
            )
    symptom_df = pd.DataFrame(
        [
            {"date": datetime.fromisoformat(date_str), **data.model_dump()}
            for date_str, data in symptom_records.items()
        ]
    )
    # Join all the lists into comma-separated strings for CSV output
    symptom_df["symptoms"] = [", ".join(map(str, sym)) for sym in symptom_df["symptoms"]]
    symptom_df["mood"] = [", ".join(map(str, mood)) for mood in symptom_df["mood"]]
    symptom_df["sex"] = [", ".join(map(str, sex)) for sex in symptom_df["sex"]]
    symptom_df["discharge"] = [
        ", ".join(map(str, discharge)) for discharge in symptom_df["discharge"]
    ]
    # Now merge all three DataFrames on date
    combined_df = pd.merge(period_df, temp_df, how="outer", on="date")
    combined_df = pd.merge(combined_df, symptom_df, how="outer", on="date")
    combined_df = combined_df.sort_values("date").reset_index(drop=True)
    return combined_df

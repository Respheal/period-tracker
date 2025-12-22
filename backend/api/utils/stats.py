from datetime import UTC, datetime
from typing import Sequence

import pandas as pd

from api.db import models
from api.utils.dependencies import get_settings

settings = get_settings()

# temps = [
#     {"timestamp": "2024-01-01T08:00:00Z", "temperature": 36.4},
#     {"timestamp": "2024-01-02T08:00:00Z", "temperature": 36.5},
#     {"timestamp": "2024-01-03T08:00:00Z", "temperature": 36.7},
#     {"timestamp": "2024-01-04T08:00:00Z", "temperature": 36.6},
#     {"timestamp": "2024-01-05T08:00:00Z", "temperature": 36.8},
#     {"timestamp": "2024-01-06T08:00:00Z", "temperature": 37.0},
#     {"timestamp": "2024-01-07T08:00:00Z", "temperature": 36.9},
#     {"timestamp": "2024-01-08T08:00:00Z", "temperature": 36.5},
#     {"timestamp": "2024-01-09T08:00:00Z", "temperature": 36.5},
#     {"timestamp": "2024-01-10T08:00:00Z", "temperature": 36.5},
#     {"timestamp": "2024-01-11T08:00:00Z", "temperature": 36.9},
#     {"timestamp": "2024-01-12T08:00:00Z", "temperature": 36.8},
#     {"timestamp": "2024-01-13T08:00:00Z", "temperature": 36.7},
#     {"timestamp": "2024-01-14T08:00:00Z", "temperature": 36.6},
#     {"timestamp": "2024-01-15T08:00:00Z", "temperature": 36.5},
#     {"timestamp": "2024-01-16T08:00:00Z", "temperature": 36.4},
#     {"timestamp": "2024-01-17T08:00:00Z", "temperature": 36.5},
#     {"timestamp": "2024-01-18T08:00:00Z", "temperature": 37.6},
#     {"timestamp": "2024-01-19T08:00:00Z", "temperature": 37.7},
#     {"timestamp": "2024-01-20T08:00:00Z", "temperature": 37.8},
# ]


def temperatures_to_frame(temps: Sequence[models.Temperature]) -> pd.DataFrame:
    """Convert Temperatures to a time-indexed DataFrame."""
    df = pd.DataFrame(
        [
            {"timestamp": pd.to_datetime(t.timestamp), "temperature": t.temperature}
            for t in temps
        ]
    )
    if df.empty:
        return df
    df = df.sort_values("timestamp").set_index("timestamp")
    return df


def compute_smoothed_temperature(df: pd.DataFrame) -> pd.Series:
    return df["temperature"].ewm(span=settings.SMOOTHING_SPAN_DAYS, adjust=False).mean()


def compute_baseline(df: pd.DataFrame) -> pd.Series:
    return df["temperature"].ewm(span=settings.BASELINE_SPAN_DAYS, adjust=False).mean()


def has_long_gap(df: pd.DataFrame) -> bool:
    if len(df) < 2:
        return False
    gaps = df.index.to_series().diff().dt.days  # type: ignore
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
    *,
    temperatures: Sequence[models.Temperature],
    previous_state: models.TemperatureState | None = None,
) -> models.TemperatureState:
    """
    Given all known temperatures for a user and their previous TemperatureState,
    return an updated TemperatureState.
    """
    now = datetime.now(UTC)
    df = temperatures_to_frame(temperatures)

    # Initialize state if missing
    state = previous_state or models.TemperatureState(phase=models.TempPhase.LEARNING)

    if df.empty:
        state.phase = models.TempPhase.LEARNING
        state.last_evaluated = now
        return state

    # Guardrail: long gaps break interpretation
    if has_long_gap(df):
        state.phase = models.TempPhase.UNKNOWN
        state.last_evaluated = now
        return state

    smoothed = compute_smoothed_temperature(df)

    # Establish baseline only after enough data
    if len(smoothed) < settings.MIN_POINTS_FOR_BASELINE:
        state.phase = models.TempPhase.LEARNING
        state.last_evaluated = now
        return state

    baseline_series = compute_baseline(df)
    baseline_value = baseline_series.iloc[-1]

    state.baseline = baseline_value

    if detect_elevated_phase(smoothed, baseline_value):
        state.phase = models.TempPhase.ELEVATED
    else:
        state.phase = models.TempPhase.LOW

    state.last_evaluated = now
    return state

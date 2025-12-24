from datetime import UTC, datetime, timedelta

import pandas as pd
from sqlmodel import Session

from api.db import models
from api.utils.config import Settings
from api.utils.stats import (
    compute_baseline,
    compute_smoothed_temperature,
    detect_elevated_phase,
    evaluate_temperature_state,
    has_long_gap,
    temperatures_to_frame,
)
from tests.utils.temp import create_temperature_readings
from tests.utils.user import create_random_user


class TestTemperaturesToFrame:
    def test_empty_temperatures(self) -> None:
        df = temperatures_to_frame([])
        assert df.empty

    def test_single_temperature(self, session: Session) -> None:
        user = create_random_user(session)
        now = datetime.now(UTC)
        temp = models.Temperature(
            user_id=user.user_id,
            temperature=36.5,
            timestamp=now,
        )
        df = temperatures_to_frame([temp])
        assert len(df) == 1
        assert df["temperature"].iloc[0] == 36.5

    def test_multiple_temperatures(self, session: Session) -> None:
        user = create_random_user(session)
        temps = create_temperature_readings(session, user, [36.5, 36.7, 36.9])
        df = temperatures_to_frame(temps)
        assert len(df) == 3
        assert df.index.name == "timestamp"
        assert all(df["temperature"].notna())

    def test_sorts_by_timestamp(self, session: Session) -> None:
        user = create_random_user(session)
        now = datetime.now(UTC)
        # Create readings out of order
        temp1 = models.Temperature(
            user_id=user.user_id, temperature=36.5, timestamp=now - timedelta(days=2)
        )
        temp2 = models.Temperature(user_id=user.user_id, temperature=36.7, timestamp=now)
        temp3 = models.Temperature(
            user_id=user.user_id, temperature=36.9, timestamp=now - timedelta(days=1)
        )
        df = temperatures_to_frame([temp2, temp1, temp3])
        assert len(df) == 3
        # Verify they're sorted
        temps_list = df["temperature"].tolist()
        assert temps_list[0] == 36.5  # oldest
        assert temps_list[1] == 36.9
        assert temps_list[2] == 36.7  # newest

    def test_averages_duplicate_days(self, session: Session) -> None:
        user = create_random_user(session)
        now = datetime.now(UTC).replace(hour=8, minute=0, second=0, microsecond=0)
        # Create two readings on the same day
        temp1 = models.Temperature(user_id=user.user_id, temperature=36.0, timestamp=now)
        temp2 = models.Temperature(
            user_id=user.user_id, temperature=37.0, timestamp=now + timedelta(hours=12)
        )
        df = temperatures_to_frame([temp1, temp2])
        # Should only have one row (averaged)
        assert len(df) == 1
        assert df["temperature"].iloc[0] == 36.5  # average of 36.0 and 37.0


class TestComputeSmoothedTemperature:
    def test_empty_dataframe(self) -> None:
        df = pd.DataFrame(columns=["temperature"])
        df = df.set_index(pd.DatetimeIndex([]))
        smoothed = compute_smoothed_temperature(df)
        assert len(smoothed) == 0

    def test_single_value(self, session: Session) -> None:
        user = create_random_user(session)
        temps = create_temperature_readings(session, user, [36.5])
        df = temperatures_to_frame(temps)
        smoothed = compute_smoothed_temperature(df)
        assert len(smoothed) == 1
        assert smoothed.iloc[0] == 36.5

    def test_smoothing_calculation(self, session: Session) -> None:
        user = create_random_user(session)
        # Create consistent temperatures
        temps = create_temperature_readings(session, user, [36.5] * 10)
        df = temperatures_to_frame(temps)
        smoothed = compute_smoothed_temperature(df)
        # All smoothed values should be close to 36.5
        assert all(abs(smoothed - 36.5) < 0.1)

    def test_smoothing_reduces_noise(self, session: Session) -> None:
        user = create_random_user(session)
        # Create noisy data
        temps = create_temperature_readings(
            session, user, [36.5, 37.5, 36.0, 37.0, 36.5, 37.0]
        )
        df = temperatures_to_frame(temps)
        smoothed = compute_smoothed_temperature(df)
        # Smoothed values should have less variance than raw
        assert smoothed.std() < df["temperature"].std()


class TestComputeBaseline:
    def test_baseline_calculation(self, session: Session) -> None:
        user = create_random_user(session)
        temps = create_temperature_readings(session, user, [36.5] * 30)
        df = temperatures_to_frame(temps)
        baseline = compute_baseline(df)
        assert len(baseline) == 30
        # Baseline should converge to the average
        assert abs(baseline.iloc[-1] - 36.5) < 0.1

    def test_baseline_span(self, session: Session) -> None:
        user = create_random_user(session)
        # Create temps with a shift in the middle
        temps = [36.0] * 15 + [37.0] * 15
        readings = create_temperature_readings(session, user, temps)
        df = temperatures_to_frame(readings)
        baseline = compute_baseline(df)
        # Baseline should be slower to respond than smoothed temp
        # (since BASELINE_SPAN_DAYS > SMOOTHING_SPAN_DAYS)
        assert baseline.iloc[-1] > 36.0
        assert baseline.iloc[-1] < 37.0


class TestHasLongGap:
    def test_no_gap(self, session: Session) -> None:
        user = create_random_user(session)
        temps = create_temperature_readings(session, user, [36.5] * 5)
        df = temperatures_to_frame(temps)
        assert not has_long_gap(df)

    def test_small_gap(self, session: Session) -> None:
        user = create_random_user(session)
        now = datetime.now(UTC)
        small_gap = Settings().MAX_MISSING_DAYS - 1
        temps = [
            models.Temperature(
                user_id=user.user_id,
                temperature=36.5,
                timestamp=now - timedelta(days=small_gap),
            ),
            models.Temperature(
                user_id=user.user_id,
                temperature=36.9,
                timestamp=now,
            ),
        ]
        session.add_all(temps)
        session.commit()
        df = temperatures_to_frame(temps)
        # Gap should be smaller than MAX_MISSING_DAYS and thus not trigger has_long_gap
        assert not has_long_gap(df)

    def test_long_gap(self, session: Session, settings: Settings) -> None:
        user = create_random_user(session)
        now = datetime.now(UTC)
        large_gap = settings.MAX_MISSING_DAYS + 1
        temps = []
        for i in [0, large_gap]:
            temps.append(
                models.Temperature(
                    user_id=user.user_id,
                    temperature=36.5 + i * 0.1,
                    timestamp=now - timedelta(days=10 - i),
                )
            )
        session.add_all(temps)
        session.commit()
        df = temperatures_to_frame(temps)
        # Gap of settings.MAX_MISSING_DAYS + 1 days should trigger has_long_gap
        assert has_long_gap(df)

    def test_less_than_two_readings(self) -> None:
        df = pd.DataFrame({"temperature": [36.5]})
        df.index = pd.DatetimeIndex([datetime.now(UTC)])
        assert not has_long_gap(df)


class TestDetectElevatedPhase:
    def test_insufficient_data(self) -> None:
        smoothed = pd.Series([36.5, 36.7])
        baseline = 36.5
        assert not detect_elevated_phase(smoothed, baseline)

    def test_no_elevation(self, session: Session) -> None:
        user = create_random_user(session)
        temps = create_temperature_readings(session, user, [36.5] * 10)
        df = temperatures_to_frame(temps)
        smoothed = compute_smoothed_temperature(df)
        baseline = 36.5
        assert not detect_elevated_phase(smoothed, baseline)

    def test_sustained_elevation(self, session: Session) -> None:
        user = create_random_user(session)
        # Low temps, then elevated temps
        temps = [36.5] * 10 + [37.2] * 5
        readings = create_temperature_readings(session, user, temps)
        df = temperatures_to_frame(readings)
        smoothed = compute_smoothed_temperature(df)
        baseline = 36.5
        # Should detect elevation
        assert detect_elevated_phase(smoothed, baseline)

    def test_brief_spike_not_elevated(self, session: Session) -> None:
        user = create_random_user(session)
        # One spike shouldn't trigger elevation
        temps = [36.5] * 5 + [37.5] + [36.5] * 4
        readings = create_temperature_readings(session, user, temps)
        df = temperatures_to_frame(readings)
        smoothed = compute_smoothed_temperature(df)
        baseline = 36.5
        # Brief spike should be smoothed out
        assert not detect_elevated_phase(smoothed, baseline)


class TestEvaluateTemperatureState:
    def test_empty_temperatures(self) -> None:
        state = evaluate_temperature_state([])
        assert state.phase == models.TempPhase.LEARNING
        assert state.baseline is None
        assert state.last_evaluated is not None

    def test_insufficient_data_learning_phase(self, session: Session) -> None:
        user = create_random_user(session)
        # Only a few readings
        temps = create_temperature_readings(session, user, [36.5, 36.7, 36.9])
        state = evaluate_temperature_state(temps)
        assert state.phase == models.TempPhase.LEARNING

    def test_long_gap_unknown_phase(self, session: Session, settings: Settings) -> None:
        user = create_random_user(session)
        now = datetime.now(UTC)
        # Create readings with a gap larger than MAX_MISSING_DAYS
        large_gap = settings.MAX_MISSING_DAYS + 1
        temps = [
            models.Temperature(
                user_id=user.user_id,
                temperature=36.5,
                timestamp=now - timedelta(days=large_gap + 5),
            ),
            models.Temperature(
                user_id=user.user_id,
                temperature=36.7,
                timestamp=now,
            ),
        ]
        session.add_all(temps)
        session.commit()
        state = evaluate_temperature_state(temps)
        # Should detect gap and mark as UNKNOWN
        assert state.phase == models.TempPhase.UNKNOWN

    def test_low_phase(self, session: Session) -> None:
        user = create_random_user(session)
        # Create a series of consistent low temps
        temps = create_temperature_readings(session, user, [36.5] * 15)
        state = evaluate_temperature_state(temps)
        assert state.phase == models.TempPhase.LOW
        assert state.baseline is not None
        assert abs(state.baseline - 36.5) < 0.2

    def test_elevated_phase(self, session: Session) -> None:
        user = create_random_user(session)
        # Low temps followed by sustained elevation
        temp_values = [36.5] * 15 + [37.2] * 5
        temps = create_temperature_readings(session, user, temp_values)
        state = evaluate_temperature_state(temps)
        assert state.phase == models.TempPhase.ELEVATED
        assert state.baseline is not None

    def test_preserves_previous_state(self, session: Session) -> None:
        user = create_random_user(session)
        temps = create_temperature_readings(session, user, [36.5] * 15)
        # Create initial state
        previous_state = models.TemperatureState(
            user_id=user.user_id,
            phase=models.TempPhase.LOW,
            baseline=36.5,
        )
        # Evaluate with previous state
        new_state = evaluate_temperature_state(temps, previous_state)
        # Verify the state is updated in place
        assert new_state.pid == previous_state.pid
        assert new_state.user_id == user.user_id
        assert new_state.last_evaluated is not None

    def test_transition_from_low_to_elevated(
        self, session: Session, settings: Settings
    ) -> None:
        user = create_random_user(session)

        # Start with low phase
        low_temps = [36.5] * 20
        temps = create_temperature_readings(session, user, low_temps)
        state = evaluate_temperature_state(temps)
        assert state.phase == models.TempPhase.LOW

        # Add significantly elevated temps to trigger detection
        # The elevation needs to be sustained and above threshold
        elevated_temps = [37.5] * (settings.ELEVATION_DAYS_REQUIRED + 1)
        new_temps = create_temperature_readings(
            session, user, elevated_temps, start_date=datetime.now(UTC)
        )
        all_temps = temps + new_temps
        new_state = evaluate_temperature_state(all_temps, state)
        # Note: Detection depends on smoothing and baseline calculations
        assert new_state.phase == models.TempPhase.ELEVATED

    def test_baseline_updates(self, session: Session) -> None:
        user = create_random_user(session)
        temps = create_temperature_readings(session, user, [36.5] * 15)
        state = evaluate_temperature_state(temps)

        # Baseline should be set
        assert state.baseline is not None
        initial_baseline = state.baseline

        # Add more temps at a different level
        new_temps = create_temperature_readings(
            session, user, [36.8] * 10, start_date=datetime.now(UTC)
        )
        all_temps = temps + new_temps
        new_state = evaluate_temperature_state(all_temps, state)

        # Baseline should update (slowly, due to EWM)
        assert new_state.baseline is not None
        assert new_state.baseline != initial_baseline


class TestTemperatureStateIntegration:
    def test_user_temp_state_relationship(self, session: Session) -> None:
        """Test that TemperatureState is properly linked to User."""
        user = create_random_user(session)
        session.refresh(user)

        # User should have an initialized temp_state
        assert user.temp_state is not None
        assert user.temp_state.phase == models.TempPhase.LEARNING
        assert user.temp_state.user_id == user.user_id

    def test_temp_state_cascade_delete(self, session: Session) -> None:
        """Test that deleting a user cascades to temp_state."""
        user = create_random_user(session)
        session.refresh(user)
        temp_state_id = user.temp_state.pid

        # Delete user
        session.delete(user)
        session.commit()

        # Temp state should be deleted too
        deleted_state = session.get(models.TemperatureState, temp_state_id)
        assert deleted_state is None

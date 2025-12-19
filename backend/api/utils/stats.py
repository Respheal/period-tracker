from typing import Sequence

from api.db import models
from api.utils.dependencies import get_settings


def get_temp_averages(
    readings: Sequence[models.Temperature],
) -> list[models.TempEMAverage]:
    """
    Calculate the Exponential Moving Average (EMA) for a list of temperature readings.
    """
    settings = get_settings()
    counter = 0
    average = 0.0
    temp_emas: list[models.TempEMAverage] = []

    for reading in readings:
        counter += 1
        average = average + (reading.temperature - average) / min(
            counter, settings.SMOOTHING_FACTOR
        )
        temp_ema = models.TempEMAverage.model_validate(
            {
                "temperature": reading.temperature,
                "timestamp": reading.timestamp,
                "average_temperature": average,
            }
        )
        temp_emas.append(temp_ema)
    return temp_emas

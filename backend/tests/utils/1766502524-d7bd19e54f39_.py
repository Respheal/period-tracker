import datetime
from collections.abc import Sequence

from api.db.models import Temperature

temps = [
    Temperature(
        pid=1,
        user_id="00651253-2a90-4c93-aff1-67c0379a5bd8",
        temperature=36.3,
        timestamp=datetime.datetime(2025, 12, 20, 15, 33, 12, 725180),
    ),
    Temperature(
        pid=2,
        user_id="00651253-2a90-4c93-aff1-67c0379a5bd8",
        temperature=36.9,
        timestamp=datetime.datetime(2025, 12, 19, 15, 33, 12, 725180),
    ),
    Temperature(
        pid=3,
        user_id="00651253-2a90-4c93-aff1-67c0379a5bd8",
        temperature=36.6,
        timestamp=datetime.datetime(2025, 12, 18, 15, 33, 12, 725180),
    ),
    Temperature(
        pid=4,
        user_id="00651253-2a90-4c93-aff1-67c0379a5bd8",
        temperature=36.6,
        timestamp=datetime.datetime(2025, 12, 17, 15, 33, 12, 725180),
    ),
    Temperature(
        pid=5,
        user_id="00651253-2a90-4c93-aff1-67c0379a5bd8",
        temperature=36.6,
        timestamp=datetime.datetime(2025, 12, 16, 15, 33, 12, 725180),
    ),
    Temperature(
        pid=6,
        user_id="00651253-2a90-4c93-aff1-67c0379a5bd8",
        temperature=35.8,
        timestamp=datetime.datetime(2025, 12, 15, 15, 33, 12, 725180),
    ),
    Temperature(
        pid=7,
        user_id="00651253-2a90-4c93-aff1-67c0379a5bd8",
        temperature=36.6,
        timestamp=datetime.datetime(2025, 12, 14, 15, 33, 12, 725180),
    ),
    Temperature(
        pid=8,
        user_id="00651253-2a90-4c93-aff1-67c0379a5bd8",
        temperature=36.3,
        timestamp=datetime.datetime(2025, 12, 13, 15, 33, 12, 725180),
    ),
    Temperature(
        pid=9,
        user_id="00651253-2a90-4c93-aff1-67c0379a5bd8",
        temperature=36.2,
        timestamp=datetime.datetime(2025, 12, 12, 15, 33, 12, 725180),
    ),
    Temperature(
        pid=10,
        user_id="00651253-2a90-4c93-aff1-67c0379a5bd8",
        temperature=36.5,
        timestamp=datetime.datetime(2025, 12, 11, 15, 33, 12, 725180),
    ),
    Temperature(
        pid=11,
        user_id="00651253-2a90-4c93-aff1-67c0379a5bd8",
        temperature=36.9,
        timestamp=datetime.datetime(2025, 12, 10, 15, 33, 12, 725180),
    ),
    Temperature(
        pid=12,
        user_id="00651253-2a90-4c93-aff1-67c0379a5bd8",
        temperature=36.8,
        timestamp=datetime.datetime(2025, 12, 9, 15, 33, 12, 725180),
    ),
    Temperature(
        pid=13,
        user_id="00651253-2a90-4c93-aff1-67c0379a5bd8",
        temperature=36.5,
        timestamp=datetime.datetime(2025, 12, 8, 15, 33, 12, 725180),
    ),
    Temperature(
        pid=14,
        user_id="00651253-2a90-4c93-aff1-67c0379a5bd8",
        temperature=36.3,
        timestamp=datetime.datetime(2025, 12, 7, 15, 33, 12, 725180),
    ),
    Temperature(
        pid=15,
        user_id="00651253-2a90-4c93-aff1-67c0379a5bd8",
        temperature=36.5,
        timestamp=datetime.datetime(2025, 12, 6, 15, 33, 12, 725180),
    ),
    Temperature(
        pid=16,
        user_id="00651253-2a90-4c93-aff1-67c0379a5bd8",
        temperature=36.8,
        timestamp=datetime.datetime(2025, 12, 5, 15, 33, 12, 725180),
    ),
    Temperature(
        pid=17,
        user_id="00651253-2a90-4c93-aff1-67c0379a5bd8",
        temperature=36.3,
        timestamp=datetime.datetime(2025, 12, 4, 15, 33, 12, 725180),
    ),
    Temperature(
        pid=18,
        user_id="00651253-2a90-4c93-aff1-67c0379a5bd8",
        temperature=37.1,
        timestamp=datetime.datetime(2025, 12, 3, 15, 33, 12, 725180),
    ),
    Temperature(
        pid=19,
        user_id="00651253-2a90-4c93-aff1-67c0379a5bd8",
        temperature=37.2,
        timestamp=datetime.datetime(2025, 12, 2, 15, 33, 12, 725180),
    ),
    Temperature(
        pid=20,
        user_id="00651253-2a90-4c93-aff1-67c0379a5bd8",
        temperature=36.4,
        timestamp=datetime.datetime(2025, 12, 1, 15, 33, 12, 725180),
    ),
    Temperature(
        pid=21,
        user_id="00651253-2a90-4c93-aff1-67c0379a5bd8",
        temperature=36.5,
        timestamp=datetime.datetime(2025, 11, 30, 15, 33, 12, 725180),
    ),
    Temperature(
        pid=22,
        user_id="00651253-2a90-4c93-aff1-67c0379a5bd8",
        temperature=35.8,
        timestamp=datetime.datetime(2025, 11, 29, 15, 33, 12, 725180),
    ),
    Temperature(
        pid=23,
        user_id="00651253-2a90-4c93-aff1-67c0379a5bd8",
        temperature=36.5,
        timestamp=datetime.datetime(2025, 11, 28, 15, 33, 12, 725180),
    ),
    Temperature(
        pid=24,
        user_id="00651253-2a90-4c93-aff1-67c0379a5bd8",
        temperature=36.5,
        timestamp=datetime.datetime(2025, 11, 27, 15, 33, 12, 725180),
    ),
    Temperature(
        pid=25,
        user_id="00651253-2a90-4c93-aff1-67c0379a5bd8",
        temperature=36.4,
        timestamp=datetime.datetime(2025, 11, 26, 15, 33, 12, 725180),
    ),
    Temperature(
        pid=26,
        user_id="00651253-2a90-4c93-aff1-67c0379a5bd8",
        temperature=36.9,
        timestamp=datetime.datetime(2025, 11, 25, 15, 33, 12, 725180),
    ),
    Temperature(
        pid=27,
        user_id="00651253-2a90-4c93-aff1-67c0379a5bd8",
        temperature=36.6,
        timestamp=datetime.datetime(2025, 11, 24, 15, 33, 12, 725180),
    ),
    Temperature(
        pid=28,
        user_id="00651253-2a90-4c93-aff1-67c0379a5bd8",
        temperature=37.5,
        timestamp=datetime.datetime(2025, 12, 22, 15, 33, 12, 725180),
    ),
    Temperature(
        user_id="00651253-2a90-4c93-aff1-67c0379a5bd8",
        temperature=37.5,
        timestamp=datetime.datetime(
            2025, 12, 21, 15, 33, 12, 725180, tzinfo=datetime.timezone.utc
        ),
        pid=29,
    ),
]
print()

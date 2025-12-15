import random
import string
from uuid import UUID


def random_lower_string() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=32))


def is_valid_uuid(value: str) -> bool:
    try:
        UUID(value)
        return True
    except ValueError:
        return False

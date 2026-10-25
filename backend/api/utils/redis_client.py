from functools import lru_cache

import redis

from api.utils.dependencies import get_settings


@lru_cache
def _get_pool(host: str, port: int, db: int) -> redis.ConnectionPool:
    # Shared connection pool for the given host, port, and db.
    return redis.ConnectionPool(
        host=host,
        port=port,
        db=db,
        protocol=3,
    )


def get_redis_client(db: int | None = None) -> redis.Redis:
    settings = get_settings()
    pool = _get_pool(
        settings.REDIS_HOST,
        settings.REDIS_PORT,
        db if db is not None else settings.REDIS_DB,
    )
    return redis.Redis(connection_pool=pool)

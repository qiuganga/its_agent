from typing import Any

from app.config.settings import settings
from app.infrastructure.logging.logger import logger


_redis_client: Any | None = None


def get_redis_client() -> Any | None:
    """Return a shared redis.asyncio client, or None when Redis is unavailable."""
    global _redis_client
    if _redis_client is not None:
        return _redis_client

    try:
        import redis.asyncio as redis
    except Exception as exc:
        logger.warning("Redis client package unavailable: %s", exc.__class__.__name__)
        return None

    try:
        _redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
    except Exception as exc:
        logger.error("Failed to create Redis client: %s", exc.__class__.__name__)
        return None

    return _redis_client

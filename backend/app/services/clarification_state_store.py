import json
import asyncio
from typing import Any

from app.config.settings import settings
from app.infrastructure.cache.redis_client import get_redis_client
from app.infrastructure.logging.logger import logger


REDIS_OPERATION_TIMEOUT_SECONDS = 0.25


class ClarificationStateStore:
    def __init__(self, redis_client: Any | None = None):
        self._redis_client = redis_client

    def _key(self, user_id: str, session_id: str | None) -> str:
        return f"clarification:{user_id}:{session_id or 'default_session'}"

    def _client(self) -> Any | None:
        if self._redis_client is not None:
            return self._redis_client
        return get_redis_client()

    async def set_state(
        self,
        user_id: str,
        session_id: str,
        state: dict,
        ttl_seconds: int | None = None,
    ) -> None:
        client = self._client()
        if client is None:
            return
        ttl = ttl_seconds or settings.CLARIFICATION_STATE_TTL_SECONDS
        try:
            await asyncio.wait_for(
                client.set(
                    self._key(user_id, session_id),
                    json.dumps(state, ensure_ascii=False),
                    ex=ttl,
                ),
                timeout=REDIS_OPERATION_TIMEOUT_SECONDS,
            )
        except Exception as exc:
            logger.warning(
                "Failed to write clarification state user_id=%s session_id=%s: %s",
                user_id,
                session_id,
                exc.__class__.__name__,
            )

    async def get_state(self, user_id: str, session_id: str) -> dict | None:
        client = self._client()
        if client is None:
            return None
        try:
            raw = await asyncio.wait_for(
                client.get(self._key(user_id, session_id)),
                timeout=REDIS_OPERATION_TIMEOUT_SECONDS,
            )
        except Exception as exc:
            logger.warning(
                "Failed to read clarification state user_id=%s session_id=%s: %s",
                user_id,
                session_id,
                exc.__class__.__name__,
            )
            return None
        if not raw:
            return None
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            logger.warning(
                "Invalid clarification state JSON user_id=%s session_id=%s",
                user_id,
                session_id,
            )
            return None
        return payload if isinstance(payload, dict) else None

    async def clear_state(self, user_id: str, session_id: str) -> None:
        client = self._client()
        if client is None:
            return
        try:
            await asyncio.wait_for(
                client.delete(self._key(user_id, session_id)),
                timeout=REDIS_OPERATION_TIMEOUT_SECONDS,
            )
        except Exception as exc:
            logger.warning(
                "Failed to clear clarification state user_id=%s session_id=%s: %s",
                user_id,
                session_id,
                exc.__class__.__name__,
            )


clarification_state_store = ClarificationStateStore()

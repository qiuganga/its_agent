import asyncio
import time
from dataclasses import dataclass, field


@dataclass
class SessionBudget:
    session_total_tool_calls: int = 0
    session_tool_call_count_by_name: dict[str, int] = field(default_factory=dict)
    session_total_sub_agent_calls: int = 0
    last_access_at: float = field(default_factory=time.monotonic)


class SessionBudgetStore:
    def __init__(self, ttl_seconds: int = 1800):
        self.ttl_seconds = ttl_seconds
        self._store: dict[tuple[str, str], SessionBudget] = {}
        self._lock = asyncio.Lock()

    async def reserve(
        self,
        *,
        user_id: str,
        session_id: str,
        tool_name: str,
        max_total_tool_calls: int,
        max_calls_per_session: int | None,
        count_as_sub_agent_call: bool,
    ) -> tuple[bool, str | None]:
        async with self._lock:
            self._cleanup_locked()
            key = (user_id, session_id)
            budget = self._store.setdefault(key, SessionBudget())
            budget.last_access_at = time.monotonic()

            if budget.session_total_tool_calls >= max_total_tool_calls:
                return False, "SESSION_TOOL_BUDGET_REACHED"

            current_tool_count = budget.session_tool_call_count_by_name.get(tool_name, 0)
            if max_calls_per_session is not None and current_tool_count >= max_calls_per_session:
                return False, "SESSION_TOOL_BUDGET_REACHED"

            budget.session_total_tool_calls += 1
            budget.session_tool_call_count_by_name[tool_name] = current_tool_count + 1
            if count_as_sub_agent_call:
                budget.session_total_sub_agent_calls += 1
            return True, None

    async def snapshot(self, user_id: str, session_id: str) -> SessionBudget | None:
        async with self._lock:
            self._cleanup_locked()
            return self._store.get((user_id, session_id))

    async def clear(self) -> None:
        async with self._lock:
            self._store.clear()

    def _cleanup_locked(self) -> None:
        now = time.monotonic()
        expired_keys = [
            key for key, budget in self._store.items()
            if now - budget.last_access_at > self.ttl_seconds
        ]
        for key in expired_keys:
            self._store.pop(key, None)

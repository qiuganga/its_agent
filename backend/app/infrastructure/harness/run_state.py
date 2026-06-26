import asyncio
import hashlib
import json
import re
import time
from dataclasses import dataclass, field
from typing import Any


def _normalize_value(value: Any) -> Any:
    if isinstance(value, str):
        return re.sub(r"\s+", " ", value.strip())
    if isinstance(value, dict):
        return {str(k): _normalize_value(v) for k, v in sorted(value.items(), key=lambda item: str(item[0]))}
    if isinstance(value, (list, tuple)):
        return [_normalize_value(v) for v in value]
    return value


def canonicalize_arguments(arguments: dict[str, Any]) -> str:
    normalized = _normalize_value(arguments or {})
    return json.dumps(normalized, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


def fingerprint_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def blocked_result(reason_code: str, message: str, next_action: str | None = None) -> dict[str, Any]:
    return {
        "ok": False,
        "harness_blocked": True,
        "reason_code": reason_code,
        "message": message,
        "next_action": next_action or "不要再次调用该工具；请使用之前已经返回的结果生成最终答复。",
    }


@dataclass
class RunHarnessState:
    run_id: str
    user_id: str
    session_id: str
    max_request_seconds: float
    started_at: float = field(default_factory=time.monotonic)
    total_agent_visible_tool_calls: int = 0
    total_sub_agent_tool_calls: int = 0
    tool_call_count_by_name: dict[str, int] = field(default_factory=dict)
    failed_count_by_name: dict[str, int] = field(default_factory=dict)
    seen_call_signatures: set[str] = field(default_factory=set)
    blocked_events: list[dict[str, Any]] = field(default_factory=list)
    trace_events: list[dict[str, Any]] = field(default_factory=list)
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock, repr=False)

    def elapsed_seconds(self) -> float:
        return time.monotonic() - self.started_at

    def deadline_exceeded(self) -> bool:
        return self.elapsed_seconds() >= self.max_request_seconds

    def remaining_seconds(self) -> float:
        return max(0.0, self.max_request_seconds - self.elapsed_seconds())

    async def trace(self, event: dict[str, Any]) -> None:
        async with self._lock:
            self.trace_events.append(event)

    async def mark_failed(self, tool_name: str) -> None:
        async with self._lock:
            self.failed_count_by_name[tool_name] = self.failed_count_by_name.get(tool_name, 0) + 1

    async def record_blocked(self, event: dict[str, Any]) -> None:
        async with self._lock:
            self.blocked_events.append(event)
            self.trace_events.append(event)

    async def reserve_tool_call(
        self,
        *,
        agent_name: str,
        tool_name: str,
        canonical_arguments: str,
        max_calls_per_run: int,
        max_total_calls: int,
        max_total_sub_agent_calls: int,
        count_toward_total_budget: bool,
        count_as_sub_agent_call: bool,
    ) -> tuple[bool, dict[str, Any] | None, str]:
        signature_raw = f"{agent_name}:{tool_name}:{canonical_arguments}"
        signature = fingerprint_text(signature_raw)
        argument_fingerprint = fingerprint_text(canonical_arguments)

        async with self._lock:
            if count_toward_total_budget and self.total_agent_visible_tool_calls >= max_total_calls:
                return False, blocked_result(
                    "RUN_TOTAL_TOOL_BUDGET_REACHED",
                    "本次请求的工具调用总预算已耗尽，系统已停止继续调用工具。",
                ), argument_fingerprint

            if count_as_sub_agent_call and self.total_sub_agent_tool_calls >= max_total_sub_agent_calls:
                return False, blocked_result(
                    "SUB_AGENT_TOOL_LIMIT_REACHED",
                    "本次请求的子 Agent 调用预算已耗尽，系统已阻止继续启动子 Agent。",
                ), argument_fingerprint

            current_tool_count = self.tool_call_count_by_name.get(tool_name, 0)
            if current_tool_count >= max_calls_per_run:
                return False, blocked_result(
                    "RUN_TOOL_LIMIT_REACHED",
                    f"当前请求中 {tool_name} 已达到每次请求调用上限。",
                ), argument_fingerprint

            if signature in self.seen_call_signatures:
                return False, blocked_result(
                    "DUPLICATE_TOOL_CALL",
                    "当前请求中相同工具和相同参数已经执行过，系统已阻止重复调用。",
                ), argument_fingerprint

            self.seen_call_signatures.add(signature)
            self.tool_call_count_by_name[tool_name] = current_tool_count + 1
            if count_toward_total_budget:
                self.total_agent_visible_tool_calls += 1
            if count_as_sub_agent_call:
                self.total_sub_agent_tool_calls += 1

        return True, None, argument_fingerprint

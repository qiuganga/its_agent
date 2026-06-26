import asyncio
import inspect
import time
from collections.abc import Awaitable, Callable
from typing import Any

from app.config.settings import settings
from app.infrastructure.harness.observability import log_harness_event
from app.infrastructure.harness.policy import HarnessPolicy, ToolPolicy, freeze_tool_policies
from app.infrastructure.harness.run_state import blocked_result, canonicalize_arguments
from app.infrastructure.harness.session_store import SessionBudgetStore


ActionCallable = Callable[[], Any | Awaitable[Any]]


class SystemHarness:
    def __init__(self, policy: HarnessPolicy):
        self.policy = policy
        self.session_store = SessionBudgetStore(ttl_seconds=policy.session_ttl_seconds)
        self.tool_semaphores = {
            name: asyncio.Semaphore(tool_policy.max_concurrency)
            for name, tool_policy in policy.tool_policies.items()
        }
        self.run_semaphore = asyncio.Semaphore(policy.max_concurrent_runs)

    async def acquire_run_slot(self) -> bool:
        if self.run_semaphore.locked():
            return False
        await self.run_semaphore.acquire()
        return True

    def release_run_slot(self) -> None:
        self.run_semaphore.release()

    async def invoke(
        self,
        *,
        run_context: Any,
        agent_key: str,
        tool_name: str,
        arguments: dict[str, Any],
        action: ActionCallable,
    ) -> Any:
        started_at = time.monotonic()
        run_state = run_context.run_state
        tool_policy = self.policy.get_tool_policy(tool_name)
        canonical_args = canonicalize_arguments(arguments)
        argument_fingerprint = ""

        async def block(reason_code: str, message: str, event_type: str = "tool_blocked") -> dict[str, Any]:
            result = blocked_result(reason_code, message)
            event = {
                "run_id": run_context.run_id,
                "user_id": run_context.user_id,
                "session_id": run_context.session_id,
                "agent_key": agent_key,
                "tool_name": tool_name,
                "event_type": event_type,
                "elapsed_ms": int((time.monotonic() - started_at) * 1000),
                "result_status": "blocked",
                "reason_code": reason_code,
                "argument_fingerprint": argument_fingerprint,
            }
            await run_state.record_blocked(event)
            log_harness_event(**event)
            return result

        if tool_policy is None:
            return await block(
                "TOOL_PERMISSION_DENIED",
                "该工具不在系统白名单中，已被 Harness 阻止。",
                "tool_blocked_permission",
            )

        if agent_key not in tool_policy.allowed_agents:
            return await block(
                "TOOL_PERMISSION_DENIED",
                "当前 Agent 无权调用该工具，已被 Harness 阻止。",
                "tool_blocked_permission",
            )

        if run_state.deadline_exceeded():
            return await block(
                "REQUEST_DEADLINE_EXCEEDED",
                "本次请求已超过最大执行时间，系统已停止继续调用工具。",
                "tool_blocked_deadline",
            )

        allowed, blocked, argument_fingerprint = await run_state.reserve_tool_call(
            agent_name=agent_key,
            tool_name=tool_name,
            canonical_arguments=canonical_args,
            max_calls_per_run=tool_policy.max_calls_per_run,
            max_total_calls=self.policy.max_total_agent_visible_tool_calls,
            max_total_sub_agent_calls=self.policy.max_total_sub_agent_tool_calls,
            count_toward_total_budget=tool_policy.count_toward_total_budget,
            count_as_sub_agent_call=tool_policy.count_as_sub_agent_call,
        )
        if not allowed:
            reason_code = str(blocked.get("reason_code")) if blocked else "HARNESS_BLOCKED"
            event_type = {
                "DUPLICATE_TOOL_CALL": "tool_blocked_duplicate",
                "RUN_TOOL_LIMIT_REACHED": "tool_blocked_run_limit",
                "RUN_TOTAL_TOOL_BUDGET_REACHED": "tool_blocked_run_limit",
                "SUB_AGENT_TOOL_LIMIT_REACHED": "tool_blocked_run_limit",
            }.get(reason_code, "tool_blocked")
            return await block(reason_code, str(blocked.get("message")), event_type)

        session_allowed, session_reason = await self.session_store.reserve(
            user_id=run_context.user_id,
            session_id=run_context.session_id,
            tool_name=tool_name,
            max_total_tool_calls=self.policy.session_max_total_tool_calls,
            max_calls_per_session=tool_policy.max_calls_per_session,
            count_as_sub_agent_call=tool_policy.count_as_sub_agent_call,
        )
        if not session_allowed:
            return await block(
                session_reason or "SESSION_TOOL_BUDGET_REACHED",
                "当前会话的工具调用预算已达到上限，系统已停止继续调用工具。",
                "tool_blocked_session_limit",
            )

        semaphore = self.tool_semaphores[tool_name]
        started_event = {
            "run_id": run_context.run_id,
            "user_id": run_context.user_id,
            "session_id": run_context.session_id,
            "agent_key": agent_key,
            "tool_name": tool_name,
            "event_type": "tool_started",
            "elapsed_ms": int((time.monotonic() - started_at) * 1000),
            "result_status": "started",
            "reason_code": None,
            "argument_fingerprint": argument_fingerprint,
        }
        await run_state.trace(started_event)
        log_harness_event(**started_event)

        async with semaphore:
            timeout_seconds = min(tool_policy.timeout_seconds, max(0.001, run_state.remaining_seconds()))
            try:
                maybe_result = action()
                if inspect.isawaitable(maybe_result):
                    result = await asyncio.wait_for(maybe_result, timeout=timeout_seconds)
                else:
                    result = maybe_result
            except asyncio.TimeoutError:
                await run_state.mark_failed(tool_name)
                return await block(
                    "TOOL_TIMEOUT",
                    "工具执行超时，系统已停止等待该工具结果。",
                    "tool_timeout",
                )
            except Exception as exc:
                await run_state.mark_failed(tool_name)
                event = {
                    "run_id": run_context.run_id,
                    "user_id": run_context.user_id,
                    "session_id": run_context.session_id,
                    "agent_key": agent_key,
                    "tool_name": tool_name,
                    "event_type": "tool_failed",
                    "elapsed_ms": int((time.monotonic() - started_at) * 1000),
                    "result_status": "failed",
                    "reason_code": exc.__class__.__name__,
                    "argument_fingerprint": argument_fingerprint,
                }
                await run_state.trace(event)
                log_harness_event(**event)
                return {
                    "ok": False,
                    "harness_error": True,
                    "reason_code": exc.__class__.__name__,
                    "message": "工具执行失败，系统已阻止自动重试。请基于已有信息回答，或提示用户稍后再试。",
                }

        event = {
            "run_id": run_context.run_id,
            "user_id": run_context.user_id,
            "session_id": run_context.session_id,
            "agent_key": agent_key,
            "tool_name": tool_name,
            "event_type": "tool_succeeded",
            "elapsed_ms": int((time.monotonic() - started_at) * 1000),
            "result_status": "succeeded",
            "reason_code": None,
            "argument_fingerprint": argument_fingerprint,
        }
        await run_state.trace(event)
        log_harness_event(**event)
        return result


def build_default_policy() -> HarnessPolicy:
    tool_policies = {
        "consult_technical_expert": ToolPolicy(
            tool_name="consult_technical_expert",
            allowed_agents=("orchestrator",),
            max_calls_per_run=1,
            max_calls_per_session=20,
            timeout_seconds=25,
            max_concurrency=10,
            count_as_sub_agent_call=True,
        ),
        "query_service_station_and_navigate": ToolPolicy(
            tool_name="query_service_station_and_navigate",
            allowed_agents=("orchestrator",),
            max_calls_per_run=1,
            max_calls_per_session=20,
            timeout_seconds=25,
            max_concurrency=10,
            count_as_sub_agent_call=True,
        ),
        "query_knowledge": ToolPolicy(
            tool_name="query_knowledge",
            allowed_agents=("technical_agent",),
            max_calls_per_run=1,
            max_calls_per_session=None,
            timeout_seconds=15,
            max_concurrency=10,
        ),
        "search_web": ToolPolicy(
            tool_name="search_web",
            allowed_agents=("technical_agent",),
            max_calls_per_run=1,
            max_calls_per_session=None,
            timeout_seconds=12,
            max_concurrency=5,
        ),
        "resolve_user_location_from_text": ToolPolicy(
            tool_name="resolve_user_location_from_text",
            allowed_agents=("service_agent",),
            max_calls_per_run=1,
            max_calls_per_session=None,
            timeout_seconds=12,
            max_concurrency=5,
        ),
        "query_nearest_repair_shops_by_coords": ToolPolicy(
            tool_name="query_nearest_repair_shops_by_coords",
            allowed_agents=("service_agent",),
            max_calls_per_run=1,
            max_calls_per_session=None,
            timeout_seconds=8,
            max_concurrency=10,
        ),
        "geocode_destination": ToolPolicy(
            tool_name="geocode_destination",
            allowed_agents=("service_agent",),
            max_calls_per_run=1,
            max_calls_per_session=None,
            timeout_seconds=10,
            max_concurrency=5,
        ),
        "map_navigation_tool": ToolPolicy(
            tool_name="map_navigation_tool",
            allowed_agents=("service_agent",),
            max_calls_per_run=1,
            max_calls_per_session=None,
            timeout_seconds=10,
            max_concurrency=5,
        ),
    }
    return HarnessPolicy(
        orchestrator_max_turns=settings.HARNESS_ORCHESTRATOR_MAX_TURNS,
        technical_agent_max_turns=settings.HARNESS_TECHNICAL_MAX_TURNS,
        service_agent_max_turns=settings.HARNESS_SERVICE_MAX_TURNS,
        max_total_agent_visible_tool_calls=settings.HARNESS_MAX_TOTAL_TOOL_CALLS_PER_RUN,
        max_total_sub_agent_tool_calls=settings.HARNESS_MAX_SUB_AGENT_TOOL_CALLS_PER_RUN,
        max_request_seconds=settings.HARNESS_MAX_REQUEST_SECONDS,
        max_concurrent_runs=settings.HARNESS_MAX_CONCURRENT_RUNS,
        session_ttl_seconds=settings.HARNESS_SESSION_TTL_SECONDS,
        session_max_total_tool_calls=settings.HARNESS_SESSION_MAX_TOTAL_TOOL_CALLS,
        trace_enabled=settings.HARNESS_TRACE_ENABLED,
        tool_policies=freeze_tool_policies(tool_policies),
    )


system_harness = SystemHarness(build_default_policy())

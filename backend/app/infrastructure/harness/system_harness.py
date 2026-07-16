import asyncio
import inspect
import time
import uuid
from collections.abc import Awaitable, Callable
from typing import Any

from app.config.settings import settings
from app.infrastructure.harness.observability import log_harness_event, log_mcp_contract_event
from app.infrastructure.harness.policy import HarnessPolicy, ToolPolicy, freeze_tool_policies
from app.infrastructure.harness.run_state import blocked_result, canonicalize_arguments, fingerprint_text
from app.infrastructure.harness.session_store import SessionBudgetStore
from app.infrastructure.tools.mcp.contracts.base import (
    McpResult,
    is_mcp_result_payload,
    mcp_result_to_agent_payload,
    result_item_count,
)


ActionCallable = Callable[[], Any | Awaitable[Any]]


def _infer_result_item_count(result: Any) -> int | None:
    if isinstance(result, McpResult):
        return result_item_count(result)
    if is_mcp_result_payload(result):
        try:
            return result_item_count(McpResult.model_validate(result))
        except Exception:
            return None
    if isinstance(result, dict):
        count = result.get("count")
        if isinstance(count, int):
            return count
        items = result.get("items")
        if isinstance(items, list):
            return len(items)
        data = result.get("data")
        if isinstance(data, list):
            return len(data)
    if isinstance(result, list):
        return len(result)
    return None


class SystemHarness:
    def __init__(self, policy: HarnessPolicy):
        self.policy = policy
        self.session_store = SessionBudgetStore(ttl_seconds=policy.session_ttl_seconds)
        self.tool_semaphores = {
            name: asyncio.Semaphore(tool_policy.max_concurrency)
            for name, tool_policy in policy.tool_policies.items()
        }
        self._run_slots: asyncio.Queue[int] = asyncio.Queue(maxsize=policy.max_concurrent_runs)
        for token in range(policy.max_concurrent_runs):
            self._run_slots.put_nowait(token)

    async def acquire_run_slot(self) -> bool:
        try:
            self._run_slots.get_nowait()
            return True
        except asyncio.QueueEmpty:
            return False

    def release_run_slot(self) -> None:
        try:
            self._run_slots.put_nowait(1)
        except asyncio.QueueFull:
            pass

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
        argument_fingerprint = fingerprint_text(canonical_args)
        tool_call_id = uuid.uuid4().hex
        active_started = False

        async def emit_started() -> None:
            nonlocal active_started
            if active_started:
                return
            active_started = True
            await run_state.emit_started_tool_event({
                "kind": "TOOL_STARTED",
                "tool_call_id": tool_call_id,
                "tool_name": tool_name,
                "status": "started",
                "argument_fingerprint": argument_fingerprint,
            })

        async def emit_result(
            *,
            status: str,
            ok: bool,
            error_code: str | None = None,
            result_item_count_value: int | None = None,
            latency_ms: int | None = None,
            schema_version: str | None = None,
            provider: str | None = None,
            retryable: bool | None = None,
            decrement_active: bool = False,
        ) -> None:
            await run_state.emit_terminal_tool_event({
                "kind": "TOOL_RESULT",
                "tool_call_id": tool_call_id,
                "tool_name": tool_name,
                "status": status,
                "ok": ok,
                "error_code": error_code,
                "result_item_count": result_item_count_value,
                "latency_ms": latency_ms if latency_ms is not None else int((time.monotonic() - started_at) * 1000),
                "schema_version": schema_version,
                "provider": provider,
                "retryable": retryable,
                "argument_fingerprint": argument_fingerprint,
            }, decrement_active=decrement_active)

        async def finish_tool_event(
            *,
            status: str,
            ok: bool,
            error_code: str | None = None,
            result_item_count_value: int | None = None,
            latency_ms: int | None = None,
            schema_version: str | None = None,
            provider: str | None = None,
            retryable: bool | None = None,
        ) -> None:
            nonlocal active_started
            try:
                await emit_result(
                    status=status,
                    ok=ok,
                    error_code=error_code,
                    result_item_count_value=result_item_count_value,
                    latency_ms=latency_ms,
                    schema_version=schema_version,
                    provider=provider,
                    retryable=retryable,
                    decrement_active=active_started,
                )
            finally:
                active_started = False

        async def record_event(event_type: str, result_status: str, reason_code: str | None = None) -> None:
            event = {
                "run_id": run_context.run_id,
                "user_id": run_context.user_id,
                "session_id": run_context.session_id,
                "agent_key": agent_key,
                "tool_name": tool_name,
                "event_type": event_type,
                "elapsed_ms": int((time.monotonic() - started_at) * 1000),
                "result_status": result_status,
                "reason_code": reason_code,
                "argument_fingerprint": argument_fingerprint,
            }
            await run_state.trace(event)
            log_harness_event(**event)

        async def record_mcp_result(result: McpResult[object]) -> None:
            error = result.error
            mcp_event = {
                "run_id": run_context.run_id,
                "user_id": run_context.user_id,
                "session_id": run_context.session_id,
                "agent_key": agent_key,
                "tool_name": tool_name,
                "provider": result.meta.provider,
                "mcp_tool_name": result.meta.tool_name,
                "schema_version": result.meta.schema_version,
                "mcp_ok": result.ok,
                "error_code": error.code if error else None,
                "retryable": error.retryable if error else None,
                "latency_ms": result.meta.latency_ms,
                "result_item_count": result_item_count(result),
                "argument_fingerprint": argument_fingerprint,
            }
            await run_state.trace({"event_type": "mcp_contract_result", **mcp_event})
            log_mcp_contract_event(**mcp_event)

        async def block(
            reason_code: str,
            message: str,
            event_type: str = "tool_blocked",
            tool_event_status: str = "blocked",
        ) -> dict[str, Any]:
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
            await finish_tool_event(status=tool_event_status, ok=False, error_code=reason_code)
            return result

        if tool_policy is None:
            return await block("TOOL_PERMISSION_DENIED", "\u8be5\u5de5\u5177\u4e0d\u5728\u7cfb\u7edf\u767d\u540d\u5355\u4e2d\uff0c\u5df2\u88ab Harness \u963b\u6b62\u3002", "tool_blocked_permission")

        if agent_key not in tool_policy.allowed_agents:
            return await block("TOOL_PERMISSION_DENIED", "\u5f53\u524d Agent \u65e0\u6743\u8c03\u7528\u8be5\u5de5\u5177\uff0c\u5df2\u88ab Harness \u963b\u6b62\u3002", "tool_blocked_permission")

        if run_state.deadline_exceeded():
            return await block("REQUEST_DEADLINE_EXCEEDED", "\u672c\u6b21\u8bf7\u6c42\u5df2\u8d85\u8fc7\u6700\u5927\u6267\u884c\u65f6\u95f4\uff0c\u7cfb\u7edf\u5df2\u505c\u6b62\u7ee7\u7eed\u8c03\u7528\u5de5\u5177\u3002", "tool_blocked_deadline")

        if await run_state.is_tool_failure_limit_reached(
            tool_name,
            self.policy.max_consecutive_tool_failures_per_run,
        ):
            return await block(
                "TOOL_CONSECUTIVE_FAILURE_LIMIT_REACHED",
                "\u8be5\u5de5\u5177\u5728\u672c\u6b21\u8bf7\u6c42\u4e2d\u5df2\u8fde\u7eed\u6267\u884c\u5931\u8d25\u591a\u6b21\uff0c\u7cfb\u7edf\u5df2\u505c\u6b62\u7ee7\u7eed\u91cd\u8bd5\u3002\u8bf7\u57fa\u4e8e\u5df2\u6709\u4fe1\u606f\u56de\u7b54\u3001\u6539\u7528\u5907\u7528\u80fd\u529b\uff0c\u6216\u63d0\u793a\u7528\u6237\u7a0d\u540e\u91cd\u8bd5\u3002",
                "tool_blocked_failure_limit",
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
                "\u5f53\u524d\u4f1a\u8bdd\u7684\u5de5\u5177\u8c03\u7528\u9884\u7b97\u5df2\u8fbe\u5230\u4e0a\u9650\uff0c\u7cfb\u7edf\u5df2\u505c\u6b62\u7ee7\u7eed\u8c03\u7528\u5de5\u5177\u3002",
                "tool_blocked_session_limit",
            )

        semaphore = self.tool_semaphores[tool_name]
        remaining_before_queue = run_state.remaining_seconds()
        if remaining_before_queue <= 0:
            return await block("REQUEST_DEADLINE_EXCEEDED", "\u672c\u6b21\u8bf7\u6c42\u5df2\u8d85\u8fc7\u6700\u5927\u6267\u884c\u65f6\u95f4\uff0c\u7cfb\u7edf\u5df2\u505c\u6b62\u7ee7\u7eed\u8c03\u7528\u5de5\u5177\u3002", "tool_blocked_deadline")

        await emit_started()
        await record_event("tool_queue_started", "started")
        acquired = False
        try:
            await asyncio.wait_for(semaphore.acquire(), timeout=remaining_before_queue)
            acquired = True
        except asyncio.CancelledError:
            await finish_tool_event(status="failed", ok=False, error_code="TOOL_CANCELLED")
            raise
        except asyncio.TimeoutError:
            await run_state.mark_tool_failed(tool_name)
            result = await block(
                "TOOL_QUEUE_TIMEOUT",
                "\u7b49\u5f85\u5de5\u5177\u5e76\u53d1\u540d\u989d\u65f6\uff0c\u672c\u6b21\u8bf7\u6c42\u7684\u5269\u4f59\u65f6\u95f4\u5df2\u7ecf\u8017\u5c3d\uff0c\u7cfb\u7edf\u5df2\u963b\u6b62\u6267\u884c\u771f\u5b9e\u5de5\u5177\u3002",
                "tool_queue_timeout",
                "timeout",
            )
            return result

        try:
            await record_event("tool_started", "started")
            timeout_seconds = min(tool_policy.timeout_seconds, max(0.001, run_state.remaining_seconds()))
            try:
                maybe_result = action()
                if inspect.isawaitable(maybe_result):
                    result = await asyncio.wait_for(maybe_result, timeout=timeout_seconds)
                else:
                    result = maybe_result
            except asyncio.CancelledError:
                await finish_tool_event(status="failed", ok=False, error_code="TOOL_CANCELLED")
                raise
            except asyncio.TimeoutError:
                await run_state.mark_tool_failed(tool_name)
                result = await block(
                    "TOOL_TIMEOUT",
                    "\u5de5\u5177\u6267\u884c\u8d85\u65f6\uff0c\u7cfb\u7edf\u5df2\u505c\u6b62\u7b49\u5f85\u8be5\u5de5\u5177\u7ed3\u679c\u3002",
                    "tool_timeout",
                    "timeout",
                )
                return result
            except Exception as exc:
                await run_state.mark_tool_failed(tool_name)
                await record_event("tool_failed", "failed", exc.__class__.__name__)
                await finish_tool_event(status="failed", ok=False, error_code=exc.__class__.__name__)
                return {
                    "ok": False,
                    "harness_error": True,
                    "reason_code": exc.__class__.__name__,
                    "message": "\u5de5\u5177\u6267\u884c\u5931\u8d25\uff0c\u7cfb\u7edf\u5df2\u963b\u6b62\u81ea\u52a8\u91cd\u8bd5\u3002\u8bf7\u57fa\u4e8e\u5df2\u6709\u4fe1\u606f\u56de\u7b54\uff0c\u6216\u63d0\u793a\u7528\u6237\u7a0d\u540e\u518d\u8bd5\u3002",
                }
        finally:
            if acquired:
                semaphore.release()

        if isinstance(result, McpResult):
            await record_mcp_result(result)
            payload = mcp_result_to_agent_payload(result)
            if result.ok:
                await run_state.mark_tool_succeeded(tool_name)
                await record_event("tool_succeeded", "succeeded")
                await finish_tool_event(
                    status="completed",
                    ok=True,
                    result_item_count_value=result_item_count(result),
                    latency_ms=result.meta.latency_ms,
                    schema_version=result.meta.schema_version,
                    provider=result.meta.provider,
                )
            else:
                await run_state.mark_tool_failed(tool_name)
                await record_event("tool_failed", "failed", result.error.code if result.error else "MCP_ERROR")
                await finish_tool_event(
                    status="failed",
                    ok=False,
                    error_code=result.error.code if result.error else "MCP_ERROR",
                    result_item_count_value=result_item_count(result),
                    latency_ms=result.meta.latency_ms,
                    schema_version=result.meta.schema_version,
                    provider=result.meta.provider,
                    retryable=result.error.retryable if result.error else None,
                )
            return payload

        if is_mcp_result_payload(result):
            parsed_result = McpResult.model_validate(result)
            await record_mcp_result(parsed_result)
            if parsed_result.ok:
                await run_state.mark_tool_succeeded(tool_name)
                await record_event("tool_succeeded", "succeeded")
                await finish_tool_event(
                    status="completed",
                    ok=True,
                    result_item_count_value=result_item_count(parsed_result),
                    latency_ms=parsed_result.meta.latency_ms,
                    schema_version=parsed_result.meta.schema_version,
                    provider=parsed_result.meta.provider,
                )
            else:
                await run_state.mark_tool_failed(tool_name)
                await record_event(
                    "tool_failed",
                    "failed",
                    parsed_result.error.code if parsed_result.error else "MCP_ERROR",
                )
                await finish_tool_event(
                    status="failed",
                    ok=False,
                    error_code=parsed_result.error.code if parsed_result.error else "MCP_ERROR",
                    result_item_count_value=result_item_count(parsed_result),
                    latency_ms=parsed_result.meta.latency_ms,
                    schema_version=parsed_result.meta.schema_version,
                    provider=parsed_result.meta.provider,
                    retryable=parsed_result.error.retryable if parsed_result.error else None,
                )
            return parsed_result.model_dump(mode="json")

        await run_state.mark_tool_succeeded(tool_name)
        await record_event("tool_succeeded", "succeeded")
        await finish_tool_event(
            status="completed",
            ok=True,
            result_item_count_value=_infer_result_item_count(result),
        )
        return result


def build_default_policy() -> HarnessPolicy:
    tool_policies = {
        "consult_technical_expert": ToolPolicy(
            tool_name="consult_technical_expert",
            allowed_agents=("orchestrator",),
            max_calls_per_run=1,
            max_calls_per_session=20,
            timeout_seconds=40,
            max_concurrency=10,
            count_as_sub_agent_call=True,
        ),
        "query_service_station_and_navigate": ToolPolicy(
            tool_name="query_service_station_and_navigate",
            allowed_agents=("orchestrator",),
            max_calls_per_run=1,
            max_calls_per_session=20,
            timeout_seconds=40,
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
        max_consecutive_tool_failures_per_run=settings.HARNESS_MAX_CONSECUTIVE_TOOL_FAILURES_PER_RUN,
        max_concurrent_runs=settings.HARNESS_MAX_CONCURRENT_RUNS,
        session_ttl_seconds=settings.HARNESS_SESSION_TTL_SECONDS,
        session_max_total_tool_calls=settings.HARNESS_SESSION_MAX_TOTAL_TOOL_CALLS,
        trace_enabled=settings.HARNESS_TRACE_ENABLED,
        tool_policies=freeze_tool_policies(tool_policies),
    )


system_harness = SystemHarness(build_default_policy())

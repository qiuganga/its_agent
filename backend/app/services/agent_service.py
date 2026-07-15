import asyncio
import json
import re
import time
import traceback
import uuid
from collections.abc import AsyncGenerator

from agents import MaxTurnsExceeded
from agents.run import RunConfig, Runner, ToolExecutionConfig

from app.infrastructure.harness.context import AgentRunContext
from app.infrastructure.harness.run_state import RunHarnessState
from app.infrastructure.harness.system_harness import system_harness
from app.infrastructure.logging.logger import logger
from app.multi_agent.orchestrator_agent import orchestrator_agent
from app.schemas.request import ChatMessageRequest
from app.schemas.clarification import is_clarification_payload
from app.schemas.response import ContentKind
from app.services.clarification_state_store import clarification_state_store
from app.services.session_service import session_service
from app.services.stream_response_service import process_stream_response
from app.utils.response_util import ResponseFactory


STOP_MESSAGE = (
    "本次请求已停止继续调用工具，避免重复执行或超出执行预算。"
    "请根据当前已返回的信息继续操作，或补充更明确的条件后重新提问。"
)

MAX_TURNS_MESSAGE = (
    "系统已达到本次任务的最大推理轮数，已停止继续执行，避免循环调用。"
    "请缩小问题范围或拆分为更具体的请求。"
)

RUN_TIMEOUT_MESSAGE = (
    "本次请求处理时间超过系统上限，已停止继续执行。"
    "请缩小问题范围、稍后重试，或拆分为更具体的问题。"
)


def _sse_text(text: str, kind: ContentKind = ContentKind.PROCESS) -> str:
    return "data: " + ResponseFactory.build_text(text, kind).model_dump_json() + "\n\n"


def _sse_finish() -> str:
    return "data: " + ResponseFactory.build_finish().model_dump_json() + "\n\n"


def _sse_clarification(payload: dict) -> str:
    return "data: " + ResponseFactory.build_clarification(payload).model_dump_json() + "\n\n"


def _is_finish_sse(chunk: str) -> bool:
    if not chunk.startswith("data: "):
        return False
    try:
        payload = json.loads(chunk[len("data: "):].strip())
    except json.JSONDecodeError:
        return False
    return payload.get("status") == "FINISHED" or payload.get("content", {}).get("contentType") == "sagegpt/finish"


def _extract_clarification_payload(value: object) -> dict | None:
    if isinstance(value, dict) and is_clarification_payload(value):
        return value
    if not isinstance(value, str):
        return None
    stripped = value.strip()
    if not (stripped.startswith("{") and stripped.endswith("}")):
        return None
    try:
        payload = json.loads(stripped)
    except json.JSONDecodeError:
        return None
    if is_clarification_payload(payload):
        return payload
    return None


def _build_clarification_state(payload: dict, original_query: str) -> dict:
    return {
        "status": "waiting_clarification",
        "clarification_type": payload.get("clarification_type"),
        "missing_fields": payload.get("missing_fields", []),
        "original_query": original_query,
        "last_clarification_question": payload.get("clarification_question"),
        "source": payload.get("source"),
        "suggested_examples": payload.get("suggested_examples", []),
    }


def _build_effective_user_query(user_query: str, state: dict | None) -> tuple[str, str | None]:
    if not isinstance(state, dict) or state.get("status") != "waiting_clarification":
        return user_query, None
    original_query = str(state.get("original_query") or "").strip()
    if not original_query:
        return user_query, None
    return (
        f"原始问题：{original_query}\n用户补充信息：{user_query}",
        original_query,
    )


async def _safe_get_clarification_state(user_id: str, session_id: str) -> dict | None:
    try:
        return await clarification_state_store.get_state(user_id, session_id)
    except Exception as exc:
        logger.warning(
            "Clarification state read failed user_id=%s session_id=%s: %s",
            user_id,
            session_id,
            exc.__class__.__name__,
        )
        return None


async def _safe_set_clarification_state(user_id: str, session_id: str, state: dict) -> None:
    try:
        await clarification_state_store.set_state(user_id, session_id, state)
    except Exception as exc:
        logger.warning(
            "Clarification state write failed user_id=%s session_id=%s: %s",
            user_id,
            session_id,
            exc.__class__.__name__,
        )


async def _safe_clear_clarification_state(user_id: str, session_id: str) -> None:
    try:
        await clarification_state_store.clear_state(user_id, session_id)
    except Exception as exc:
        logger.warning(
            "Clarification state clear failed user_id=%s session_id=%s: %s",
            user_id,
            session_id,
            exc.__class__.__name__,
        )


def _build_run_config(run_context: AgentRunContext) -> RunConfig:
    trace_enabled = run_context.system_harness.policy.trace_enabled
    return RunConfig(
        tracing_disabled=not trace_enabled,
        trace_include_sensitive_data=False,
        workflow_name="its_agent",
        group_id=run_context.session_id,
        trace_metadata={
            "run_id": run_context.run_id,
            "session_id": run_context.session_id,
        },
        tool_execution=ToolExecutionConfig(max_function_tool_concurrency=1),
    )


class MultiAgentService:
    @classmethod
    async def process_task(cls, request: ChatMessageRequest, flag: bool) -> AsyncGenerator:
        run_slot_acquired = False
        finish_emitted = False
        run_id = uuid.uuid4().hex
        user_id = request.context.user_id
        session_id = request.context.session_id
        user_query = request.query
        effective_user_query = user_query
        clarification_original_query: str | None = None
        run_state: RunHarnessState | None = None
        pending_finish_chunk: str | None = None

        async def emit_finish_once() -> str | None:
            nonlocal finish_emitted
            if finish_emitted:
                return None
            finish_emitted = True
            return _sse_finish()

        async def record_run_timeout() -> None:
            if run_state is None:
                return
            elapsed_ms = int(run_state.elapsed_seconds() * 1000)
            event = {
                "run_id": run_id,
                "user_id": user_id,
                "session_id": session_id,
                "event_type": "run_timeout",
                "elapsed_ms": elapsed_ms,
                "result_status": "timeout",
                "reason_code": "RUN_TIMEOUT",
            }
            await run_state.record_blocked(event)
            logger.warning(
                "Run %s timed out: elapsed_ms=%s max_request_seconds=%s",
                run_id,
                elapsed_ms,
                system_harness.policy.max_request_seconds,
            )

        async def record_run_cancelled() -> None:
            if run_state is None:
                return
            elapsed_ms = int(run_state.elapsed_seconds() * 1000)
            event = {
                "run_id": run_id,
                "user_id": user_id,
                "session_id": session_id,
                "event_type": "run_cancelled",
                "elapsed_ms": elapsed_ms,
                "result_status": "cancelled",
                "reason_code": "CLIENT_CANCELLED",
            }
            await run_state.trace(event)
            logger.warning("Run %s cancelled by client: elapsed_ms=%s", run_id, elapsed_ms)

        try:
            run_slot_acquired = await system_harness.acquire_run_slot()
            if not run_slot_acquired:
                yield _sse_text("系统繁忙，请稍后重试。")
                finish = await emit_finish_once()
                if finish:
                    yield finish
                return

            stored_clarification_state = await _safe_get_clarification_state(user_id, session_id)
            effective_user_query, clarification_original_query = _build_effective_user_query(
                user_query,
                stored_clarification_state,
            )

            run_state = RunHarnessState(
                run_id=run_id,
                user_id=user_id,
                session_id=session_id,
                max_request_seconds=system_harness.policy.max_request_seconds,
            )
            run_context = AgentRunContext(
                user_id=user_id,
                session_id=session_id,
                run_id=run_id,
                user_query=effective_user_query,
                system_harness=system_harness,
                run_state=run_state,
            )
            await run_state.trace({
                "run_id": run_id,
                "user_id": user_id,
                "session_id": session_id,
                "event_type": "run_started",
            })

            remaining_seconds = run_state.remaining_seconds()
            if remaining_seconds <= 0:
                raise asyncio.TimeoutError

            async with asyncio.timeout(remaining_seconds):
                full_history = session_service.prepare_full_history(user_id, session_id, effective_user_query)
                prompt_history = session_service.build_prompt_history(full_history)

                streaming_result = Runner.run_streamed(
                    starting_agent=orchestrator_agent,
                    input=prompt_history,
                    context=run_context,
                    max_turns=system_harness.policy.orchestrator_max_turns,
                    run_config=_build_run_config(run_context),
                )

                try:
                    stream_chunks = process_stream_response(streaming_result, run_context=run_context)
                except TypeError:
                    stream_chunks = process_stream_response(streaming_result)

                async for chunk in stream_chunks:
                    if _is_finish_sse(chunk):
                        pending_finish_chunk = chunk
                        continue
                    yield chunk

                agent_result = streaming_result.final_output or ""
                clarification_payload = _extract_clarification_payload(agent_result)
                if clarification_payload is None and run_state is not None:
                    clarification_payload = await run_state.get_pending_clarification()
                if clarification_payload:
                    original_query_for_state = clarification_original_query or user_query
                    await _safe_set_clarification_state(
                        user_id,
                        session_id,
                        _build_clarification_state(clarification_payload, original_query_for_state),
                    )
                    yield _sse_clarification(clarification_payload)
                    format_agent_result = re.sub(
                        r"\n+",
                        "\n",
                        clarification_payload.get("clarification_question") or "",
                    )
                else:
                    await _safe_clear_clarification_state(user_id, session_id)
                    format_agent_result = re.sub(r"\n+", "\n", str(agent_result))
                full_history.append({"role": "assistant", "content": format_agent_result})
                session_service.save_history(user_id, session_id, full_history)
                await run_state.trace({
                    "run_id": run_id,
                    "user_id": user_id,
                    "session_id": session_id,
                    "event_type": "run_finished",
                })
                if pending_finish_chunk:
                    finish_emitted = True
                    yield pending_finish_chunk
                else:
                    finish = await emit_finish_once()
                    if finish:
                        yield finish

        except asyncio.CancelledError:
            await record_run_cancelled()
            raise
        except TimeoutError:
            await record_run_timeout()
            yield _sse_text(RUN_TIMEOUT_MESSAGE)
            finish = await emit_finish_once()
            if finish:
                yield finish
        except MaxTurnsExceeded:
            logger.warning("Run %s reached max turns", run_id)
            yield _sse_text(MAX_TURNS_MESSAGE)
            finish = await emit_finish_once()
            if finish:
                yield finish
        except Exception as e:
            logger.error("AgentService.process_task failed for run %s: %s", run_id, str(e))
            logger.debug("Exception detail: %s", traceback.format_exc())
            yield _sse_text(STOP_MESSAGE)
            finish = await emit_finish_once()
            if finish:
                yield finish
        finally:
            if run_slot_acquired:
                system_harness.release_run_slot()

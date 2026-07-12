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
from app.schemas.response import ContentKind
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


def _is_finish_sse(chunk: str) -> bool:
    if not chunk.startswith("data: "):
        return False
    try:
        payload = json.loads(chunk[len("data: "):].strip())
    except json.JSONDecodeError:
        return False
    return payload.get("status") == "FINISHED" or payload.get("content", {}).get("contentType") == "sagegpt/finish"


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
                user_query=user_query,
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
                full_history = session_service.prepare_full_history(user_id, session_id, user_query)
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
                format_agent_result = re.sub(r"\n+", "\n", agent_result)
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

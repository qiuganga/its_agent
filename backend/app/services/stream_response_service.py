import asyncio
from collections.abc import AsyncGenerator
from typing import Any

from agents.items import ToolCallItem
from agents.run import RunResultStreaming
from openai.types.responses.response_stream_event import (
    ResponseReasoningSummaryTextDeltaEvent,
    ResponseReasoningTextDeltaEvent,
    ResponseTextDeltaEvent,
)

from app.schemas.response import ContentKind
from app.utils.response_util import ResponseFactory
from app.utils.text_util import format_agent_update_html, format_tool_call_html


def _sse_packet(packet) -> str:
    return "data: " + packet.model_dump_json() + "\n\n"


async def _next_model_event(model_iter) -> tuple[str, Any]:
    try:
        return "model", await model_iter.__anext__()
    except StopAsyncIteration:
        return "model_done", None


async def _next_tool_event(run_state) -> tuple[str, dict[str, Any]]:
    return "tool", await run_state.tool_event_queue.get()


async def _model_event_to_sse(event: Any) -> list[str]:
    chunks: list[str] = []

    if event.type == "raw_response_event":
        if isinstance(event.data, ResponseTextDeltaEvent):
            chunks.append(_sse_packet(ResponseFactory.build_text(event.data.delta, ContentKind.ANSWER)))
        elif ResponseReasoningTextDeltaEvent and isinstance(event.data, ResponseReasoningTextDeltaEvent):
            if event.data.delta:
                chunks.append(_sse_packet(ResponseFactory.build_text(event.data.delta, ContentKind.THINKING)))
        elif isinstance(event.data, ResponseReasoningSummaryTextDeltaEvent):
            if event.data.delta:
                chunks.append(_sse_packet(ResponseFactory.build_text(event.data.delta, ContentKind.THINKING)))

    elif event.type == "run_item_stream_event":
        if hasattr(event, "name") and event.name == "tool_called":
            if isinstance(event.item, ToolCallItem) and event.item.type == "tool_call_item":
                chunks.append(_sse_packet(ResponseFactory.build_text(
                    format_tool_call_html(event.item.raw_item.name),
                    ContentKind.PROCESS,
                )))

    elif event.type == "agent_updated_stream_event":
        chunks.append(_sse_packet(ResponseFactory.build_text(
            format_agent_update_html(event.new_agent.name),
            ContentKind.PROCESS,
        )))

    return chunks


async def process_stream_response(
    streaming_result: RunResultStreaming,
    run_context: Any | None = None,
) -> AsyncGenerator[str, None]:
    """
    Stream model events and per-run tool events as SSE.

    Tool events are consumed from RunHarnessState.tool_event_queue concurrently with
    model stream_events(), so TOOL_RESULT can reach the client before the model token
    stream finishes. The finish packet is emitted only after the model stream ends,
    active_tool_calls is zero, and the tool queue is drained.
    """
    run_state = getattr(run_context, "run_state", None)
    if run_state is None:
        async for event in streaming_result.stream_events():
            for chunk in await _model_event_to_sse(event):
                yield chunk
        yield _sse_packet(ResponseFactory.build_finish())
        return

    model_iter = streaming_result.stream_events().__aiter__()
    model_done = False
    model_task: asyncio.Task | None = asyncio.create_task(_next_model_event(model_iter))
    tool_task: asyncio.Task | None = asyncio.create_task(_next_tool_event(run_state))

    try:
        while True:
            tasks = [task for task in (model_task, tool_task) if task is not None]
            if not tasks:
                break

            done, _ = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            for task in done:
                source, value = await task
                if source == "model":
                    for chunk in await _model_event_to_sse(value):
                        yield chunk
                    model_task = asyncio.create_task(_next_model_event(model_iter))
                elif source == "model_done":
                    model_done = True
                    model_task = None
                elif source == "tool":
                    try:
                        yield _sse_packet(ResponseFactory.build_tool_event(value))
                    finally:
                        run_state.tool_event_queue.task_done()
                    tool_task = None

            if tool_task is None and not (model_done and await run_state.is_tool_event_idle()):
                tool_task = asyncio.create_task(_next_tool_event(run_state))

            if model_done and await run_state.is_tool_event_idle():
                if tool_task is not None and not tool_task.done():
                    tool_task.cancel()
                    tool_task = None
                break

        yield _sse_packet(ResponseFactory.build_finish())
    finally:
        for task in (model_task, tool_task):
            if task is not None and not task.done():
                task.cancel()

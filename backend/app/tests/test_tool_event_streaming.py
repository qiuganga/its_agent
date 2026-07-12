import asyncio
import json
import unittest

from app.infrastructure.harness.system_harness import SystemHarness
from app.infrastructure.tools.mcp.contracts import McpResult, SearchWebData, SearchWebItem
from app.services.stream_response_service import process_stream_response

from app.tests.test_harness_control import make_context, make_policy


def parse_sse(chunk: str) -> dict:
    assert chunk.startswith("data: ")
    return json.loads(chunk[len("data: "):].strip())


def collect_tool_events(chunks: list[str]) -> list[dict]:
    events = []
    for chunk in chunks:
        payload = parse_sse(chunk)
        content = payload.get("content", {})
        if content.get("contentType") == "sagegpt/tool_event":
            events.append(content["event"])
    return events


class EmptyDelayedStream:
    def __init__(self, delay: float = 0.02):
        self.delay = delay
        self.final_output = "done"

    async def stream_events(self):
        await asyncio.sleep(self.delay)
        if False:
            yield None


async def collect(generator):
    return [item async for item in generator]


class ToolEventStreamingTests(unittest.IsolatedAsyncioTestCase):
    async def test_success_tool_events_are_streamed_before_finish(self):
        harness = SystemHarness(make_policy(tool_limit=3, timeout=1.0))
        ctx = make_context(harness, run_id="tool-success-stream")

        async def invoke_tool():
            await asyncio.sleep(0.001)
            return await harness.invoke(
                run_context=ctx,
                agent_key="technical_agent",
                tool_name="search_web",
                arguments={"query": "screen black"},
                action=lambda: McpResult(
                    ok=True,
                    data=SearchWebData(items=[SearchWebItem(title="T", url="https://example.com", snippet="S")]),
                    error=None,
                    meta={"provider": "fake", "tool_name": "search_web", "schema_version": "v1", "latency_ms": 7},
                ),
            )

        tool_task = asyncio.create_task(invoke_tool())
        chunks = await collect(process_stream_response(EmptyDelayedStream(), run_context=ctx))
        await tool_task

        events = collect_tool_events(chunks)
        self.assertEqual([event["kind"] for event in events], ["TOOL_STARTED", "TOOL_RESULT"])
        self.assertEqual(events[0]["tool_call_id"], events[1]["tool_call_id"])
        self.assertEqual(events[1]["tool_name"], "search_web")
        self.assertTrue(events[1]["ok"])
        self.assertEqual(events[1]["status"], "completed")
        self.assertEqual(events[1]["result_item_count"], 1)
        self.assertEqual(events[1]["latency_ms"], 7)
        self.assertLess(events[1]["sequence"], parse_sse(chunks[-1]).get("content", {}).get("sequence", 10**9))
        self.assertEqual(parse_sse(chunks[-1])["content"]["contentType"], "sagegpt/finish")

    async def test_failed_mcp_result_emits_error_code(self):
        from app.infrastructure.tools.mcp.contracts import make_error_result

        harness = SystemHarness(make_policy(tool_limit=3, timeout=1.0))
        ctx = make_context(harness, run_id="tool-failed-stream")

        await harness.invoke(
            run_context=ctx,
            agent_key="technical_agent",
            tool_name="search_web",
            arguments={"query": "bad"},
            action=lambda: make_error_result(
                provider="fake",
                tool_name="search_web",
                code="MCP_PROVIDER_ERROR",
                message="failed",
            ),
        )

        started = await ctx.run_state.tool_event_queue.get()
        result = await ctx.run_state.tool_event_queue.get()
        self.assertEqual(started["kind"], "TOOL_STARTED")
        self.assertEqual(result["kind"], "TOOL_RESULT")
        self.assertFalse(result["ok"])
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["error_code"], "MCP_PROVIDER_ERROR")

    async def test_timeout_event_and_active_count_returns_to_zero(self):
        harness = SystemHarness(make_policy(tool_limit=3, timeout=0.01))
        ctx = make_context(harness, run_id="tool-timeout-stream")

        async def slow_action():
            await asyncio.sleep(0.1)
            return "late"

        await harness.invoke(
            run_context=ctx,
            agent_key="technical_agent",
            tool_name="query_knowledge",
            arguments={"question": "slow"},
            action=slow_action,
        )

        events = [await ctx.run_state.tool_event_queue.get(), await ctx.run_state.tool_event_queue.get()]
        self.assertEqual(events[1]["kind"], "TOOL_RESULT")
        self.assertEqual(events[1]["status"], "timeout")
        self.assertEqual(events[1]["error_code"], "TOOL_TIMEOUT")
        self.assertEqual(await ctx.run_state.get_active_tool_calls(), 0)

    async def test_blocked_precheck_emits_result_without_started(self):
        harness = SystemHarness(make_policy(tool_limit=3, timeout=1.0))
        ctx = make_context(harness, run_id="tool-blocked-stream")

        result = await harness.invoke(
            run_context=ctx,
            agent_key="orchestrator",
            tool_name="query_knowledge",
            arguments={"question": "blocked"},
            action=lambda: "should-not-run",
        )

        self.assertEqual(result["reason_code"], "TOOL_PERMISSION_DENIED")
        event = await ctx.run_state.tool_event_queue.get()
        self.assertEqual(event["kind"], "TOOL_RESULT")
        self.assertEqual(event["status"], "blocked")
        self.assertFalse(event["ok"])
        self.assertEqual(event["error_code"], "TOOL_PERMISSION_DENIED")
        self.assertTrue(ctx.run_state.tool_event_queue.empty())
        self.assertEqual(await ctx.run_state.get_active_tool_calls(), 0)

    async def test_terminal_event_and_active_zero_are_visible_atomically(self):
        harness = SystemHarness(make_policy(tool_limit=3, timeout=1.0))
        ctx = make_context(harness, run_id="tool-terminal-atomic")

        await ctx.run_state.emit_started_tool_event({
            "kind": "TOOL_STARTED",
            "tool_call_id": "call-1",
            "tool_name": "query_knowledge",
            "status": "started",
            "argument_fingerprint": "fp",
        })
        self.assertEqual(await ctx.run_state.get_active_tool_calls(), 1)

        await ctx.run_state.emit_terminal_tool_event({
            "kind": "TOOL_RESULT",
            "tool_call_id": "call-1",
            "tool_name": "query_knowledge",
            "status": "completed",
            "ok": True,
            "argument_fingerprint": "fp",
        }, decrement_active=True)

        self.assertEqual(await ctx.run_state.get_active_tool_calls(), 0)
        self.assertEqual(ctx.run_state.tool_event_queue.qsize(), 2)
        self.assertFalse(await ctx.run_state.is_tool_event_idle())
        started_event = await ctx.run_state.tool_event_queue.get()
        ctx.run_state.tool_event_queue.task_done()
        result_event = await ctx.run_state.tool_event_queue.get()
        ctx.run_state.tool_event_queue.task_done()
        self.assertEqual(started_event["kind"], "TOOL_STARTED")
        self.assertEqual(result_event["kind"], "TOOL_RESULT")
        self.assertLess(started_event["sequence"], result_event["sequence"])
        self.assertEqual(await ctx.run_state.get_active_tool_calls(), 0)
        self.assertTrue(await ctx.run_state.is_tool_event_idle())

    async def test_concurrent_tools_have_unique_ids_and_incrementing_sequence(self):
        harness = SystemHarness(make_policy(tool_limit=5, timeout=1.0, tool_concurrency=2))
        ctx = make_context(harness, run_id="tool-concurrent-stream")

        async def action(value):
            await asyncio.sleep(0.01)
            return {"ok": True, "count": value}

        await asyncio.gather(
            harness.invoke(
                run_context=ctx,
                agent_key="technical_agent",
                tool_name="query_knowledge",
                arguments={"question": "a"},
                action=lambda: action(1),
            ),
            harness.invoke(
                run_context=ctx,
                agent_key="technical_agent",
                tool_name="search_web",
                arguments={"query": "b"},
                action=lambda: action(2),
            ),
        )

        events = [await ctx.run_state.tool_event_queue.get() for _ in range(4)]
        sequences = [event["sequence"] for event in events]
        self.assertEqual(sequences, sorted(sequences))
        self.assertEqual(len({event["tool_call_id"] for event in events}), 2)
        by_id = {}
        for event in events:
            by_id.setdefault(event["tool_call_id"], []).append(event["kind"])
        self.assertEqual(sorted(by_id.values()), [["TOOL_STARTED", "TOOL_RESULT"], ["TOOL_STARTED", "TOOL_RESULT"]])

    async def test_tool_event_payload_does_not_expose_arguments_or_result_data(self):
        harness = SystemHarness(make_policy(tool_limit=3, timeout=1.0))
        ctx = make_context(harness, run_id="tool-scrub-stream")

        await harness.invoke(
            run_context=ctx,
            agent_key="technical_agent",
            tool_name="query_knowledge",
            arguments={"question": "secret raw argument"},
            action=lambda: {"ok": True, "data": [{"full_text": "secret raw result"}], "count": 1},
        )

        events = [await ctx.run_state.tool_event_queue.get(), await ctx.run_state.tool_event_queue.get()]
        serialized = json.dumps(events, ensure_ascii=False)
        self.assertNotIn("secret raw argument", serialized)
        self.assertNotIn("secret raw result", serialized)
        self.assertIn("argument_fingerprint", events[0])
        self.assertEqual(events[1]["result_item_count"], 1)


if __name__ == "__main__":
    unittest.main()

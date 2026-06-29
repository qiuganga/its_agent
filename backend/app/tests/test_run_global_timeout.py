import asyncio
import json
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from app.infrastructure.harness.context import AgentRunContext
from app.infrastructure.harness.run_state import RunHarnessState
from app.infrastructure.harness.system_harness import SystemHarness
from app.schemas.request import ChatMessageRequest, UserContext
from app.schemas.response import ContentKind
from app.services import agent_service
from app.utils.response_util import ResponseFactory

from app.tests.test_harness_control import make_context, make_policy


def text_sse(text: str, kind: ContentKind = ContentKind.ANSWER) -> str:
    return "data: " + ResponseFactory.build_text(text, kind).model_dump_json() + "\n\n"


def finish_sse() -> str:
    return "data: " + ResponseFactory.build_finish().model_dump_json() + "\n\n"


def is_finish(chunk: str) -> bool:
    payload = json.loads(chunk[len("data: "):].strip())
    return payload.get("content", {}).get("contentType") == "sagegpt/finish"


def chunk_text(chunk: str) -> str:
    payload = json.loads(chunk[len("data: "):].strip())
    return payload.get("content", {}).get("text", "")


async def collect(generator):
    return [item async for item in generator]


class FakeSessionService:
    def __init__(self):
        self.saved = []

    def prepare_history(self, user_id, session_id, user_query):
        return [{"role": "user", "content": user_query}]

    def save_history(self, user_id, session_id, chat_history):
        self.saved.append((user_id, session_id, list(chat_history)))


class FakeHarness:
    def __init__(self, *, max_request_seconds=1.0, slots=1):
        self.policy = SimpleNamespace(
            max_request_seconds=max_request_seconds,
            orchestrator_max_turns=5,
            trace_enabled=False,
        )
        self.slots = slots
        self.release_count = 0

    async def acquire_run_slot(self):
        if self.slots <= 0:
            return False
        self.slots -= 1
        return True

    def release_run_slot(self):
        self.release_count += 1
        self.slots += 1


class FakeStreamingResult:
    def __init__(self, final_output="final answer"):
        self.final_output = final_output


class GlobalRunTimeoutTests(unittest.IsolatedAsyncioTestCase):
    def make_request(self):
        return ChatMessageRequest(
            query="hello",
            context=UserContext(user_id="u1", session_id="s1"),
        )

    async def test_normal_stream_finishes_once_and_saves_history(self):
        fake_harness = FakeHarness(max_request_seconds=1.0)
        fake_session = FakeSessionService()

        async def fake_process_stream(streaming_result):
            yield text_sse("partial")
            yield finish_sse()

        with patch.object(agent_service, "system_harness", fake_harness), \
             patch.object(agent_service, "session_service", fake_session), \
             patch.object(agent_service.Runner, "run_streamed", return_value=FakeStreamingResult("done")), \
             patch.object(agent_service, "process_stream_response", fake_process_stream):
            chunks = await collect(agent_service.MultiAgentService.process_task(self.make_request(), True))

        self.assertIn("partial", "".join(chunk_text(chunk) for chunk in chunks if not is_finish(chunk)))
        self.assertNotIn("RUN_TIMEOUT", "".join(chunks))
        self.assertEqual(sum(1 for chunk in chunks if is_finish(chunk)), 1)
        self.assertEqual(len(fake_session.saved), 1)
        self.assertEqual(fake_session.saved[0][2][-1], {"role": "assistant", "content": "done"})
        self.assertEqual(fake_harness.release_count, 1)

    async def test_stream_timeout_emits_timeout_once_and_does_not_save_history(self):
        fake_harness = FakeHarness(max_request_seconds=0.05)
        fake_session = FakeSessionService()
        captured_contexts: list[AgentRunContext] = []

        def fake_run_streamed(*args, **kwargs):
            captured_contexts.append(kwargs["context"])
            return FakeStreamingResult("incomplete")

        async def fake_process_stream(streaming_result):
            yield text_sse("partial")
            await asyncio.sleep(1)
            yield finish_sse()

        with patch.object(agent_service, "system_harness", fake_harness), \
             patch.object(agent_service, "session_service", fake_session), \
             patch.object(agent_service.Runner, "run_streamed", side_effect=fake_run_streamed), \
             patch.object(agent_service, "process_stream_response", fake_process_stream):
            chunks = await collect(agent_service.MultiAgentService.process_task(self.make_request(), True))

        visible_text = "".join(chunk_text(chunk) for chunk in chunks if not is_finish(chunk))
        self.assertIn("partial", visible_text)
        self.assertIn("超过系统上限", visible_text)
        self.assertEqual(sum(1 for chunk in chunks if is_finish(chunk)), 1)
        self.assertEqual(fake_session.saved, [])
        self.assertEqual(fake_harness.release_count, 1)
        self.assertEqual(fake_harness.slots, 1)
        self.assertTrue(any(
            event.get("event_type") == "run_timeout" and event.get("reason_code") == "RUN_TIMEOUT"
            for event in captured_contexts[0].run_state.trace_events
        ))

    async def test_full_run_timeout_during_tool_execution_releases_tool_semaphore(self):
        harness = SystemHarness(make_policy(timeout=1.0, max_request_seconds=10.0, tool_concurrency=1))
        ctx = make_context(harness, run_id="global-tool-timeout")
        started = asyncio.Event()

        async def slow_action():
            started.set()
            await asyncio.sleep(1)
            return "late"

        task = asyncio.create_task(harness.invoke(
            run_context=ctx,
            agent_key="technical_agent",
            tool_name="query_knowledge",
            arguments={"question": "slow"},
            action=slow_action,
        ))
        await started.wait()
        with self.assertRaises(TimeoutError):
            async with asyncio.timeout(0.02):
                await task

        next_ctx = make_context(harness, run_id="after-global-tool-timeout")
        allowed = await harness.invoke(
            run_context=next_ctx,
            agent_key="technical_agent",
            tool_name="query_knowledge",
            arguments={"question": "fast"},
            action=lambda: "ok",
        )
        self.assertEqual(allowed, "ok")

    async def test_tool_timeout_is_not_converted_to_run_timeout(self):
        harness = SystemHarness(make_policy(timeout=0.01, max_request_seconds=1.0, tool_concurrency=1))
        ctx = make_context(harness, run_id="tool-timeout-first")

        async def slow_action():
            await asyncio.sleep(0.1)
            return "late"

        result = await harness.invoke(
            run_context=ctx,
            agent_key="technical_agent",
            tool_name="query_knowledge",
            arguments={"question": "slow"},
            action=slow_action,
        )
        self.assertEqual(result["reason_code"], "TOOL_TIMEOUT")
        self.assertFalse(any(event.get("reason_code") == "RUN_TIMEOUT" for event in ctx.run_state.trace_events))

    async def test_run_slot_full_does_not_start_runner_or_timeout_logic(self):
        fake_harness = FakeHarness(max_request_seconds=0.01, slots=0)
        fake_session = FakeSessionService()

        with patch.object(agent_service, "system_harness", fake_harness), \
             patch.object(agent_service, "session_service", fake_session), \
             patch.object(agent_service.Runner, "run_streamed") as run_streamed:
            chunks = await collect(agent_service.MultiAgentService.process_task(self.make_request(), True))

        visible_text = "".join(chunk_text(chunk) for chunk in chunks if not is_finish(chunk))
        self.assertIn("系统繁忙", visible_text)
        self.assertNotIn("超过系统上限", visible_text)
        self.assertEqual(sum(1 for chunk in chunks if is_finish(chunk)), 1)
        run_streamed.assert_not_called()
        self.assertEqual(fake_harness.release_count, 0)


if __name__ == "__main__":
    unittest.main()

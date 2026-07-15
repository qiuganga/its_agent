import json
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from app.schemas.clarification import make_clarification_result
from app.schemas.request import ChatMessageRequest, UserContext
from app.services import agent_service
from app.services.clarification_state_store import ClarificationStateStore
from app.tests.test_run_global_timeout import FakeHarness, FakeSessionService, FakeStreamingResult, collect, finish_sse


class FakeRedis:
    def __init__(self):
        self.values = {}
        self.ttls = {}

    async def set(self, key, value, ex=None):
        self.values[key] = value
        self.ttls[key] = ex

    async def get(self, key):
        return self.values.get(key)

    async def delete(self, key):
        self.values.pop(key, None)


class FailingRedis:
    async def set(self, *args, **kwargs):
        raise ConnectionError("redis down")

    async def get(self, *args, **kwargs):
        raise ConnectionError("redis down")

    async def delete(self, *args, **kwargs):
        raise ConnectionError("redis down")


class FakeClarificationStateStore:
    def __init__(self, state=None):
        self.state = state
        self.set_calls = []
        self.clear_calls = []

    async def get_state(self, user_id, session_id):
        return self.state

    async def set_state(self, user_id, session_id, state, ttl_seconds=None):
        self.set_calls.append((user_id, session_id, dict(state), ttl_seconds))
        self.state = state

    async def clear_state(self, user_id, session_id):
        self.clear_calls.append((user_id, session_id))
        self.state = None


class FailingClarificationStateStore:
    async def get_state(self, user_id, session_id):
        raise ConnectionError("redis down")

    async def set_state(self, user_id, session_id, state, ttl_seconds=None):
        raise ConnectionError("redis down")

    async def clear_state(self, user_id, session_id):
        raise ConnectionError("redis down")


async def finish_only_stream(streaming_result, run_context=None):
    yield finish_sse()


class ClarificationStateStoreTests(unittest.IsolatedAsyncioTestCase):
    async def test_set_get_clear_state(self):
        redis = FakeRedis()
        store = ClarificationStateStore(redis_client=redis)
        state = {
            "status": "waiting_clarification",
            "original_query": "附近服务站",
        }

        await store.set_state("u1", "s1", state, ttl_seconds=60)
        loaded = await store.get_state("u1", "s1")
        await store.clear_state("u1", "s1")

        self.assertEqual(loaded, state)
        self.assertIsNone(await store.get_state("u1", "s1"))
        self.assertEqual(redis.ttls["clarification:u1:s1"], 60)

    async def test_redis_errors_do_not_raise(self):
        store = ClarificationStateStore(redis_client=FailingRedis())

        await store.set_state("u1", "s1", {"status": "waiting_clarification"})
        self.assertIsNone(await store.get_state("u1", "s1"))
        await store.clear_state("u1", "s1")


class AgentClarificationStateIntegrationTests(unittest.IsolatedAsyncioTestCase):
    def make_request(self, query="北京中关村"):
        return ChatMessageRequest(
            query=query,
            context=UserContext(user_id="u1", session_id="s1"),
        )

    async def test_clarification_payload_writes_waiting_state(self):
        payload = make_clarification_result(
            clarification_type="missing_location",
            missing_fields=["city_or_address"],
            clarification_question="请提供城市或地址。",
            source="resolve_user_location_from_text",
            original_query="附近服务站",
        )
        fake_store = FakeClarificationStateStore()
        fake_session = FakeSessionService()

        with patch.object(agent_service, "system_harness", FakeHarness(max_request_seconds=1.0)), \
             patch.object(agent_service, "session_service", fake_session), \
             patch.object(agent_service, "clarification_state_store", fake_store), \
             patch.object(agent_service.Runner, "run_streamed", return_value=FakeStreamingResult(json.dumps(payload, ensure_ascii=False))), \
             patch.object(agent_service, "process_stream_response", finish_only_stream):
            await collect(agent_service.MultiAgentService.process_task(self.make_request("附近服务站"), True))

        self.assertEqual(len(fake_store.set_calls), 1)
        saved_state = fake_store.set_calls[0][2]
        self.assertEqual(saved_state["status"], "waiting_clarification")
        self.assertEqual(saved_state["original_query"], "附近服务站")
        self.assertEqual(saved_state["missing_fields"], ["city_or_address"])

    async def test_next_turn_uses_enhanced_query_from_waiting_state(self):
        fake_store = FakeClarificationStateStore({
            "status": "waiting_clarification",
            "original_query": "从我这里到最近的服务站的路线",
        })
        fake_session = FakeSessionService()
        captured = SimpleNamespace(context=None)

        def fake_run_streamed(*args, **kwargs):
            captured.context = kwargs["context"]
            return FakeStreamingResult("已找到路线")

        with patch.object(agent_service, "system_harness", FakeHarness(max_request_seconds=1.0)), \
             patch.object(agent_service, "session_service", fake_session), \
             patch.object(agent_service, "clarification_state_store", fake_store), \
             patch.object(agent_service.Runner, "run_streamed", side_effect=fake_run_streamed), \
             patch.object(agent_service, "process_stream_response", finish_only_stream):
            await collect(agent_service.MultiAgentService.process_task(self.make_request("我在北京中关村"), True))

        expected = "原始问题：从我这里到最近的服务站的路线\n用户补充信息：我在北京中关村"
        self.assertEqual(captured.context.user_query, expected)
        self.assertEqual(fake_session.saved[0][2][0]["content"], expected)
        self.assertEqual(fake_store.clear_calls, [("u1", "s1")])

    async def test_normal_completion_clears_waiting_state(self):
        fake_store = FakeClarificationStateStore({
            "status": "waiting_clarification",
            "original_query": "黑屏怎么办",
        })

        with patch.object(agent_service, "system_harness", FakeHarness(max_request_seconds=1.0)), \
             patch.object(agent_service, "session_service", FakeSessionService()), \
             patch.object(agent_service, "clarification_state_store", fake_store), \
             patch.object(agent_service.Runner, "run_streamed", return_value=FakeStreamingResult("最终答案")), \
             patch.object(agent_service, "process_stream_response", finish_only_stream):
            await collect(agent_service.MultiAgentService.process_task(self.make_request("ThinkPad T14 Windows 11"), True))

        self.assertEqual(fake_store.clear_calls, [("u1", "s1")])

    async def test_store_exception_does_not_break_main_flow(self):
        with patch.object(agent_service, "system_harness", FakeHarness(max_request_seconds=1.0)), \
             patch.object(agent_service, "session_service", FakeSessionService()), \
             patch.object(agent_service, "clarification_state_store", FailingClarificationStateStore()), \
             patch.object(agent_service.Runner, "run_streamed", return_value=FakeStreamingResult("最终答案")), \
             patch.object(agent_service, "process_stream_response", finish_only_stream):
            chunks = await collect(agent_service.MultiAgentService.process_task(self.make_request("hello"), True))

        self.assertTrue(chunks)


if __name__ == "__main__":
    unittest.main()

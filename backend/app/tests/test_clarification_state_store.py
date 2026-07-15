import json
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from app.multi_agent import agent_factory
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


class AgentFactoryClarificationPrecheckTests(unittest.TestCase):
    def test_service_station_missing_location_precheck(self):
        missing_location_query = "\u4ece\u6211\u8fd9\u91cc\u5230\u6700\u8fd1\u7684\u670d\u52a1\u7ad9\u7684\u8def\u7ebf"
        concrete_route_query = "\u5317\u4eac\u6545\u5bab\u5230\u4e09\u91cc\u5c6f\u7684\u8def\u7ebf"
        concrete_service_query = "\u6211\u5728\u5317\u4eac\u4e2d\u5173\u6751\uff0c\u53bb\u6700\u8fd1\u670d\u52a1\u7ad9"

        self.assertTrue(agent_factory._needs_location_clarification(missing_location_query))
        self.assertFalse(agent_factory._needs_location_clarification(concrete_route_query))
        self.assertFalse(agent_factory._needs_location_clarification(concrete_service_query))

    def test_vague_technical_precheck(self):
        vague_query = "\u7535\u8111\u9ed1\u5c4f\u600e\u4e48\u529e"
        detailed_query = "ThinkPad T14\uff0cWindows 11\uff0c\u5f00\u673a\u9ed1\u5c4f\u4f46\u7535\u6e90\u706f\u4eae"

        self.assertTrue(agent_factory._is_vague_technical_request(vague_query))
        self.assertFalse(agent_factory._is_vague_technical_request(detailed_query))


class PendingClarificationStateIntegrationTests(unittest.IsolatedAsyncioTestCase):
    async def test_pending_clarification_writes_state_when_final_output_is_text(self):
        original_query = "\u4ece\u6211\u8fd9\u91cc\u5230\u6700\u8fd1\u7684\u670d\u52a1\u7ad9\u7684\u8def\u7ebf"
        payload = make_clarification_result(
            clarification_type="missing_location",
            missing_fields=["city_or_address"],
            clarification_question="\u8bf7\u63d0\u4f9b\u4f60\u6240\u5728\u7684\u57ce\u5e02\u6216\u5177\u4f53\u5730\u5740\u3002",
            source="query_service_station_and_navigate",
            original_query=original_query,
        )
        fake_store = FakeClarificationStateStore()
        captured = SimpleNamespace(context=None)

        def fake_run_streamed(*args, **kwargs):
            captured.context = kwargs["context"]
            return FakeStreamingResult("\u4e3a\u4e86\u627e\u5230\u6700\u8fd1\u670d\u52a1\u7ad9\uff0c\u8bf7\u63d0\u4f9b\u6240\u5728\u57ce\u5e02\u3002")

        async def stream_with_pending_clarification(streaming_result, run_context=None):
            await captured.context.run_state.set_pending_clarification(payload)
            yield finish_sse()

        request = ChatMessageRequest(
            query=original_query,
            context=UserContext(user_id="u1", session_id="s1"),
        )
        with patch.object(agent_service, "system_harness", FakeHarness(max_request_seconds=1.0)), \
             patch.object(agent_service, "session_service", FakeSessionService()), \
             patch.object(agent_service, "clarification_state_store", fake_store), \
             patch.object(agent_service.Runner, "run_streamed", side_effect=fake_run_streamed), \
             patch.object(agent_service, "process_stream_response", stream_with_pending_clarification):
            await collect(agent_service.MultiAgentService.process_task(request, True))

        self.assertEqual(len(fake_store.set_calls), 1)
        saved_state = fake_store.set_calls[0][2]
        self.assertEqual(saved_state["status"], "waiting_clarification")
        self.assertEqual(saved_state["original_query"], original_query)
        self.assertEqual(saved_state["missing_fields"], ["city_or_address"])


if __name__ == "__main__":
    unittest.main()

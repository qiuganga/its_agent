import asyncio
import inspect
import json
import time
import unittest
from types import SimpleNamespace

from app.infrastructure.harness.context import AgentRunContext
from app.infrastructure.harness.policy import HarnessPolicy, ToolPolicy, freeze_tool_policies
from app.infrastructure.harness.run_state import RunHarnessState
from app.infrastructure.harness.system_harness import SystemHarness, build_default_policy


def make_policy(
    *,
    max_total=8,
    session_total=80,
    timeout=1.0,
    tool_limit=2,
    max_request_seconds=45,
    max_runs=20,
    tool_concurrency=10,
    failure_limit=2,
):
    policies = {
        "consult_technical_expert": ToolPolicy(
            tool_name="consult_technical_expert",
            allowed_agents=("orchestrator",),
            max_calls_per_run=tool_limit,
            max_calls_per_session=20,
            timeout_seconds=timeout,
            max_concurrency=10,
            count_as_sub_agent_call=True,
        ),
        "query_service_station_and_navigate": ToolPolicy(
            tool_name="query_service_station_and_navigate",
            allowed_agents=("orchestrator",),
            max_calls_per_run=tool_limit,
            max_calls_per_session=20,
            timeout_seconds=timeout,
            max_concurrency=10,
            count_as_sub_agent_call=True,
        ),
        "query_knowledge": ToolPolicy(
            tool_name="query_knowledge",
            allowed_agents=("technical_agent",),
            max_calls_per_run=tool_limit,
            max_calls_per_session=None,
            timeout_seconds=timeout,
            max_concurrency=tool_concurrency,
        ),
        "search_web": ToolPolicy(
            tool_name="search_web",
            allowed_agents=("technical_agent",),
            max_calls_per_run=tool_limit,
            max_calls_per_session=None,
            timeout_seconds=timeout,
            max_concurrency=5,
        ),
        "map_navigation_tool": ToolPolicy(
            tool_name="map_navigation_tool",
            allowed_agents=("service_agent",),
            max_calls_per_run=tool_limit,
            max_calls_per_session=None,
            timeout_seconds=timeout,
            max_concurrency=5,
        ),
    }
    return HarnessPolicy(
        orchestrator_max_turns=5,
        technical_agent_max_turns=4,
        service_agent_max_turns=5,
        max_total_agent_visible_tool_calls=max_total,
        max_total_sub_agent_tool_calls=2,
        max_request_seconds=max_request_seconds,
        max_consecutive_tool_failures_per_run=failure_limit,
        max_concurrent_runs=max_runs,
        session_ttl_seconds=1800,
        session_max_total_tool_calls=session_total,
        trace_enabled=False,
        tool_policies=freeze_tool_policies(policies),
    )


def make_context(harness, *, user_id="u1", session_id="s1", run_id="r1"):
    state = RunHarnessState(
        run_id=run_id,
        user_id=user_id,
        session_id=session_id,
        max_request_seconds=harness.policy.max_request_seconds,
    )
    return AgentRunContext(
        user_id=user_id,
        session_id=session_id,
        run_id=run_id,
        user_query="test",
        system_harness=harness,
        run_state=state,
    )


class HarnessControlTests(unittest.IsolatedAsyncioTestCase):
    async def test_default_service_agent_tool_timeout_allows_model_finalization(self):
        policy = build_default_policy()
        service_policy = policy.get_tool_policy("query_service_station_and_navigate")
        technical_policy = policy.get_tool_policy("consult_technical_expert")
        map_policy = policy.get_tool_policy("map_navigation_tool")
        knowledge_policy = policy.get_tool_policy("query_knowledge")

        self.assertIsNotNone(service_policy)
        self.assertIsNotNone(technical_policy)
        self.assertIsNotNone(map_policy)
        self.assertIsNotNone(knowledge_policy)
        self.assertGreater(service_policy.timeout_seconds, map_policy.timeout_seconds)
        self.assertGreater(technical_policy.timeout_seconds, knowledge_policy.timeout_seconds)
        self.assertLess(service_policy.timeout_seconds, policy.max_request_seconds)
        self.assertLess(technical_policy.timeout_seconds, policy.max_request_seconds)
        self.assertGreaterEqual(policy.max_request_seconds - service_policy.timeout_seconds, 20)
        self.assertGreaterEqual(policy.max_request_seconds - technical_policy.timeout_seconds, 20)

    async def test_same_run_duplicate_tool_call_executes_once(self):
        harness = SystemHarness(make_policy(tool_limit=2))
        ctx = make_context(harness)
        calls = 0

        async def action():
            nonlocal calls
            calls += 1
            return {"ok": True}

        first = await harness.invoke(
            run_context=ctx,
            agent_key="technical_agent",
            tool_name="query_knowledge",
            arguments={"question": "  hello   world "},
            action=action,
        )
        second = await harness.invoke(
            run_context=ctx,
            agent_key="technical_agent",
            tool_name="query_knowledge",
            arguments={"question": "hello world"},
            action=action,
        )

        self.assertEqual(first, {"ok": True})
        self.assertEqual(calls, 1)
        self.assertTrue(second["harness_blocked"])
        self.assertEqual(second["reason_code"], "DUPLICATE_TOOL_CALL")

    async def test_per_run_tool_limit_blocks_second_different_call(self):
        harness = SystemHarness(make_policy(tool_limit=1))
        ctx = make_context(harness)
        calls = 0

        async def action():
            nonlocal calls
            calls += 1
            return "ok"

        await harness.invoke(
            run_context=ctx,
            agent_key="orchestrator",
            tool_name="consult_technical_expert",
            arguments={"query": "a"},
            action=action,
        )
        blocked = await harness.invoke(
            run_context=ctx,
            agent_key="orchestrator",
            tool_name="consult_technical_expert",
            arguments={"query": "b"},
            action=action,
        )

        self.assertEqual(calls, 1)
        self.assertEqual(blocked["reason_code"], "RUN_TOOL_LIMIT_REACHED")

    async def test_total_tool_budget_blocks_after_limit(self):
        harness = SystemHarness(make_policy(max_total=1, tool_limit=2))
        ctx = make_context(harness)

        async def action():
            return "ok"

        await harness.invoke(
            run_context=ctx,
            agent_key="technical_agent",
            tool_name="query_knowledge",
            arguments={"question": "a"},
            action=action,
        )
        blocked = await harness.invoke(
            run_context=ctx,
            agent_key="technical_agent",
            tool_name="search_web",
            arguments={"query": "b"},
            action=action,
        )

        self.assertEqual(blocked["reason_code"], "RUN_TOTAL_TOOL_BUDGET_REACHED")

    async def test_session_budget_is_per_user_session(self):
        harness = SystemHarness(make_policy(session_total=1, tool_limit=2))

        async def action():
            return "ok"

        first_ctx = make_context(harness, session_id="same", run_id="r1")
        second_ctx = make_context(harness, session_id="same", run_id="r2")
        other_ctx = make_context(harness, session_id="other", run_id="r3")

        await harness.invoke(
            run_context=first_ctx,
            agent_key="technical_agent",
            tool_name="query_knowledge",
            arguments={"question": "a"},
            action=action,
        )
        blocked = await harness.invoke(
            run_context=second_ctx,
            agent_key="technical_agent",
            tool_name="query_knowledge",
            arguments={"question": "a"},
            action=action,
        )
        allowed = await harness.invoke(
            run_context=other_ctx,
            agent_key="technical_agent",
            tool_name="query_knowledge",
            arguments={"question": "a"},
            action=action,
        )

        self.assertEqual(blocked["reason_code"], "SESSION_TOOL_BUDGET_REACHED")
        self.assertEqual(allowed, "ok")

    async def test_duplicate_state_is_not_shared_between_runs(self):
        harness = SystemHarness(make_policy(tool_limit=2))
        calls = 0

        async def action():
            nonlocal calls
            calls += 1
            return "ok"

        for run_id in ("r1", "r2"):
            ctx = make_context(harness, run_id=run_id)
            result = await harness.invoke(
                run_context=ctx,
                agent_key="technical_agent",
                tool_name="query_knowledge",
                arguments={"question": "same"},
                action=action,
            )
            self.assertEqual(result, "ok")

        self.assertEqual(calls, 2)

    async def test_permission_control_blocks_wrong_agents(self):
        harness = SystemHarness(make_policy())
        ctx = make_context(harness)

        async def action():
            return "should-not-run"

        blocked_a = await harness.invoke(
            run_context=ctx,
            agent_key="orchestrator",
            tool_name="query_knowledge",
            arguments={"question": "x"},
            action=action,
        )
        blocked_b = await harness.invoke(
            run_context=ctx,
            agent_key="technical_agent",
            tool_name="map_navigation_tool",
            arguments={"origin": "a", "destination": "b"},
            action=action,
        )

        self.assertEqual(blocked_a["reason_code"], "TOOL_PERMISSION_DENIED")
        self.assertEqual(blocked_b["reason_code"], "TOOL_PERMISSION_DENIED")

    async def test_timeout_returns_blocked_result_without_retry(self):
        harness = SystemHarness(make_policy(timeout=0.01))
        ctx = make_context(harness)
        calls = 0

        async def action():
            nonlocal calls
            calls += 1
            await asyncio.sleep(0.1)
            return "late"

        blocked = await harness.invoke(
            run_context=ctx,
            agent_key="technical_agent",
            tool_name="query_knowledge",
            arguments={"question": "slow"},
            action=action,
        )

        self.assertEqual(calls, 1)
        self.assertEqual(blocked["reason_code"], "TOOL_TIMEOUT")

    async def test_tool_queue_timeout_does_not_start_action(self):
        harness = SystemHarness(make_policy(timeout=1.0, max_request_seconds=1.0, tool_concurrency=1))
        first_ctx = make_context(harness, run_id="queue-a")
        second_ctx = make_context(harness, run_id="queue-b")
        second_ctx.run_state.started_at = time.monotonic() - 0.88
        first_started = asyncio.Event()
        second_calls = 0

        async def slow_action():
            first_started.set()
            await asyncio.sleep(0.2)
            return "slow"

        async def should_not_start():
            nonlocal second_calls
            second_calls += 1
            return "bad"

        first_task = asyncio.create_task(harness.invoke(
            run_context=first_ctx,
            agent_key="technical_agent",
            tool_name="query_knowledge",
            arguments={"question": "hold"},
            action=slow_action,
        ))
        await first_started.wait()
        blocked = await harness.invoke(
            run_context=second_ctx,
            agent_key="technical_agent",
            tool_name="query_knowledge",
            arguments={"question": "wait"},
            action=should_not_start,
        )
        await first_task

        self.assertEqual(blocked["reason_code"], "TOOL_QUEUE_TIMEOUT")
        self.assertEqual(second_calls, 0)

    async def test_tool_timeout_releases_semaphore(self):
        harness = SystemHarness(make_policy(timeout=0.01, tool_concurrency=1))
        first_ctx = make_context(harness, run_id="timeout-a")
        second_ctx = make_context(harness, run_id="timeout-b")
        calls = 0

        async def slow_action():
            nonlocal calls
            calls += 1
            await asyncio.sleep(0.1)
            return "late"

        async def fast_action():
            return "ok"

        blocked = await harness.invoke(
            run_context=first_ctx,
            agent_key="technical_agent",
            tool_name="query_knowledge",
            arguments={"question": "slow"},
            action=slow_action,
        )
        allowed = await harness.invoke(
            run_context=second_ctx,
            agent_key="technical_agent",
            tool_name="query_knowledge",
            arguments={"question": "fast"},
            action=fast_action,
        )

        self.assertEqual(blocked["reason_code"], "TOOL_TIMEOUT")
        self.assertEqual(calls, 1)
        self.assertEqual(allowed, "ok")

    async def test_consecutive_tool_failure_limit_blocks_without_consuming_new_budget(self):
        harness = SystemHarness(make_policy(timeout=0.01, tool_limit=5, failure_limit=2))
        ctx = make_context(harness)
        calls = 0

        async def slow_action():
            nonlocal calls
            calls += 1
            await asyncio.sleep(0.1)
            return "late"

        for question in ("a", "b"):
            result = await harness.invoke(
                run_context=ctx,
                agent_key="technical_agent",
                tool_name="query_knowledge",
                arguments={"question": question},
                action=slow_action,
            )
            self.assertEqual(result["reason_code"], "TOOL_TIMEOUT")

        run_budget_before = ctx.run_state.total_agent_visible_tool_calls
        session_before = await harness.session_store.snapshot(ctx.user_id, ctx.session_id)

        blocked = await harness.invoke(
            run_context=ctx,
            agent_key="technical_agent",
            tool_name="query_knowledge",
            arguments={"question": "c"},
            action=slow_action,
        )

        session_after = await harness.session_store.snapshot(ctx.user_id, ctx.session_id)
        self.assertEqual(blocked["reason_code"], "TOOL_CONSECUTIVE_FAILURE_LIMIT_REACHED")
        self.assertEqual(calls, 2)
        self.assertEqual(ctx.run_state.total_agent_visible_tool_calls, run_budget_before)
        self.assertEqual(session_after.session_total_tool_calls, session_before.session_total_tool_calls)

        other_tool = await harness.invoke(
            run_context=ctx,
            agent_key="service_agent",
            tool_name="map_navigation_tool",
            arguments={"origin": "x", "destination": "y"},
            action=lambda: "ok",
        )
        self.assertEqual(other_tool, "ok")

    async def test_success_resets_consecutive_failure_count_but_keeps_total_failures(self):
        harness = SystemHarness(make_policy(timeout=0.01, tool_limit=5, failure_limit=2))
        ctx = make_context(harness)

        async def slow_action():
            await asyncio.sleep(0.1)
            return "late"

        first = await harness.invoke(
            run_context=ctx,
            agent_key="technical_agent",
            tool_name="query_knowledge",
            arguments={"question": "first"},
            action=slow_action,
        )
        second = await harness.invoke(
            run_context=ctx,
            agent_key="technical_agent",
            tool_name="query_knowledge",
            arguments={"question": "second"},
            action=lambda: {"ok": True, "data": []},
        )
        third = await harness.invoke(
            run_context=ctx,
            agent_key="technical_agent",
            tool_name="query_knowledge",
            arguments={"question": "third"},
            action=slow_action,
        )

        self.assertEqual(first["reason_code"], "TOOL_TIMEOUT")
        self.assertEqual(second, {"ok": True, "data": []})
        self.assertEqual(third["reason_code"], "TOOL_TIMEOUT")
        self.assertEqual(ctx.run_state.failed_count_by_name["query_knowledge"], 2)
        self.assertEqual(ctx.run_state.consecutive_failed_count_by_name["query_knowledge"], 1)

    async def test_empty_or_business_error_results_do_not_count_as_harness_failures(self):
        harness = SystemHarness(make_policy(tool_limit=5, failure_limit=2))
        ctx = make_context(harness)

        empty_result = await harness.invoke(
            run_context=ctx,
            agent_key="technical_agent",
            tool_name="query_knowledge",
            arguments={"question": "empty"},
            action=lambda: {"ok": True, "count": 0, "data": []},
        )
        business_error = await harness.invoke(
            run_context=ctx,
            agent_key="technical_agent",
            tool_name="query_knowledge",
            arguments={"question": "not-found"},
            action=lambda: {"ok": False, "error": "not found"},
        )
        third = await harness.invoke(
            run_context=ctx,
            agent_key="technical_agent",
            tool_name="query_knowledge",
            arguments={"question": "still-allowed"},
            action=lambda: "ok",
        )

        self.assertEqual(empty_result, {"ok": True, "count": 0, "data": []})
        self.assertEqual(business_error, {"ok": False, "error": "not found"})
        self.assertEqual(third, "ok")
        self.assertNotIn("query_knowledge", ctx.run_state.failed_count_by_name)
        self.assertEqual(ctx.run_state.consecutive_failed_count_by_name["query_knowledge"], 0)

    async def test_run_slot_acquire_is_atomic_and_non_blocking(self):
        harness = SystemHarness(make_policy(max_runs=3))

        results = await asyncio.gather(*(harness.acquire_run_slot() for _ in range(20)))
        self.assertEqual(sum(1 for item in results if item), 3)

        for _ in range(3):
            harness.release_run_slot()

        reacquired = [await harness.acquire_run_slot() for _ in range(4)]
        self.assertEqual(reacquired, [True, True, True, False])
        for _ in range(3):
            harness.release_run_slot()

    async def test_search_web_serializes_blocked_dict(self):
        from app.infrastructure.tools.local.knowledge_base import search_web

        class FakeHarness:
            async def invoke(self, **kwargs):
                return {"ok": False, "harness_blocked": True, "reason_code": "DUPLICATE_TOOL_CALL"}

        ctx = SimpleNamespace(
            context=SimpleNamespace(system_harness=FakeHarness()),
            tool_name="search_web",
            run_config=SimpleNamespace(trace_include_sensitive_data=False),
        )
        result = await search_web.on_invoke_tool(ctx, json.dumps({"query": "hello"}))
        parsed = json.loads(result)
        self.assertTrue(parsed["harness_blocked"])
        self.assertEqual(parsed["reason_code"], "DUPLICATE_TOOL_CALL")

    def test_process_task_does_not_recurse_on_errors(self):
        from app.services.agent_service import MultiAgentService

        source = inspect.getsource(MultiAgentService.process_task)
        self.assertNotIn("process_task(request", source)
        self.assertNotIn("flag=False", source)

    def test_child_agents_do_not_expose_raw_mcp_servers(self):
        from app.multi_agent.service_agent import comprehensive_service_agent
        from app.multi_agent.technical_agent import technical_agent

        self.assertFalse(getattr(technical_agent, "mcp_servers", None))
        self.assertFalse(getattr(comprehensive_service_agent, "mcp_servers", None))

        technical_tool_names = {tool.name for tool in technical_agent.tools}
        service_tool_names = {tool.name for tool in comprehensive_service_agent.tools}

        self.assertEqual(technical_tool_names, {"query_knowledge", "search_web"})
        self.assertEqual(
            service_tool_names,
            {
                "resolve_user_location_from_text",
                "query_nearest_repair_shops_by_coords",
                "geocode_destination",
                "map_navigation_tool",
            },
        )


if __name__ == "__main__":
    unittest.main()

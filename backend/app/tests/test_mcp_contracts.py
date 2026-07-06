import asyncio
import json
import unittest
from types import SimpleNamespace

from app.infrastructure.harness.observability import scrub_metadata
from app.infrastructure.harness.system_harness import SystemHarness
from app.infrastructure.tools.mcp.contracts import (
    GeocodeDestinationData,
    LocationData,
    McpResult,
    QueryNearestRepairShopsData,
    RepairShopItem,
    SearchWebData,
    adapt_exception,
    adapt_provider_response,
    call_mcp_with_contract,
    make_error_result,
)
from app.infrastructure.tools.mcp.contracts.adapter import (
    MCP_INPUT_VALIDATION_ERROR,
    MCP_PROVIDER_AUTH_ERROR,
    MCP_PROVIDER_ERROR,
    MCP_RESPONSE_JSON_INVALID,
    MCP_RESPONSE_SCHEMA_INVALID,
    MCP_TIMEOUT,
)
from app.tests.test_harness_control import make_context, make_policy


class FakeContent:
    def __init__(self, text):
        self.text = text


class FakeMcpReturn:
    def __init__(self, text):
        self.content = [FakeContent(text)]


class McpContractAdapterTests(unittest.IsolatedAsyncioTestCase):
    def test_dict_raw_response_standardizes_search_items(self):
        result = adapt_provider_response(
            provider="bailian",
            tool_name="search_web",
            raw_result={"pages": [{"title": "T", "url": "https://example.com", "snippet": "S"}]},
        )

        self.assertTrue(result.ok)
        self.assertIsInstance(result.data, SearchWebData)
        self.assertEqual(result.data.items[0].title, "T")

    def test_valid_json_string_standardizes_geocode(self):
        result = adapt_provider_response(
            provider="baidu_map",
            tool_name="geocode_destination",
            raw_result='{"status":0,"result":{"location":{"lat":39.9,"lng":116.4},"formatted_address":"北京"}}',
        )

        self.assertTrue(result.ok)
        self.assertIsInstance(result.data, GeocodeDestinationData)
        self.assertEqual(result.data.lat, 39.9)

    def test_plain_text_is_wrapped_as_stable_data(self):
        result = adapt_provider_response(
            provider="baidu_map",
            tool_name="map_navigation_tool",
            raw_result="https://map.baidu.com/direction",
        )

        self.assertTrue(result.ok)
        self.assertEqual(result.data.url, "https://map.baidu.com/direction")

    def test_empty_result_is_success_not_failure(self):
        result = adapt_provider_response(
            provider="bailian",
            tool_name="search_web",
            raw_result=None,
        )

        self.assertTrue(result.ok)
        self.assertEqual(result.data.items, [])

    def test_invalid_json_returns_contract_error(self):
        result = adapt_provider_response(
            provider="bailian",
            tool_name="search_web",
            raw_result='{"pages":',
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.error.code, MCP_RESPONSE_JSON_INVALID)

    def test_schema_invalid_returns_contract_error(self):
        result = adapt_provider_response(
            provider="baidu_map",
            tool_name="geocode_destination",
            raw_result={"result": {"location": {"lat": {"bad": "type"}, "lng": 116.4}}},
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.error.code, MCP_RESPONSE_SCHEMA_INVALID)

    def test_timeout_exception_is_retryable(self):
        result = adapt_exception(
            provider="bailian",
            tool_name="search_web",
            exc=asyncio.TimeoutError(),
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.error.code, MCP_TIMEOUT)
        self.assertTrue(result.error.retryable)

    def test_auth_error_is_not_retryable(self):
        result = adapt_exception(
            provider="baidu_map",
            tool_name="geocode_destination",
            exc=RuntimeError("401 unauthorized api key"),
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.error.code, MCP_PROVIDER_AUTH_ERROR)
        self.assertFalse(result.error.retryable)

    async def test_input_validation_error_does_not_call_provider(self):
        calls = 0

        async def action(args):
            nonlocal calls
            calls += 1
            return {"pages": []}

        result = await call_mcp_with_contract(
            provider="bailian",
            tool_name="search_web",
            arguments={"query": "  "},
            action=action,
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.error.code, MCP_INPUT_VALIDATION_ERROR)
        self.assertEqual(calls, 0)

    async def test_fake_mcp_content_object_is_adapted(self):
        result = await call_mcp_with_contract(
            provider="bailian",
            tool_name="search_web",
            arguments={"query": "hello"},
            action=lambda _args: asyncio.sleep(0, result=FakeMcpReturn('{"pages":[{"title":"A"}]}')),
        )

        self.assertTrue(result.ok)
        self.assertEqual(result.data.items[0].title, "A")

    def test_provider_business_error_is_stable(self):
        result = adapt_provider_response(
            provider="baidu_map",
            tool_name="resolve_user_location_from_text",
            raw_result={"status": 2, "message": "provider failed"},
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.error.code, MCP_PROVIDER_ERROR)

    def test_agent_payload_does_not_include_raw_response(self):
        result = adapt_provider_response(
            provider="bailian",
            tool_name="search_web",
            raw_result={
                "pages": [{"title": "T", "raw_response": "secret"}],
                "raw_response": {"Authorization": "Bearer secret"},
            },
        )

        payload = result.model_dump(mode="json")
        self.assertNotIn("raw_response", json.dumps(payload))
        self.assertNotIn("Authorization", json.dumps(payload))

    def test_sensitive_log_fields_are_scrubbed(self):
        scrubbed = scrub_metadata({
            "Authorization": "Bearer secret",
            "api_key": "secret",
            "password": "secret",
            "provider": "baidu_map",
        })

        self.assertEqual(scrubbed["Authorization"], "***")
        self.assertEqual(scrubbed["api_key"], "***")
        self.assertEqual(scrubbed["password"], "***")
        self.assertEqual(scrubbed["provider"], "baidu_map")

    def test_location_ip_fixture_success(self):
        result = adapt_provider_response(
            provider="baidu_map",
            tool_name="resolve_user_location_from_text",
            raw_result={"status": 0, "content": {"point": {"x": "12958160.0", "y": "4825907.0"}}},
        )

        self.assertTrue(result.ok)
        self.assertIsInstance(result.data, LocationData)
        self.assertEqual(result.data.source, "ip")

    def test_navigation_failure_fixture(self):
        result = adapt_provider_response(
            provider="baidu_map",
            tool_name="map_navigation_tool",
            raw_result={"error": {"code": "AUTH", "message": "forbidden"}},
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.error.code, MCP_PROVIDER_AUTH_ERROR)

    def test_repair_shop_contract_model_exists_without_mcp_semantics(self):
        data = QueryNearestRepairShopsData(
            items=[RepairShopItem(id=1, service_station_name="A", address="B")],
            count=1,
            lat=39.9,
            lng=116.4,
            limit=3,
        )

        self.assertEqual(data.count, 1)
        self.assertEqual(data.items[0].service_station_name, "A")


class McpHarnessIntegrationTests(unittest.IsolatedAsyncioTestCase):
    async def test_harness_counts_mcp_failure_result(self):
        harness = SystemHarness(make_policy(tool_limit=5, failure_limit=2))
        ctx = make_context(harness)

        result = await harness.invoke(
            run_context=ctx,
            agent_key="technical_agent",
            tool_name="search_web",
            arguments={"query": "a"},
            action=lambda: make_error_result(
                provider="fake",
                tool_name="search_web",
                code="MCP_PROVIDER_ERROR",
                message="failed",
            ),
        )

        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["code"], "MCP_PROVIDER_ERROR")
        self.assertEqual(ctx.run_state.failed_count_by_name["search_web"], 1)

    async def test_harness_does_not_count_empty_mcp_success_as_failure(self):
        harness = SystemHarness(make_policy(tool_limit=5, failure_limit=2))
        ctx = make_context(harness)

        result = await harness.invoke(
            run_context=ctx,
            agent_key="technical_agent",
            tool_name="search_web",
            arguments={"query": "empty"},
            action=lambda: McpResult(
                ok=True,
                data=SearchWebData(items=[]),
                error=None,
                meta={"provider": "fake", "tool_name": "search_web", "schema_version": "v1"},
            ),
        )

        self.assertTrue(result["ok"])
        self.assertEqual(result["data"]["items"], [])
        self.assertNotIn("search_web", ctx.run_state.failed_count_by_name)

    async def test_non_mcp_plain_dict_behavior_is_unchanged(self):
        harness = SystemHarness(make_policy(tool_limit=5, failure_limit=2))
        ctx = make_context(harness)

        result = await harness.invoke(
            run_context=ctx,
            agent_key="technical_agent",
            tool_name="search_web",
            arguments={"query": "business-error"},
            action=lambda: {"ok": False, "error": "business not found"},
        )

        self.assertEqual(result, {"ok": False, "error": "business not found"})
        self.assertNotIn("search_web", ctx.run_state.failed_count_by_name)


if __name__ == "__main__":
    unittest.main()

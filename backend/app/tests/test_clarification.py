import asyncio
import json
import unittest

from app.infrastructure.tools.local.knowledge_base import (
    is_vague_technical_query,
    query_knowledge_impl,
)
from app.infrastructure.tools.local.service_station import (
    map_navigation_tool_impl,
    query_nearest_repair_shops_by_coords_impl,
    resolve_user_location_from_text_impl,
)
from app.schemas.clarification import (
    ClarificationResult,
    is_clarification_payload,
    make_clarification_result,
)
from app.services.agent_service import _extract_clarification_payload
from app.utils.response_util import ResponseFactory


class ClarificationTests(unittest.TestCase):
    def test_clarification_result_serialization(self):
        result = ClarificationResult(
            clarification_type="missing_location",
            missing_fields=["city_or_address"],
            clarification_question="请提供城市或地址。",
            source="test",
            original_query="附近服务站",
            suggested_examples=["北京市海淀区中关村"],
        ).model_dump(mode="json")

        self.assertFalse(result["ok"])
        self.assertTrue(result["need_clarification"])
        self.assertEqual(result["missing_fields"], ["city_or_address"])
        self.assertEqual(result["clarification_question"], "请提供城市或地址。")

    def test_make_clarification_result_and_detection(self):
        payload = make_clarification_result(
            clarification_type="missing_device_info",
            missing_fields=["device_model", "os_version"],
            clarification_question="请补充设备型号和系统版本。",
            source="query_knowledge",
            original_query="黑屏怎么办",
        )

        self.assertTrue(is_clarification_payload(payload))
        self.assertTrue(payload["need_clarification"])
        self.assertEqual(payload["missing_fields"], ["device_model", "os_version"])
        self.assertFalse(is_clarification_payload({"ok": False, "error": "failed"}))
        self.assertFalse(is_clarification_payload("not-json"))

    def test_response_factory_build_clarification_is_sanitized(self):
        packet = ResponseFactory.build_clarification({
            "need_clarification": True,
            "clarification_type": "missing_location",
            "missing_fields": ["city_or_address"],
            "clarification_question": "请提供城市或地址。",
            "source": "resolve_user_location_from_text",
            "original_query": "附近服务站",
            "suggested_examples": ["北京市海淀区中关村"],
            "api_key": "secret-key",
            "raw_response": {"password": "secret-password"},
        })
        dumped = packet.model_dump(mode="json")
        content = dumped["content"]

        self.assertEqual(content["contentType"], "sagegpt/clarification")
        self.assertEqual(content["kind"], "CLARIFICATION")
        self.assertEqual(content["text"], "请提供城市或地址。")
        serialized = json.dumps(dumped, ensure_ascii=False)
        self.assertNotIn("secret-key", serialized)
        self.assertNotIn("secret-password", serialized)
        self.assertNotIn("raw_response", serialized)

    def test_agent_service_extracts_pure_json_clarification(self):
        payload = make_clarification_result(
            clarification_type="missing_destination",
            missing_fields=["destination"],
            clarification_question="请提供目的地。",
            source="geocode_destination",
        )
        self.assertEqual(_extract_clarification_payload(payload), payload)
        self.assertEqual(_extract_clarification_payload(json.dumps(payload, ensure_ascii=False)), payload)
        self.assertIsNone(_extract_clarification_payload("请提供目的地。"))


class ClarificationToolTests(unittest.IsolatedAsyncioTestCase):
    async def test_service_station_missing_location_returns_clarification(self):
        result = await resolve_user_location_from_text_impl("帮我查附近服务站")

        self.assertTrue(is_clarification_payload(result))
        self.assertEqual(result["clarification_type"], "missing_location")
        self.assertIn("city_or_address", result["missing_fields"])

    async def test_map_navigation_missing_destination_returns_clarification(self):
        result = await map_navigation_tool_impl(origin="北京市海淀区中关村", destination="")

        self.assertTrue(is_clarification_payload(result))
        self.assertEqual(result["clarification_type"], "missing_destination")
        self.assertIn("destination", result["missing_fields"])

    async def test_invalid_repair_shop_coords_returns_clarification(self):
        result = json.loads(query_nearest_repair_shops_by_coords_impl(999, 999))

        self.assertTrue(is_clarification_payload(result))
        self.assertEqual(result["clarification_type"], "missing_location")

    async def test_vague_technical_query_returns_clarification(self):
        self.assertTrue(is_vague_technical_query("黑屏怎么办"))
        self.assertFalse(is_vague_technical_query("ThinkPad T14，Windows 11，开机黑屏但电源灯亮"))

        result = await query_knowledge_impl("黑屏怎么办")
        self.assertTrue(is_clarification_payload(result))
        self.assertEqual(result["clarification_type"], "missing_device_info")
        self.assertIn("device_model", result["missing_fields"])


if __name__ == "__main__":
    unittest.main()

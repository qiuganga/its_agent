import sys
import unittest
from pathlib import Path


KNOWLEDGE_ROOT = Path(__file__).resolve().parents[1]
if str(KNOWLEDGE_ROOT) not in sys.path:
    sys.path.insert(0, str(KNOWLEDGE_ROOT))

from services.query_normalization_service import QueryNormalizationService


class QueryNormalizationTests(unittest.TestCase):
    def setUp(self):
        self.service = QueryNormalizationService()

    def assert_normalized(self, question, expected):
        normalized = self.service.normalize(question)
        self.assertEqual(normalized, expected)
        self.assertEqual(self.service.normalize(normalized), normalized)

    def test_bluetooth_device_long_rule_has_priority(self):
        self.assert_normalized("搜不到蓝牙设备怎么办", "蓝牙设备无法被发现怎么办")
        self.assertNotIn("无法被发现设备", self.service.normalize("搜不到蓝牙设备怎么办"))

    def test_bluetooth_short_rule_still_normalizes(self):
        self.assert_normalized("搜不到蓝牙怎么办", "蓝牙设备无法被发现怎么办")

    def test_system_stuck_without_duplicate_semantics(self):
        self.assert_normalized("系统卡死没有响应怎么办", "系统无响应怎么办")
        self.assert_normalized("电脑卡死没有响应怎么办", "系统无响应怎么办")

    def test_black_screen_with_fan_deduplicates_black_screen_semantics(self):
        self.assert_normalized("屏幕不亮但风扇会转，电脑黑屏怎么处理", "黑屏但风扇会转怎么处理")

    def test_bluetooth_connection_device_long_rule_has_priority(self):
        self.assert_normalized("连不上蓝牙设备怎么添加", "蓝牙连接失败怎么添加")
        self.assertNotIn("失败设备", self.service.normalize("连不上蓝牙设备怎么添加"))

    def test_multiple_rules_can_apply_once(self):
        normalized = self.service.normalize("开不了机，屏幕不亮怎么办")

        self.assertIn("无法开机", normalized)
        self.assertIn("黑屏", normalized)
        self.assertEqual(self.service.normalize(normalized), normalized)

    def test_question_without_rule_is_stable(self):
        self.assert_normalized("Excel 文件菜单灰色不可用怎么办", "Excel 文件菜单灰色不可用怎么办")

    def test_whitespace_and_commas_are_normalized(self):
        self.assert_normalized("  开不了机，   \n\t屏幕不亮  ", "无法开机，黑屏")

    def test_error_codes_models_and_hyphenated_terms_are_preserved(self):
        question = "ThinkPad X1 Wi-Fi 蓝屏报错 0x0000007B 怎么办"

        normalized = self.service.normalize(question)

        self.assertIn("ThinkPad X1", normalized)
        self.assertIn("Wi-Fi", normalized)
        self.assertIn("0x0000007B", normalized)
        self.assertEqual(self.service.normalize(normalized), normalized)

    def test_does_not_invent_brand_model_or_system_version(self):
        normalized = self.service.normalize("屏幕不亮怎么办")

        self.assertIn("黑屏", normalized)
        for unexpected in ["ThinkPad", "Windows", "Lenovo", "K900", "Windows 11"]:
            self.assertNotIn(unexpected, normalized)

    def test_black_screen_cleanup_is_not_over_aggressive(self):
        question = "电脑黑屏但外接显示器正常怎么办"

        self.assert_normalized(question, question)


if __name__ == "__main__":
    unittest.main()

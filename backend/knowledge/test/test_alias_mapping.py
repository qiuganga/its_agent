import os
import sys
import unittest


KNOWLEDGE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if KNOWLEDGE_ROOT not in sys.path:
    sys.path.insert(0, KNOWLEDGE_ROOT)


from services.query_alias_mapping_service import AliasMappingService
from services.query_normalization_service import QueryNormalizationService


class AliasMappingTests(unittest.TestCase):
    def setUp(self):
        self.service = AliasMappingService()

    def assertMapsToContains(self, query, expected):
        mapped = self.service.map_alias(query)
        self.assertIn(expected, mapped)
        self.assertEqual(self.service.map_alias(mapped), mapped)

    def test_wifi_aliases(self):
        self.assertMapsToContains("wifi 连不上", "Wi-Fi")
        self.assertMapsToContains("WiFi 不稳定", "Wi-Fi")

    def test_office365_and_office_aliases(self):
        self.assertMapsToContains("Office365 激活失败", "Microsoft Office")
        self.assertMapsToContains("office 打不开", "Microsoft Office")

    def test_bluetooth_alias(self):
        self.assertMapsToContains("Bluetooth 搜不到设备", "蓝牙")

    def test_think_pad_alias_uses_longest_match(self):
        mapped = self.service.map_alias("Think Pad 开机黑屏")

        self.assertIn("ThinkPad", mapped)
        self.assertNotIn("Think Pad", mapped)
        self.assertEqual(self.service.map_alias(mapped), mapped)

    def test_excel_word_aliases(self):
        self.assertMapsToContains("EXCEL 文件打不开", "Excel")
        self.assertMapsToContains("Word 无法启动", "Word")

    def test_confirmed_candidate_aliases(self):
        self.assertMapsToContains("win7 安装失败", "Windows 7")
        self.assertMapsToContains("Win7 蓝屏", "Windows 7")
        self.assertMapsToContains("xp 开机慢", "Windows XP")
        self.assertMapsToContains("XP 无法启动", "Windows XP")
        self.assertMapsToContains("windows xp 无法联网", "Windows XP")
        self.assertMapsToContains("Printer 不能打印", "打印机")
        self.assertMapsToContains("printer 驱动安装失败", "打印机")

    def test_confirmed_candidate_aliases_are_idempotent(self):
        query = "win7 和 xp 的 printer 都不能用"
        mapped_once = self.service.map_alias(query)
        mapped_twice = self.service.map_alias(mapped_once)

        self.assertEqual(mapped_once, mapped_twice)
        self.assertEqual(mapped_once.count("Windows 7"), 1)
        self.assertEqual(mapped_once.count("Windows XP"), 1)
        self.assertEqual(mapped_once.count("打印机"), 1)

    def test_medium_risk_candidates_are_not_enabled_unless_configured(self):
        if "PowerPoint" not in self.service.alias_map:
            self.assertEqual(self.service.map_alias("PPT 打不开"), "PPT 打不开")
            self.assertEqual(self.service.map_alias("PowerPoint 打不开"), "PowerPoint 打不开")

        if "任务栏输入法图标" not in self.service.alias_map:
            self.assertEqual(self.service.map_alias("输入法图标不见了"), "输入法图标不见了")

    def test_repeated_mapping_is_idempotent(self):
        mapped_once = self.service.map_alias("office365 和 wifi 都不能用")
        mapped_twice = self.service.map_alias(mapped_once)

        self.assertEqual(mapped_once, mapped_twice)
        self.assertEqual(mapped_once.count("Microsoft Office"), 1)
        self.assertEqual(mapped_once.count("Wi-Fi"), 1)

    def test_query_normalization_applies_alias_after_rules(self):
        service = QueryNormalizationService(alias_mapping_service=self.service)

        normalized = service.normalize("wifi 连不上怎么办")

        self.assertIn("Wi-Fi", normalized)
        self.assertEqual(service.last_debug_info["original_query"], "wifi 连不上怎么办")
        self.assertIn("alias_query", service.last_debug_info)
        self.assertTrue(service.last_debug_info["alias_applied"])

    def test_alias_not_triggered_is_reported(self):
        service = QueryNormalizationService(alias_mapping_service=self.service)

        normalized = service.normalize("键盘输入延迟怎么办")

        self.assertEqual(normalized, "键盘输入延迟怎么办")
        self.assertFalse(service.last_debug_info["alias_applied"])


if __name__ == "__main__":
    unittest.main()

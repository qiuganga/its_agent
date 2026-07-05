import os
import sys
import unittest
from dataclasses import dataclass, field


KNOWLEDGE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if KNOWLEDGE_ROOT not in sys.path:
    sys.path.insert(0, KNOWLEDGE_ROOT)

from services.anchor_evidence_service import (
    ANCHOR_EVIDENCE_MISSING,
    FULL_ANCHOR_EVIDENCE,
    NO_ANCHOR_EVIDENCE,
    NO_STRONG_ANCHOR,
    evaluate_document_evidence,
    evaluate_retrieval_evidence,
    extract_strong_anchors,
)


@dataclass
class FakeDocument:
    page_content: str
    metadata: dict = field(default_factory=dict)


class AnchorEvidenceTests(unittest.TestCase):
    def test_error_code_anchor_extracts_and_matches_exactly(self):
        anchors = extract_strong_anchors("电脑蓝屏报错 0x0000007B 怎么办")
        self.assertIn("0x0000007B", [anchor.term for anchor in anchors])

        doc = FakeDocument("", {"title": "台式和一体机蓝屏报错代码：0x0000007B"})
        evidence = evaluate_document_evidence(anchors, doc)
        self.assertEqual(evidence.anchor_evidence_status, FULL_ANCHOR_EVIDENCE)
        self.assertIn("0x0000007B", evidence.matched_locations["title"])

    def test_common_product_and_technology_terms_are_preserved(self):
        anchors = extract_strong_anchors("ThinkPad X1 安装 Windows 后如何进入 BIOS 使用 Outlook Word Excel Wi-Fi")
        terms = {anchor.term for anchor in anchors}
        for expected in ["ThinkPad X1", "Windows", "BIOS", "Outlook", "Word", "Excel", "Wi-Fi"]:
            self.assertIn(expected, terms)

    def test_wifi_equivalence_does_not_match_wireless_keyboard_mouse(self):
        anchors = extract_strong_anchors("无线网络连不上怎么办")
        good = evaluate_document_evidence(anchors, FakeDocument("WiFi 设置方法", {"title": "无线网络连接失败"}))
        bad = evaluate_document_evidence(anchors, FakeDocument("", {"title": "无线键鼠套装安装注意事项"}))

        self.assertEqual(good.anchor_evidence_status, FULL_ANCHOR_EVIDENCE)
        self.assertEqual(bad.anchor_evidence_status, NO_ANCHOR_EVIDENCE)

    def test_generic_terms_are_not_independent_strong_anchors(self):
        anchors = extract_strong_anchors("电脑系统问题怎么办，无法开机黑屏，文件图片异常怎么处理")
        terms = {anchor.term for anchor in anchors}
        for generic in ["电脑", "系统", "问题", "怎么办", "处理", "异常", "无法", "开机", "黑屏", "文件", "图片"]:
            self.assertNotIn(generic, terms)

    def test_specific_chinese_phrases_are_strong_anchors(self):
        anchors = extract_strong_anchors("手机屏幕进水后如何更换折叠屏铰链，量子网络和冰箱冷冻室也有问题")
        terms = {anchor.term for anchor in anchors}
        self.assertIn("折叠屏铰链", terms)
        self.assertIn("量子网络", terms)
        self.assertIn("冰箱冷冻室", terms)

    def test_evidence_ignores_url_path_source_id_and_hash_like_metadata(self):
        anchors = extract_strong_anchors("量子网络怎么连接")
        doc = FakeDocument(
            "普通正文内容",
            {
                "title": "普通标题",
                "keywords": "",
                "source_id": "faq/量子网络.md",
                "path": "D:/kb/量子网络.md",
                "collection_experiment": "its-knowledge-clean-v1",
            },
        )
        evidence = evaluate_document_evidence(anchors, doc)
        self.assertEqual(evidence.anchor_evidence_status, NO_ANCHOR_EVIDENCE)

    def test_no_anchor_question_does_not_trigger_block(self):
        decision = evaluate_retrieval_evidence("电脑黑屏怎么办", [FakeDocument("任何内容", {"title": "无关标题"})])
        self.assertTrue(decision.ok)
        self.assertIsNone(decision.reason_code)
        self.assertEqual(decision.final_top_k_statuses, [])

    def test_missing_anchor_evidence_blocks(self):
        decision = evaluate_retrieval_evidence("折叠屏铰链怎么更换", [FakeDocument("普通内容", {"title": "普通标题"})])
        self.assertFalse(decision.ok)
        self.assertEqual(decision.reason_code, ANCHOR_EVIDENCE_MISSING)

    def test_any_final_document_with_anchor_evidence_allows(self):
        docs = [
            FakeDocument("普通内容", {"title": "普通标题"}),
            FakeDocument("蓝牙设备添加步骤", {"title": "如何添加启用蓝牙的设备"}),
        ]
        decision = evaluate_retrieval_evidence("搜不到蓝牙设备怎么办", docs)
        self.assertTrue(decision.ok)
        self.assertIn("蓝牙设备", decision.matched_anchor_terms)

    def test_no_strong_anchor_status_for_document_evidence(self):
        evidence = evaluate_document_evidence([], FakeDocument("内容", {"title": "标题"}))
        self.assertEqual(evidence.anchor_evidence_status, NO_STRONG_ANCHOR)
        self.assertIsNone(evidence.anchor_coverage_ratio)


if __name__ == "__main__":
    unittest.main()

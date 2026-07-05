import os
import sys
import unittest
from dataclasses import dataclass, field


KNOWLEDGE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if KNOWLEDGE_ROOT not in sys.path:
    sys.path.insert(0, KNOWLEDGE_ROOT)

from services.anchor_evidence_service import (
    ANCHOR_EVIDENCE_MISSING,
    ANCHOR_TYPE_HARD,
    ANCHOR_TYPE_NEGATIVE,
    ANCHOR_TYPE_SOFT,
    HARD_EVIDENCE_EXISTS_OUTSIDE_TOPK,
    apply_anchor_adjustment,
    evaluate_hard_soft_negative_gate,
    extract_anchors,
)
from services.retrieval_service import RetrievalService


@dataclass
class FakeDocument:
    page_content: str
    metadata: dict = field(default_factory=dict)


class AnchorEvidenceV2Tests(unittest.TestCase):
    def terms_by_type(self, question: str, anchor_type: str) -> set[str]:
        return {anchor.term for anchor in extract_anchors(question) if anchor.anchor_type == anchor_type}

    def test_error_codes_are_hard_anchors(self):
        self.assertIn("0x0000007B", self.terms_by_type("blue screen 0x0000007B", ANCHOR_TYPE_HARD))
        self.assertIn("E0001", self.terms_by_type("error E0001 while booting", ANCHOR_TYPE_HARD))
        self.assertIn("404", self.terms_by_type("browser shows 404", ANCHOR_TYPE_HARD))

    def test_models_are_hard_anchors(self):
        terms = self.terms_by_type("ThinkPad X1 and Lenovo G485 fail to boot", ANCHOR_TYPE_HARD)
        self.assertIn("ThinkPad X1", terms)
        self.assertIn("Lenovo G485", terms)

    def test_configured_compound_terms_are_hard_anchors(self):
        terms = self.terms_by_type("folding screen hinge and quantum network freezer cold room", ANCHOR_TYPE_HARD)
        self.assertIn("折叠屏铰链", terms)
        self.assertIn("量子网络", terms)
        self.assertIn("冰箱冷冻室", terms)

    def test_common_products_are_soft_not_hard(self):
        anchors = extract_anchors("Windows Word Excel Bluetooth Wi-Fi wireless network")
        soft = {anchor.term for anchor in anchors if anchor.anchor_type == ANCHOR_TYPE_SOFT}
        hard = {anchor.term for anchor in anchors if anchor.anchor_type == ANCHOR_TYPE_HARD}
        for term in {"Windows", "Word", "Excel", "Bluetooth", "Wi-Fi"}:
            self.assertIn(term, soft)
            self.assertNotIn(term, hard)

    def test_generic_terms_are_not_hard(self):
        hard = self.terms_by_type("computer system network black screen device file", ANCHOR_TYPE_HARD)
        self.assertFalse(hard & {"computer", "system", "network", "black screen", "device", "file"})

    def test_negative_wifi_is_not_positive_wifi(self):
        anchors = extract_anchors("Wireless keyboard and mouse suddenly fail, not Wi-Fi")
        negative = {anchor.term for anchor in anchors if anchor.anchor_type == ANCHOR_TYPE_NEGATIVE}
        soft = {anchor.term for anchor in anchors if anchor.anchor_type == ANCHOR_TYPE_SOFT}
        hard = {anchor.term for anchor in anchors if anchor.anchor_type == ANCHOR_TYPE_HARD}
        self.assertIn("Wi-Fi", negative)
        self.assertNotIn("Wi-Fi", soft)
        self.assertIn("无线键鼠", hard)

    def test_unable_to_connect_wifi_is_not_negative(self):
        negative = self.terms_by_type("unable to connect Wi-Fi", ANCHOR_TYPE_NEGATIVE)
        self.assertNotIn("Wi-Fi", negative)

    def test_alias_mapping_matches_chinese_document(self):
        anchors = extract_anchors("display brightness is too low")
        doc = FakeDocument("", {"title": "如何设置显示屏幕的亮度"})
        adjusted = apply_anchor_adjustment("display brightness is too low", [doc])
        evidence = adjusted[0][1]
        self.assertIn("display brightness", evidence.matched_soft_anchor_terms)

    def test_soft_anchor_missing_does_not_hard_block(self):
        decision = evaluate_hard_soft_negative_gate(
            "Word inserted picture blank box",
            [FakeDocument("ordinary content", {"title": "unrelated"})],
            [FakeDocument("ordinary content", {"title": "unrelated"})],
        )
        self.assertTrue(decision.ok)
        self.assertIsNone(decision.reason_code)

    def test_hard_anchor_in_window_not_top2_does_not_block(self):
        decision = evaluate_hard_soft_negative_gate(
            "blue screen 0x0000007B",
            [FakeDocument("ordinary content", {"title": "generic boot issue"})],
            [
                FakeDocument("ordinary content", {"title": "generic boot issue"}),
                FakeDocument("ordinary content", {"title": "台式和一体机蓝屏报错代码：0x0000007B"}),
            ],
        )
        self.assertTrue(decision.ok)
        self.assertEqual(decision.reason_code, HARD_EVIDENCE_EXISTS_OUTSIDE_TOPK)

    def test_hard_anchor_missing_in_window_blocks_experimentally(self):
        decision = evaluate_hard_soft_negative_gate(
            "blue screen 0x0000007B",
            [FakeDocument("ordinary content", {"title": "generic boot issue"})],
            [FakeDocument("ordinary content", {"title": "generic boot issue"})],
        )
        self.assertFalse(decision.ok)
        self.assertEqual(decision.reason_code, ANCHOR_EVIDENCE_MISSING)

    def test_default_retrieval_service_is_off(self):
        self.assertEqual(RetrievalService(chroma_vector=object(), spliter=object()).anchor_evidence_mode, "off")

    def test_legacy_mode_is_still_available(self):
        service = RetrievalService(chroma_vector=object(), spliter=object(), anchor_evidence_mode="legacy")
        self.assertEqual(service.anchor_evidence_mode, "legacy")

    def test_hard_soft_negative_mode_does_not_mutate_default(self):
        service = RetrievalService(chroma_vector=object(), spliter=object(), anchor_evidence_mode="hard-soft-negative")
        self.assertEqual(service.anchor_evidence_mode, "hard-soft-negative")
        self.assertEqual(RetrievalService(chroma_vector=object(), spliter=object()).anchor_evidence_mode, "off")

    def test_business_anchor_logic_does_not_reference_eval_labels(self):
        service_path = os.path.join(KNOWLEDGE_ROOT, "services", "anchor_evidence_service.py")
        with open(service_path, "r", encoding="utf-8") as handle:
            source = handle.read()
        for forbidden in ["case_id", "expected_answerability", "expected_title_contains", "expected_source_ids"]:
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()

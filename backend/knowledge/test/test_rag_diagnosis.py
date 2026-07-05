import unittest
import sys
from pathlib import Path
from types import SimpleNamespace

KNOWLEDGE_ROOT = Path(__file__).resolve().parents[1]
if str(KNOWLEDGE_ROOT) not in sys.path:
    sys.path.insert(0, str(KNOWLEDGE_ROOT))

from scripts.diagnose_rag_retrieval import (
    anchor_evidence_for_text,
    classify_case,
    document_to_record,
    extract_anchor_terms,
    summarize_content,
)


class TestRagDiagnosis(unittest.TestCase):
    def test_extracts_error_code_anchor(self):
        anchors = extract_anchor_terms("电脑蓝屏报错 0x0000007B 怎么办")

        self.assertIn("0x0000007B", anchors)

    def test_extracts_model_and_english_product_anchors(self):
        anchors = extract_anchor_terms("ThinkPad X1 安装 Windows 后如何进入 BIOS")

        self.assertIn("ThinkPad X1", anchors)
        self.assertIn("Windows", anchors)
        self.assertIn("BIOS", anchors)

    def test_generic_terms_are_not_anchors(self):
        anchors = extract_anchor_terms("电脑系统问题怎么办")

        self.assertNotIn("电脑", anchors)
        self.assertNotIn("系统", anchors)
        self.assertNotIn("怎么办", anchors)

    def test_full_anchor_evidence(self):
        evidence = anchor_evidence_for_text(["Windows", "BIOS"], "Windows 启动前进入 BIOS 设置")

        self.assertEqual(evidence["anchor_evidence_status"], "FULL_ANCHOR_EVIDENCE")
        self.assertEqual(evidence["anchor_coverage_ratio"], 1.0)

    def test_no_anchor_evidence(self):
        evidence = anchor_evidence_for_text(["Windows", "BIOS"], "这是一个无关的网络说明")

        self.assertEqual(evidence["anchor_evidence_status"], "NO_ANCHOR_EVIDENCE")
        self.assertEqual(evidence["matched_anchor_terms"], [])

    def test_no_strong_anchor(self):
        evidence = anchor_evidence_for_text([], "任意内容")

        self.assertEqual(evidence["anchor_evidence_status"], "NO_STRONG_ANCHOR")
        self.assertIsNone(evidence["anchor_coverage_ratio"])

    def test_missing_metadata_fields_do_not_break(self):
        document = SimpleNamespace(page_content="Windows BIOS 测试内容" * 20, metadata={})

        record = document_to_record(
            document,
            fallback_rank=1,
            anchor_terms=["Windows", "BIOS"],
            expected_title_contains=["BIOS"],
            show_content=False,
        )

        self.assertEqual(record["rank"], 1)
        self.assertIsNone(record["source_id"])
        self.assertEqual(record["anchor_evidence_status"], "FULL_ANCHOR_EVIDENCE")

    def test_summary_limited_by_default_and_full_when_requested(self):
        content = "A" * 400

        limited = summarize_content(content, show_content=False)
        full = summarize_content(content, show_content=True)

        self.assertLessEqual(len(limited), 303)
        self.assertTrue(limited.endswith("..."))
        self.assertEqual(full, content)

    def test_insufficient_evidence_requires_manual_review(self):
        flags = classify_case(
            case={
                "expected_no_answer": False,
                "expected_title_contains": ["蓝屏"],
            },
            stage_records=[
                {
                    "vector_candidates": [{"expected_title_hit": False}],
                    "title_candidates": [{"expected_title_hit": False}],
                    "reranked_topk": [{"expected_title_hit": False}],
                }
            ],
            final_records=[],
            pre_threshold_records=[],
            rejected_by_low_confidence=False,
        )

        self.assertTrue(flags["candidate_recall_problem"])
        self.assertTrue(flags["requires_manual_review"])


if __name__ == "__main__":
    unittest.main()

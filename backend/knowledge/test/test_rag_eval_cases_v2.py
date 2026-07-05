import json
import os
import sys
import tempfile
import unittest
from pathlib import Path


KNOWLEDGE_ROOT = Path(__file__).resolve().parents[1]
if str(KNOWLEDGE_ROOT) not in sys.path:
    sys.path.insert(0, str(KNOWLEDGE_ROOT))

from scripts.audit_rag_eval_cases import build_audit
from scripts.evaluate_rag_retrieval import build_group_metrics, load_cases


CASES_V2 = KNOWLEDGE_ROOT / "testdata" / "rag_eval_cases_v2.json"


class RagEvalCasesV2Tests(unittest.TestCase):
    def test_v2_case_schema_and_unique_ids(self):
        cases = json.loads(CASES_V2.read_text(encoding="utf-8"))
        ids = [case["id"] for case in cases]
        self.assertGreaterEqual(len(cases), 60)
        self.assertEqual(len(ids), len(set(ids)))

        for case in cases:
            self.assertIn("id", case)
            self.assertIn("question", case)
            self.assertIn("category", case)
            if int(case["id"].split("_")[1]) >= 25:
                self.assertIn(case["category"], {
                    "anchor_answerable",
                    "anchor_unanswerable",
                    "generic_answerable",
                    "generic_unanswerable",
                    "confusing",
                })
                self.assertIn(case["expected_answerability"], {"answerable", "unanswerable"})
                if case["expected_answerability"] == "answerable":
                    self.assertTrue(case.get("expected_source_ids") or case.get("expected_title_contains"))
                else:
                    self.assertFalse(case.get("expected_source_ids"))

    def test_audit_identifies_missing_source_id(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            crawl = root / "crawl"
            crawl.mkdir()
            (crawl / "known.md").write_text("# Known\ncontent", encoding="utf-8")
            cases = root / "cases.json"
            cases.write_text(json.dumps([
                {
                    "id": "case_x",
                    "question": "known question",
                    "category": "anchor_answerable",
                    "expected_answerability": "answerable",
                    "expected_title_contains": [],
                    "expected_source_ids": ["missing.md"],
                    "expected_anchor_terms": ["BIOS"],
                    "gold_evidence_note": "test",
                    "review_status": "verified",
                }
            ]), encoding="utf-8")

            audit = build_audit(cases, crawl)

        self.assertEqual(audit["summary"]["invalid_cases"], 1)
        self.assertIn("missing.md", audit["records"][0]["source_id_missing"])

    def test_audit_identifies_duplicate_question(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            crawl = root / "crawl"
            crawl.mkdir()
            (crawl / "known.md").write_text("# Known\ncontent", encoding="utf-8")
            records = []
            for idx in range(2):
                records.append({
                    "id": f"case_{idx}",
                    "question": "same question",
                    "category": "generic_unanswerable",
                    "expected_answerability": "unanswerable",
                    "expected_title_contains": [],
                    "expected_source_ids": [],
                    "expected_anchor_terms": [],
                    "gold_evidence_note": "test",
                    "review_status": "verified",
                })
            cases = root / "cases.json"
            cases.write_text(json.dumps(records), encoding="utf-8")

            audit = build_audit(cases, crawl)

        self.assertEqual(audit["summary"]["duplicate_cases"], 2)

    def test_audit_is_local_only_in_source(self):
        source = (KNOWLEDGE_ROOT / "scripts" / "audit_rag_eval_cases.py").read_text(encoding="utf-8")
        self.assertNotIn("OpenAIEmbeddings", source)
        self.assertNotIn("import chromadb", source)
        self.assertNotIn("langchain_chroma", source)
        self.assertNotIn("requests.", source)
        self.assertNotIn("httpx.", source)
        self.assertNotIn("urllib.", source)

    def test_evaluate_load_cases_accepts_override_without_changing_default(self):
        default_cases = load_cases()
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "cases.json"
            path.write_text(json.dumps([{"id": "case_tmp", "question": "q", "category": "generic_unanswerable"}]), encoding="utf-8")
            custom_cases = load_cases(path)

        self.assertNotEqual(default_cases, custom_cases)
        self.assertEqual(custom_cases[0]["id"], "case_tmp")

    def test_group_metrics_are_calculated_for_abcde_groups(self):
        results = [
            {
                "case_id": "a",
                "case_group": "A_anchor_answerable",
                "expected_answerability": "answerable",
                "top1_title_weak_hit": True,
                "top2_title_weak_hit": True,
                "rejected_by_low_confidence": False,
                "rejected_by_anchor_evidence": False,
                "anchor_decision": {},
            },
            {
                "case_id": "b",
                "case_group": "B_anchor_unanswerable",
                "expected_answerability": "unanswerable",
                "top1_title_weak_hit": False,
                "top2_title_weak_hit": False,
                "rejected_by_low_confidence": False,
                "rejected_by_anchor_evidence": True,
                "anchor_decision": {"reason_code": "ANCHOR_EVIDENCE_MISSING"},
            },
        ]

        metrics = build_group_metrics(results)

        self.assertEqual(metrics["A_anchor_answerable"]["expected_answer_false_rejected_count"], 0)
        self.assertEqual(metrics["B_anchor_unanswerable"]["expected_no_answer_correctly_rejected_count"], 1)
        self.assertEqual(metrics["B_anchor_unanswerable"]["anchor_evidence_missing_count"], 1)


if __name__ == "__main__":
    unittest.main()

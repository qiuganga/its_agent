import json
import tempfile
import unittest
from pathlib import Path

from backend.knowledge.scripts.compare_alias_mapping_reports import build_comparison


def _write_json(path: Path, payload) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


class AliasReportComparisonTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.baseline_path = self.root / "baseline.json"
        self.alias_path = self.root / "alias.json"
        self.baseline = self._report()
        self.alias = self._report(alias=True)
        _write_json(self.baseline_path, self.baseline)
        _write_json(self.alias_path, self.alias)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _settings(self) -> dict:
        return {
            "collection_name": "its-knowledge-clean-v1",
            "RAG_BM25_MODE": "experimental",
            "RAG_ANCHOR_EVIDENCE_MODE": "hard-soft-negative",
            "RAG_RERANKER_MODE": "experimental",
            "RAG_RERANKER_PROVIDER": "siliconflow",
            "RAG_RERANKER_MODEL": "Qwen/Qwen3-Reranker-8B",
            "RAG_MIN_RERANK_SCORE": 0.35,
            "RAG_FINAL_TOP_K": 2,
        }

    def _summary(self) -> dict:
        return {
            "total_cases": 82,
            "bm25_mode": "experimental",
            "anchor_evidence_mode": "hard-soft-negative",
            "reranker_mode": "experimental",
            "reranker_provider": "siliconflow",
            "top1_title_weak_hit_count": 1,
            "top2_title_weak_hit_count": 1,
            "expected_answer_false_rejected": 1,
            "expected_no_answer_anchor_rejected": 0,
            "expected_no_answer_not_rejected": 0,
            "accepted_count": 81,
            "total_rejected_count": 1,
            "reranker_latency_avg_ms": 10,
            "reranker_latency_p95_ms": 20,
            "source_id_missing_before_rerank_total": 0,
        }

    def _doc(self, title: str) -> dict:
        return {
            "title": title,
            "source_id": f"{title}.md",
            "retrieval_route": "bm25",
            "retrieval_routes": ["bm25"],
            "reranker_score": 0.7,
            "final_rerank_score": 0.7,
            "mmr_score": 0.7,
            "anchor_evidence_status": "NO_STRONG_ANCHOR",
        }

    def _result(self, case_id: str, question: str, normalized: str, title: str, hit: bool = True) -> dict:
        return {
            "case_id": case_id,
            "expected_answerability": "answerable",
            "original_question": question,
            "normalized_question": normalized,
            "query_variants": [question, normalized],
            "rejected_by_low_confidence": False,
            "rejected_by_anchor_evidence": False,
            "top1_title_weak_hit": hit,
            "top2_title_weak_hit": hit,
            "final_documents": [self._doc(title)],
            "documents_before_threshold": [],
        }

    def _report(self, alias: bool = False) -> dict:
        summary = self._summary()
        results = []
        for index in range(82):
            case_id = f"case_{index + 1:03d}"
            question = "win7 蓝屏怎么办" if index == 0 else f"普通问题 {index}"
            normalized = "Windows 7 蓝屏怎么办" if alias and index == 0 else question
            title = "Windows 7 蓝屏修复" if alias and index == 0 else "旧标题"
            hit = bool(alias and index == 0) if index == 0 else True
            results.append(self._result(case_id, question, normalized, title, hit=hit))
        if alias:
            summary["top1_title_weak_hit_count"] = 2
            summary["top2_title_weak_hit_count"] = 2
            summary["expected_answer_false_rejected"] = 0
        return {
            "status": "success",
            "cases_file": "backend\\knowledge\\testdata\\rag_eval_cases_v2.json",
            "settings": self._settings(),
            "summary": summary,
            "results": results,
        }

    def test_validates_total_cases(self):
        self.alias["summary"]["total_cases"] = 81
        _write_json(self.alias_path, self.alias)
        with self.assertRaisesRegex(ValueError, "total_cases"):
            build_comparison(self.baseline_path, self.alias_path)

    def test_validates_cases_file(self):
        self.alias["cases_file"] = "other.json"
        _write_json(self.alias_path, self.alias)
        with self.assertRaisesRegex(ValueError, "cases_file"):
            build_comparison(self.baseline_path, self.alias_path)

    def test_validates_collection_name(self):
        self.alias["settings"]["collection_name"] = "other"
        _write_json(self.alias_path, self.alias)
        with self.assertRaisesRegex(ValueError, "collection_name"):
            build_comparison(self.baseline_path, self.alias_path)

    def test_identifies_top2_changed(self):
        report = build_comparison(self.baseline_path, self.alias_path)
        self.assertEqual(1, report["metrics"]["top2_changed_count"])
        first = report["comparisons"][0]
        self.assertTrue(first["top2_changed"])

    def test_counts_alias_applied_cases(self):
        report = build_comparison(self.baseline_path, self.alias_path)
        self.assertEqual(1, report["metrics"]["alias_applied_case_count"])
        self.assertEqual(1, report["metrics"]["new_alias_hit_case_count"])

    def test_does_not_read_eval_labels_to_change_business_results(self):
        report = build_comparison(self.baseline_path, self.alias_path)
        first = report["comparisons"][0]
        self.assertNotIn("expected_keywords", first)
        self.assertNotIn("expected_title_contains", first)

    def test_missing_file_fails_clearly(self):
        with self.assertRaises(FileNotFoundError):
            build_comparison(self.root / "missing.json", self.alias_path)


if __name__ == "__main__":
    unittest.main()

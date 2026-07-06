import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from backend.knowledge.scripts.mine_alias_candidates import mine_candidates, write_outputs


def _write_json(path: Path, payload) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


class AliasCandidateMiningTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.alias_file = self.root / "query_aliases.yaml"
        self.cases_file = self.root / "cases.json"
        self.reranker_file = self.root / "reranker.json"
        self.bm25_file = self.root / "bm25.json"
        self.threshold_file = self.root / "threshold.json"

        self.alias_file.write_text(
            "\n".join(
                [
                    "Wi-Fi:",
                    "  - wifi",
                    "  - WiFi",
                    "  - 无线网络",
                    "蓝牙:",
                    "  - Bluetooth",
                    "Microsoft Office:",
                    "  - Office365",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        _write_json(
            self.cases_file,
            [
                {
                    "id": "case_wifi",
                    "question": "wifi 连不上怎么办",
                    "expected_keywords": ["Wi-Fi"],
                    "expected_title_contains": ["无线网络"],
                    "category": "alias",
                },
                {
                    "id": "case_bt",
                    "question": "Bluetooth 设备搜不到",
                    "expected_keywords": ["蓝牙"],
                    "expected_title_contains": ["蓝牙"],
                    "category": "alias",
                },
                {
                    "id": "case_office",
                    "question": "Office365 打不开",
                    "expected_keywords": ["Microsoft Office"],
                    "expected_title_contains": ["Microsoft Office"],
                    "category": "alias",
                },
                {
                    "id": "case_generic",
                    "question": "系统文件有问题",
                    "expected_keywords": ["系统", "电脑", "文件"],
                    "expected_title_contains": ["系统"],
                    "category": "generic",
                },
            ],
        )
        _write_json(
            self.reranker_file,
            {
                "results": [
                    self._result(
                        "case_wifi",
                        "wifi 连不上怎么办",
                        "Wi-Fi 连不上怎么办",
                        "无线网络连接故障处理",
                        False,
                    ),
                    self._result(
                        "case_bt",
                        "Bluetooth 设备搜不到",
                        "Bluetooth 设备搜不到",
                        "蓝牙设备无法连接",
                        False,
                    ),
                    self._result(
                        "case_office",
                        "Office365 打不开",
                        "Office365 打不开",
                        "Microsoft Office 启动失败",
                        False,
                    ),
                    self._result(
                        "case_generic",
                        "系统文件有问题",
                        "系统文件有问题",
                        "电脑系统文件修复",
                        False,
                    ),
                ]
            },
        )
        _write_json(
            self.bm25_file,
            {
                "results": [
                    self._result("case_wifi", "wifi 连不上怎么办", "Wi-Fi 连不上怎么办", "无线网络连接故障处理", True),
                    self._result("case_bt", "Bluetooth 设备搜不到", "Bluetooth 设备搜不到", "蓝牙设备无法连接", True),
                    self._result("case_office", "Office365 打不开", "Office365 打不开", "Microsoft Office 启动失败", True),
                    self._result("case_generic", "系统文件有问题", "系统文件有问题", "电脑系统文件修复", True),
                ]
            },
        )
        _write_json(self.threshold_file, {"recommendation": {"recommended_threshold": 0.35}})

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _result(self, case_id: str, original: str, normalized: str, title: str, hit: bool) -> dict:
        return {
            "case_id": case_id,
            "expected_answerability": "answerable",
            "original_question": original,
            "normalized_question": normalized,
            "query_variants": [original, normalized],
            "rejected_by_low_confidence": False,
            "rejected_by_anchor_evidence": False,
            "final_topk_count": 1,
            "top2_title_weak_hit": hit,
            "ab_comparison": {"classification": "changed" if not hit else "neutral"},
            "final_documents": [
                {
                    "title": title,
                    "source_id": f"{case_id}.md",
                    "retrieval_route": "bm25",
                    "retrieval_routes": ["bm25"],
                    "matched_by_bm25_query": normalized,
                    "anchor_terms": [],
                }
            ],
            "documents_before_threshold": [],
        }

    def _mine(self) -> dict:
        return mine_candidates(
            alias_file=self.alias_file,
            cases_file=self.cases_file,
            reranker_report_file=self.reranker_file,
            bm25_report_file=self.bm25_file,
            threshold_analysis_file=self.threshold_file,
        )

    def test_existing_alias_not_duplicated_as_new_suggestion(self):
        report = self._mine()
        wifi = next(item for item in report["suggestions"] if item["canonical"] == "Wi-Fi")
        self.assertEqual("existing_alias", wifi["status"])
        self.assertNotIn("wifi", wifi["new_aliases"])
        self.assertNotIn("无线网络", wifi["new_aliases"])

    def test_wifi_bluetooth_office_candidates_are_detected(self):
        report = self._mine()
        by_name = {item["canonical"]: item for item in report["suggestions"]}
        self.assertIn("Wi-Fi", by_name)
        self.assertIn("蓝牙", by_name)
        self.assertIn("Microsoft Office", by_name)
        self.assertIn("case_wifi", by_name["Wi-Fi"]["evidence_cases"])
        self.assertIn("case_bt", by_name["蓝牙"]["evidence_cases"])
        self.assertIn("case_office", by_name["Microsoft Office"]["evidence_cases"])

    def test_generic_terms_are_not_standalone_suggestions(self):
        report = self._mine()
        all_aliases = {alias for item in report["suggestions"] for alias in item["aliases"]}
        self.assertNotIn("系统", all_aliases)
        self.assertNotIn("电脑", all_aliases)
        self.assertNotIn("文件", all_aliases)

    def test_confidence_score_is_between_zero_and_one(self):
        report = self._mine()
        for item in report["suggestions"]:
            self.assertGreaterEqual(item["confidence_score"], 0.0)
            self.assertLessEqual(item["confidence_score"], 1.0)

    def test_output_json_schema(self):
        report = self._mine()
        self.assertEqual("alias-candidate-mining-v1", report["schema_version"])
        self.assertIn("summary", report)
        self.assertIn("suggestions", report)
        first = report["suggestions"][0]
        for key in (
            "canonical",
            "aliases",
            "new_aliases",
            "confidence_score",
            "confidence_band",
            "status",
            "risk",
            "evidence_cases",
            "evidence",
        ):
            self.assertIn(key, first)

    def test_no_network_embedding_or_reranker_calls(self):
        with patch("socket.create_connection", side_effect=AssertionError("network disabled")):
            report = self._mine()
        self.assertGreater(report["summary"]["total_candidates"], 0)

    def test_query_aliases_file_is_not_modified(self):
        before = hashlib.sha256(self.alias_file.read_bytes()).hexdigest()
        report = self._mine()
        write_outputs(report, self.root / "out.json", self.root / "out.md")
        after = hashlib.sha256(self.alias_file.read_bytes()).hexdigest()
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()

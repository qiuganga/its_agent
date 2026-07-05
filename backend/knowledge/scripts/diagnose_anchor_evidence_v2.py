from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
KNOWLEDGE_ROOT = SCRIPT_PATH.parents[1]
REPO_ROOT = KNOWLEDGE_ROOT.parents[1]
if str(KNOWLEDGE_ROOT) not in sys.path:
    sys.path.insert(0, str(KNOWLEDGE_ROOT))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from services.anchor_evidence_service import (  # noqa: E402
    ANCHOR_TYPE_HARD,
    ANCHOR_TYPE_NEGATIVE,
    ANCHOR_TYPE_SOFT,
    evaluate_document_evidence,
    extract_anchors,
)


TESTDATA = KNOWLEDGE_ROOT / "testdata"
CASES_PATH = TESTDATA / "rag_eval_cases_v2.json"
LEGACY_REPORT_PATH = TESTDATA / "rag_eval_report_v2_anchor_evidence.json"
OUT_JSON = TESTDATA / "rag_anchor_evidence_v2_diagnosis.json"
OUT_MD = TESTDATA / "rag_anchor_evidence_v2_diagnosis.md"

FOCUS_CASES = {
    "case_025",
    "case_026",
    "case_027",
    "case_030",
    "case_039",
    "case_040",
    "case_071",
    "case_072",
    "case_074",
    "case_080",
}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def classify_reason(result: dict[str, Any], case: dict[str, Any], anchors: list[Any]) -> str:
    hard = [anchor for anchor in anchors if anchor.anchor_type == ANCHOR_TYPE_HARD]
    soft = [anchor for anchor in anchors if anchor.anchor_type == ANCHOR_TYPE_SOFT]
    negative = [anchor for anchor in anchors if anchor.anchor_type == ANCHOR_TYPE_NEGATIVE]
    window = result.get("documents_before_threshold") or []
    final_docs = result.get("final_documents") or []
    expected_sources = set(case.get("expected_source_ids") or [])
    if not hard and soft:
        return "SOFT_ANCHOR_WRONGLY_USED_FOR_BLOCK"
    if any(anchor.term in {"Windows", "Word", "Excel", "Bluetooth", "Wi-Fi", "蓝牙设备"} for anchor in anchors):
        return "ALIAS_OR_LANGUAGE_GAP"
    if negative:
        return "NEGATION_NOT_HANDLED"
    if hard and any(_doc_matches_hard(doc, hard) for doc in window) and not any(_doc_matches_hard(doc, hard) for doc in final_docs):
        return "EVIDENCE_ONLY_OUTSIDE_TOP2"
    if expected_sources and not any(doc.get("source_id") in expected_sources for doc in window):
        return "CANDIDATE_RECALL_MISSING"
    if hard and any(anchor.source == "configured_hard_phrase" for anchor in hard):
        return "HARD_ANCHOR_TOO_BROAD"
    if case.get("review_status") == "needs_manual_review":
        return "GOLD_CASE_NEEDS_MANUAL_REVIEW"
    return "OTHER"


def _doc_matches_hard(doc: dict[str, Any], hard_anchors: list[Any]) -> bool:
    fake_doc = type("Doc", (), {})()
    fake_doc.page_content = ""
    fake_doc.metadata = {"title": doc.get("title") or "", "keywords": ""}
    evidence = evaluate_document_evidence(hard_anchors, fake_doc)
    return bool(evidence.matched_hard_anchor_terms)


def diagnose() -> dict[str, Any]:
    cases = {case["id"]: case for case in load_json(CASES_PATH)}
    report = load_json(LEGACY_REPORT_PATH)
    rejected = [
        item
        for item in report.get("results", [])
        if item.get("case_id") in FOCUS_CASES or item.get("rejected_by_anchor_evidence")
    ]
    records = []
    for result in rejected:
        case = cases.get(result["case_id"], {})
        anchors = extract_anchors(result.get("original_question", ""))
        hard = [anchor for anchor in anchors if anchor.anchor_type == ANCHOR_TYPE_HARD]
        soft = [anchor for anchor in anchors if anchor.anchor_type == ANCHOR_TYPE_SOFT]
        negative = [anchor for anchor in anchors if anchor.anchor_type == ANCHOR_TYPE_NEGATIVE]
        window = result.get("documents_before_threshold") or []
        final_docs = result.get("final_documents") or []
        expected_sources = set(case.get("expected_source_ids") or [])
        record = {
            "case_id": result["case_id"],
            "original_question": result.get("original_question"),
            "case_group": result.get("case_group"),
            "expected_answerability": result.get("expected_answerability"),
            "anchors": [
                {
                    "term": anchor.term,
                    "normalized_term": anchor.normalized_term,
                    "anchor_type": anchor.anchor_type,
                    "aliases": list(anchor.aliases),
                    "source": anchor.source,
                }
                for anchor in anchors
            ],
            "hard_anchors": [anchor.term for anchor in hard],
            "soft_anchors": [anchor.term for anchor in soft],
            "negative_anchors": [anchor.term for anchor in negative],
            "final_top2": [_summarize_doc(doc) for doc in final_docs[:2]],
            "final_top2_has_anchor": any((doc.get("matched_anchor_terms") or []) for doc in final_docs[:2]),
            "candidate_window_has_anchor": any((doc.get("matched_anchor_terms") or []) for doc in window),
            "candidate_window_has_hard_anchor": any((doc.get("matched_hard_anchor_terms") or []) for doc in window),
            "expected_sources_in_window": [doc.get("source_id") for doc in window if doc.get("source_id") in expected_sources],
            "expected_source_ids": sorted(expected_sources),
            "rejection_reason": (result.get("anchor_decision") or {}).get("reason_code"),
            "diagnosis_reason": classify_reason(result, case, anchors),
        }
        records.append(record)
    summary = {}
    for record in records:
        summary[record["diagnosis_reason"]] = summary.get(record["diagnosis_reason"], 0) + 1
    return {
        "status": "success",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "legacy_report": str(LEGACY_REPORT_PATH),
        "total_records": len(records),
        "reason_counts": summary,
        "records": records,
        "notes": [
            "This script diagnoses existing reports only; it does not call Embedding, LLM, /query, or Chroma.",
            "Diagnosis categories are heuristic and require manual confirmation.",
        ],
    }


def _summarize_doc(doc: dict[str, Any]) -> dict[str, Any]:
    return {
        "title": doc.get("title"),
        "source_id": doc.get("source_id"),
        "final_rerank_score": doc.get("final_rerank_score"),
        "anchor_adjustment": doc.get("anchor_adjustment"),
        "evidence_adjusted_score": doc.get("evidence_adjusted_score"),
        "anchor_evidence_status": doc.get("anchor_evidence_status"),
        "matched_anchor_terms": doc.get("matched_anchor_terms") or [],
        "matched_hard_anchor_terms": doc.get("matched_hard_anchor_terms") or [],
        "matched_soft_anchor_terms": doc.get("matched_soft_anchor_terms") or [],
        "matched_negative_anchor_terms": doc.get("matched_negative_anchor_terms") or [],
    }


def write_reports(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        "# Anchor Evidence v2 Diagnosis",
        "",
        f"- Status: `{report['status']}`",
        f"- Generated at: `{report['generated_at']}`",
        f"- Records: {report['total_records']}",
        "",
        "## Reason Counts",
        "",
    ]
    for reason, count in sorted(report["reason_counts"].items()):
        lines.append(f"- {reason}: {count}")
    lines.extend(["", "## Records", ""])
    for record in report["records"]:
        lines.append(f"### {record['case_id']}")
        lines.append(f"- Question: {record['original_question']}")
        lines.append(f"- Group: {record['case_group']} / {record['expected_answerability']}")
        lines.append(f"- Hard: {record['hard_anchors']}")
        lines.append(f"- Soft: {record['soft_anchors']}")
        lines.append(f"- Negative: {record['negative_anchors']}")
        lines.append(f"- Rejection: {record['rejection_reason']}")
        lines.append(f"- Diagnosis: {record['diagnosis_reason']}")
        lines.append(f"- Expected source in window: {record['expected_sources_in_window']}")
        lines.append(f"- Final Top2: {[doc['title'] for doc in record['final_top2']]}")
        lines.append("")
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = diagnose()
    write_reports(report)
    print("Anchor Evidence v2 diagnosis completed")
    print(f"records={report['total_records']}")
    print(f"reason_counts={report['reason_counts']}")
    print(f"json_report={OUT_JSON}")
    print(f"md_report={OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

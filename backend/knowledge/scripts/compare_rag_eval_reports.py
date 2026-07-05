from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
KNOWLEDGE_ROOT = SCRIPT_PATH.parents[1]

BEFORE_JSON = KNOWLEDGE_ROOT / "testdata" / "rag_eval_report_before_normalization_fix.json"
AFTER_JSON = KNOWLEDGE_ROOT / "testdata" / "rag_eval_report_after_normalization_fix.json"
OUT_JSON = KNOWLEDGE_ROOT / "testdata" / "rag_eval_normalization_comparison.json"
OUT_MD = KNOWLEDGE_ROOT / "testdata" / "rag_eval_normalization_comparison.md"

FOCUS_CASES = [
    "case_001",
    "case_002",
    "case_003",
    "case_006",
    "case_009",
    "case_010",
    "case_011",
    "case_012",
]
NO_ANSWER_CASES = ["case_022", "case_023", "case_024"]


def load_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def result_map(report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {item["case_id"]: item for item in report.get("results", [])}


def top_titles(result: dict[str, Any], n: int = 2) -> list[str]:
    docs = result.get("final_documents") or result.get("documents_before_threshold") or []
    return [(doc.get("title") or "") for doc in docs[:n]]


def top_scores(result: dict[str, Any], n: int = 2) -> list[float | None]:
    docs = result.get("final_documents") or result.get("documents_before_threshold") or []
    return [to_float(doc.get("final_rerank_score")) for doc in docs[:n]]


def top_matched_by_normalized(result: dict[str, Any], n: int = 2) -> list[bool]:
    docs = result.get("final_documents") or result.get("documents_before_threshold") or []
    return [bool(doc.get("matched_by_normalized_query")) for doc in docs[:n]]


def to_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def title_hit(result: dict[str, Any], rank: int) -> bool:
    key = "top1_title_weak_hit" if rank == 1 else "top2_title_weak_hit"
    return bool(result.get(key))


def classify_case(before: dict[str, Any], after: dict[str, Any]) -> str:
    before_top2_hit = title_hit(before, 2)
    after_top2_hit = title_hit(after, 2)
    before_top1_hit = title_hit(before, 1)
    after_top1_hit = title_hit(after, 1)
    before_titles = top_titles(before)
    after_titles = top_titles(after)
    before_norm = before.get("normalized_question")
    after_norm = after.get("normalized_question")

    if after_top2_hit and not before_top2_hit:
        return "positive"
    if after_top1_hit and not before_top1_hit:
        return "positive"
    if before_top2_hit and not after_top2_hit:
        return "negative"
    if before_titles != after_titles or before_norm != after_norm:
        return "requires_manual_review"
    return "unchanged"


def compare_case(case_id: str, before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    return {
        "case_id": case_id,
        "original_question_same": before.get("original_question") == after.get("original_question"),
        "original_question": after.get("original_question"),
        "before_normalized_question": before.get("normalized_question"),
        "after_normalized_question": after.get("normalized_question"),
        "normalized_question_changed": before.get("normalized_question") != after.get("normalized_question"),
        "before_dual_retrieval_enabled": before.get("dual_retrieval_enabled"),
        "after_dual_retrieval_enabled": after.get("dual_retrieval_enabled"),
        "retrieval_mode_changed": before.get("dual_retrieval_enabled") != after.get("dual_retrieval_enabled"),
        "before_candidate_count_before_dedup": before.get("candidate_count_before_dedup"),
        "after_candidate_count_before_dedup": after.get("candidate_count_before_dedup"),
        "before_candidate_count_after_dedup": before.get("candidate_count_after_dedup"),
        "after_candidate_count_after_dedup": after.get("candidate_count_after_dedup"),
        "before_top_titles": top_titles(before),
        "after_top_titles": top_titles(after),
        "before_top_scores": top_scores(before),
        "after_top_scores": top_scores(after),
        "before_matched_by_normalized_query": top_matched_by_normalized(before),
        "after_matched_by_normalized_query": top_matched_by_normalized(after),
        "before_top1_title_weak_hit": title_hit(before, 1),
        "after_top1_title_weak_hit": title_hit(after, 1),
        "before_top2_title_weak_hit": title_hit(before, 2),
        "after_top2_title_weak_hit": title_hit(after, 2),
        "before_rejected_by_low_confidence": before.get("rejected_by_low_confidence"),
        "after_rejected_by_low_confidence": after.get("rejected_by_low_confidence"),
        "classification": classify_case(before, after),
    }


def compare_reports(before_report: dict[str, Any], after_report: dict[str, Any]) -> dict[str, Any]:
    before_results = result_map(before_report)
    after_results = result_map(after_report)
    common_ids = sorted(set(before_results) & set(after_results))
    case_comparisons = [
        compare_case(case_id, before_results[case_id], after_results[case_id])
        for case_id in common_ids
    ]
    classification_counts = Counter(item["classification"] for item in case_comparisons)
    return {
        "status": "success",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "before": {
            "path": str(BEFORE_JSON),
            "generated_at": before_report.get("generated_at"),
            "summary": before_report.get("summary", {}),
        },
        "after": {
            "path": str(AFTER_JSON),
            "generated_at": after_report.get("generated_at"),
            "summary": after_report.get("summary", {}),
        },
        "overall_delta": build_overall_delta(before_report.get("summary", {}), after_report.get("summary", {})),
        "classification_counts": dict(classification_counts),
        "focus_cases": [item for item in case_comparisons if item["case_id"] in FOCUS_CASES],
        "no_answer_cases": [item for item in case_comparisons if item["case_id"] in NO_ANSWER_CASES],
        "case_comparisons": case_comparisons,
        "notes": [
            "expected_title_contains is only a weak automatic label, not final retrieval accuracy.",
            "requires_manual_review means title/score changes are insufficient for reliable automatic judgment.",
            "This comparison only analyzes report deltas and does not call external services.",
        ],
    }


def build_overall_delta(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    keys = [
        "total_cases",
        "normalization_triggered",
        "normalization_not_triggered",
        "dual_retrieval_count",
        "single_retrieval_count",
        "accepted_count",
        "low_confidence_rejected_count",
        "top1_title_weak_hit_count",
        "top2_title_weak_hit_count",
        "expected_no_answer_correctly_rejected",
        "expected_no_answer_not_rejected",
    ]
    return {
        key: {
            "before": before.get(key),
            "after": after.get(key),
            "delta": numeric_delta(before.get(key), after.get(key)),
        }
        for key in keys
    }


def numeric_delta(before: Any, after: Any) -> float | int | None:
    if isinstance(before, (int, float)) and isinstance(after, (int, float)):
        return after - before
    return None


def write_reports(comparison: dict[str, Any]) -> None:
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(comparison, handle, ensure_ascii=False, indent=2)
    with OUT_MD.open("w", encoding="utf-8") as handle:
        handle.write(render_markdown(comparison))


def render_markdown(comparison: dict[str, Any]) -> str:
    lines = [
        "# RAG Normalization A/B Comparison",
        "",
        f"- Generated at: `{comparison['generated_at']}`",
        f"- Before report: `{comparison['before']['path']}`",
        f"- Before generated at: `{comparison['before']['generated_at']}`",
        f"- After report: `{comparison['after']['path']}`",
        f"- After generated at: `{comparison['after']['generated_at']}`",
        "",
        "## Overall Delta",
        "",
        "| Metric | Before | After | Delta |",
        "|---|---:|---:|---:|",
    ]
    for key, item in comparison["overall_delta"].items():
        lines.append(f"| {key} | {item['before']} | {item['after']} | {item['delta']} |")

    lines.extend([
        "",
        "## Classification Counts",
        "",
    ])
    for key, count in comparison["classification_counts"].items():
        lines.append(f"- {key}: {count}")

    lines.extend([
        "",
        "## Focus Cases",
        "",
    ])
    for item in comparison["focus_cases"]:
        lines.extend(render_case(item))

    lines.extend([
        "",
        "## No-answer Cases",
        "",
    ])
    for item in comparison["no_answer_cases"]:
        lines.extend(render_case(item))

    lines.extend([
        "",
        "## Notes",
        "",
    ])
    for note in comparison["notes"]:
        lines.append(f"- {note}")
    return "\n".join(lines)


def render_case(item: dict[str, Any]) -> list[str]:
    return [
        f"### {item['case_id']}",
        f"- Question: {item['original_question']}",
        f"- Normalized before: {item['before_normalized_question']}",
        f"- Normalized after: {item['after_normalized_question']}",
        f"- Dual before/after: {item['before_dual_retrieval_enabled']} / {item['after_dual_retrieval_enabled']}",
        f"- Candidates before/after: {item['before_candidate_count_after_dedup']} / {item['after_candidate_count_after_dedup']}",
        f"- Top titles before: {item['before_top_titles']}",
        f"- Top titles after: {item['after_top_titles']}",
        f"- Scores before: {item['before_top_scores']}",
        f"- Scores after: {item['after_top_scores']}",
        f"- Top2 weak hit before/after: {item['before_top2_title_weak_hit']} / {item['after_top2_title_weak_hit']}",
        f"- Classification: `{item['classification']}`",
        "",
    ]


def main() -> int:
    before_report = load_report(BEFORE_JSON)
    after_report = load_report(AFTER_JSON)
    comparison = compare_reports(before_report, after_report)
    write_reports(comparison)
    print("RAG normalization comparison completed")
    print(f"classification_counts={comparison['classification_counts']}")
    print(f"json_report={OUT_JSON}")
    print(f"md_report={OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

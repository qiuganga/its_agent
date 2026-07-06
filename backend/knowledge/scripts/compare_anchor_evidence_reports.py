from __future__ import annotations

import json
import argparse
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
KNOWLEDGE_ROOT = SCRIPT_PATH.parents[1]
TESTDATA = KNOWLEDGE_ROOT / "testdata"

BASELINE_REPORT = TESTDATA / "rag_eval_report_clean_v1_anchor_baseline.json"
FALLBACK_BASELINE_REPORT = TESTDATA / "rag_eval_report_clean_v1.json"
EXPERIMENT_REPORT = TESTDATA / "rag_eval_report_clean_v1_anchor_evidence.json"
OUT_JSON = TESTDATA / "rag_anchor_evidence_comparison.json"
OUT_MD = TESTDATA / "rag_anchor_evidence_comparison.md"

FOCUS_CASES = [
    "case_002",
    "case_005",
    "case_006",
    "case_009",
    "case_010",
    "case_014",
    "case_015",
    "case_022",
    "case_023",
    "case_024",
]


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def result_map(report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {item["case_id"]: item for item in report.get("results", [])}


def top_docs(result: dict[str, Any]) -> list[dict[str, Any]]:
    return result.get("final_documents") or result.get("documents_before_threshold") or []


def top_titles(result: dict[str, Any]) -> list[str]:
    return [doc.get("title") or "" for doc in top_docs(result)[:2]]


def missing_source_count(report: dict[str, Any]) -> int:
    return sum(
        1
        for result in report.get("results", [])
        for doc in top_docs(result)
        if not doc.get("source_id")
    )


def metric_summary(report: dict[str, Any]) -> dict[str, Any]:
    summary = report.get("summary", {})
    return {
        "total_cases": summary.get("total_cases"),
        "strong_anchor_case_count": summary.get("strong_anchor_case_count", 0),
        "hard_anchor_case_count": summary.get("hard_anchor_case_count", 0),
        "soft_anchor_case_count": summary.get("soft_anchor_case_count", 0),
        "negative_anchor_case_count": summary.get("negative_anchor_case_count", 0),
        "no_anchor_case_count": summary.get("no_anchor_case_count", 0),
        "no_strong_anchor_case_count": summary.get("no_strong_anchor_case_count", 0),
        "top1_title_weak_hit_count": summary.get("top1_title_weak_hit_count"),
        "top2_title_weak_hit_count": summary.get("top2_title_weak_hit_count"),
        "expected_no_answer_correctly_rejected": summary.get("expected_no_answer_correctly_rejected"),
        "expected_no_answer_anchor_rejected": summary.get("expected_no_answer_anchor_rejected", 0),
        "expected_no_answer_not_rejected": summary.get("expected_no_answer_not_rejected"),
        "expected_answer_false_rejected": summary.get("expected_answer_false_rejected"),
        "anchor_evidence_missing_count": summary.get("anchor_evidence_missing_count", 0),
        "hard_evidence_exists_outside_topk_count": summary.get("hard_evidence_exists_outside_topk_count", 0),
        "negative_anchor_penalty_count": summary.get("negative_anchor_penalty_count", 0),
        "bm25_mode": summary.get("bm25_mode", "off"),
        "bm25_candidate_total": summary.get("bm25_candidate_total", 0),
        "bm25_unique_added_total": summary.get("bm25_unique_added_total", 0),
        "bm25_vector_overlap_total": summary.get("bm25_vector_overlap_total", 0),
        "bm25_title_overlap_total": summary.get("bm25_title_overlap_total", 0),
        "source_id_missing_before_rerank_total": summary.get("source_id_missing_before_rerank_total", 0),
        "missing_source_topk_count": missing_source_count(report),
        "group_metrics": summary.get("group_metrics", {}),
    }


def summarize_doc(doc: dict[str, Any]) -> dict[str, Any]:
    return {
        "title": doc.get("title") or "",
        "source_id": doc.get("source_id") or "",
        "final_rerank_score": doc.get("final_rerank_score"),
        "anchor_adjustment": doc.get("anchor_adjustment"),
        "evidence_adjusted_score": doc.get("evidence_adjusted_score"),
        "anchor_evidence_status": doc.get("anchor_evidence_status"),
        "matched_anchor_terms": doc.get("matched_anchor_terms") or [],
        "hard_anchor_adjustment": doc.get("hard_anchor_adjustment"),
        "soft_anchor_adjustment": doc.get("soft_anchor_adjustment"),
        "negative_anchor_adjustment": doc.get("negative_anchor_adjustment"),
        "retrieval_routes": doc.get("retrieval_routes") or [],
        "bm25_score": doc.get("bm25_score"),
    }


def compare_case(case_id: str, baseline: dict[str, Any], experiment: dict[str, Any]) -> dict[str, Any]:
    baseline_titles = top_titles(baseline)
    experiment_titles = top_titles(experiment)
    return {
        "case_id": case_id,
        "question": experiment.get("original_question") or baseline.get("original_question"),
        "extracted_anchors": (
            (experiment.get("anchor_decision") or {}).get("anchor_evidence", {}).get("anchors")
            or [term for doc in experiment.get("documents_before_threshold", []) for term in doc.get("anchor_terms", [])]
        ),
        "baseline_top2": baseline_titles,
        "experiment_top2": experiment_titles,
        "top2_changed": baseline_titles != experiment_titles,
        "baseline_rejected": bool(baseline.get("rejected_by_low_confidence") or baseline.get("rejected_by_anchor_evidence")),
        "experiment_rejected": bool(experiment.get("rejected_by_low_confidence") or experiment.get("rejected_by_anchor_evidence")),
        "experiment_rejection_reason": (experiment.get("anchor_decision") or {}).get("reason_code"),
        "requires_manual_review": bool(
            experiment.get("expected_no_answer") and not experiment.get("rejected_by_anchor_evidence")
        ),
        "experiment_documents": [summarize_doc(doc) for doc in top_docs(experiment)[:2]],
    }


def build_comparison() -> dict[str, Any]:
    baseline_path = BASELINE_REPORT if BASELINE_REPORT.exists() else FALLBACK_BASELINE_REPORT
    return build_comparison_from_paths(baseline_path, EXPERIMENT_REPORT)


def build_comparison_from_paths(baseline_path: Path, experiment_path: Path) -> dict[str, Any]:
    baseline = load_json(baseline_path)
    experiment = load_json(experiment_path)
    validate_comparable_reports(baseline, experiment)
    baseline_map = result_map(baseline)
    experiment_map = result_map(experiment)
    case_ids = sorted(set(baseline_map) & set(experiment_map))
    comparisons = [compare_case(case_id, baseline_map[case_id], experiment_map[case_id]) for case_id in case_ids]
    changed_counter = Counter("changed" if item["top2_changed"] else "unchanged" for item in comparisons)
    return {
        "status": "success",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "baseline_report": str(baseline_path),
        "experiment_report": str(experiment_path),
        "metrics": {
            "baseline": metric_summary(baseline),
            "experiment": metric_summary(experiment),
        },
        "top2_change_counts": dict(changed_counter),
        "analysis": build_analysis(baseline, experiment, comparisons),
        "bm25_analysis": build_bm25_analysis(baseline, experiment, comparisons),
        "focus_cases": [item for item in comparisons if item["case_id"] in FOCUS_CASES],
        "case_comparisons": comparisons,
        "notes": [
            "expected_title_contains remains a weak label and is not treated as ground truth.",
            "Anchor rejection is based only on extracted anchors from original_question and final TopK evidence fields.",
        ],
    }


def validate_comparable_reports(
    baseline: dict[str, Any],
    experiment: dict[str, Any],
    *,
    expected_total_cases: int | None = None,
) -> None:
    baseline_summary = baseline.get("summary", {})
    experiment_summary = experiment.get("summary", {})
    baseline_settings = baseline.get("settings", {})
    experiment_settings = experiment.get("settings", {})
    baseline_total = baseline_summary.get("total_cases")
    experiment_total = experiment_summary.get("total_cases")
    errors = []

    if baseline_total != experiment_total:
        errors.append(f"total_cases mismatch: baseline={baseline_total}, experiment={experiment_total}")
    if expected_total_cases is not None and baseline_total != expected_total_cases:
        errors.append(f"baseline total_cases must be {expected_total_cases}, got {baseline_total}")
    if expected_total_cases is not None and experiment_total != expected_total_cases:
        errors.append(f"experiment total_cases must be {expected_total_cases}, got {experiment_total}")
    if baseline.get("cases_file") != experiment.get("cases_file"):
        errors.append(f"cases_file mismatch: baseline={baseline.get('cases_file')}, experiment={experiment.get('cases_file')}")

    comparable_setting_keys = [
        "collection_name",
        "RAG_ANCHOR_EVIDENCE_MODE",
        "EMBEDDING_MODEL",
        "VECTOR_DISTANCE_SPACE",
        "RAG_VECTOR_CANDIDATE_TOP_K",
        "RAG_TITLE_CANDIDATE_TOP_K",
        "RAG_FINAL_TOP_K",
        "RAG_MIN_RERANK_SCORE",
    ]
    for key in comparable_setting_keys:
        if baseline_settings.get(key) != experiment_settings.get(key):
            errors.append(f"{key} mismatch: baseline={baseline_settings.get(key)}, experiment={experiment_settings.get(key)}")

    baseline_bm25 = baseline_summary.get("bm25_mode") or baseline_settings.get("RAG_BM25_MODE")
    experiment_bm25 = experiment_summary.get("bm25_mode") or experiment_settings.get("RAG_BM25_MODE")
    if baseline_bm25 == experiment_bm25:
        errors.append(f"bm25_mode should differ for A/B comparison, got both={baseline_bm25}")

    if errors:
        raise ValueError("Reports are not comparable: " + "; ".join(errors))


def infer_expected_total_cases(args: argparse.Namespace) -> int | None:
    if args.expected_total_cases is not None:
        return args.expected_total_cases
    if args.output_prefix and "v2_82" in args.output_prefix:
        return 82
    return None


def build_bm25_analysis(
    baseline: dict[str, Any],
    experiment: dict[str, Any],
    comparisons: list[dict[str, Any]],
) -> dict[str, Any]:
    baseline_summary = baseline.get("summary", {})
    experiment_summary = experiment.get("summary", {})
    changed = [item for item in comparisons if item["top2_changed"]]
    improved = []
    regressed = []
    for item in comparisons:
        baseline_hit = bool((result_map(baseline).get(item["case_id"]) or {}).get("top2_title_weak_hit"))
        experiment_hit = bool((result_map(experiment).get(item["case_id"]) or {}).get("top2_title_weak_hit"))
        if experiment_hit and not baseline_hit:
            improved.append(item["case_id"])
        if baseline_hit and not experiment_hit:
            regressed.append(item["case_id"])
    return {
        "baseline_bm25_mode": baseline_summary.get("bm25_mode", "off"),
        "experiment_bm25_mode": experiment_summary.get("bm25_mode", "off"),
        "bm25_candidate_delta": int(experiment_summary.get("bm25_candidate_total", 0))
        - int(baseline_summary.get("bm25_candidate_total", 0)),
        "bm25_unique_added_delta": int(experiment_summary.get("bm25_unique_added_total", 0))
        - int(baseline_summary.get("bm25_unique_added_total", 0)),
        "top2_changed_cases": [item["case_id"] for item in changed],
        "top2_weak_hit_improved_cases": improved,
        "top2_weak_hit_regressed_cases": regressed,
    }


def build_three_way_comparison_from_paths(
    baseline_path: Path,
    legacy_path: Path,
    experiment_path: Path,
) -> dict[str, Any]:
    comparison = build_comparison_from_paths(baseline_path, experiment_path)
    legacy = load_json(legacy_path)
    comparison["legacy_report"] = str(legacy_path)
    comparison["metrics"]["legacy"] = metric_summary(legacy)
    comparison["three_way_analysis"] = {
        "legacy_false_rejected": metric_summary(legacy).get("expected_answer_false_rejected"),
        "new_false_rejected": comparison["metrics"]["experiment"].get("expected_answer_false_rejected"),
        "legacy_anchor_rejected_no_answer": metric_summary(legacy).get("expected_no_answer_anchor_rejected"),
        "new_anchor_rejected_no_answer": comparison["metrics"]["experiment"].get("expected_no_answer_anchor_rejected"),
        "new_hard_evidence_outside_topk": comparison["metrics"]["experiment"].get("hard_evidence_exists_outside_topk_count"),
        "new_negative_anchor_penalties": comparison["metrics"]["experiment"].get("negative_anchor_penalty_count"),
    }
    return comparison


def build_analysis(
    baseline: dict[str, Any],
    experiment: dict[str, Any],
    comparisons: list[dict[str, Any]],
) -> dict[str, Any]:
    experiment_summary = experiment.get("summary", {})
    group_metrics = experiment_summary.get("group_metrics", {})
    false_rejected = []
    still_accepted = []
    for group, metrics in group_metrics.items():
        false_rejected.extend(metrics.get("expected_answer_false_rejected_cases", []))
        still_accepted.extend(metrics.get("expected_no_answer_still_accepted_cases", []))
    changed = [item for item in comparisons if item["top2_changed"]]
    likely_anchor_help = [
        item["case_id"]
        for item in changed
        if any(doc.get("anchor_adjustment") and doc.get("anchor_adjustment") > 0 for doc in item.get("experiment_documents", []))
    ]
    anchor_missing = [
        item["case_id"]
        for item in comparisons
        if item.get("experiment_rejection_reason") == "ANCHOR_EVIDENCE_MISSING"
    ]
    return {
        "anchor_gate_rejects_anchor_unanswerable": group_metrics.get("B_anchor_unanswerable", {}).get(
            "expected_no_answer_correctly_rejected_count", 0
        ),
        "anchor_gate_false_rejected_answerable": false_rejected,
        "no_strong_anchor_answerable_false_rejected": group_metrics.get("C_generic_answerable", {}).get(
            "expected_answer_false_rejected_cases", []
        ),
        "remaining_unanswerable_accepted": still_accepted,
        "anchor_missing_cases": anchor_missing,
        "top2_changed_cases": [item["case_id"] for item in changed],
        "likely_anchor_help_cases": likely_anchor_help,
        "requires_reranker_groups": [
            group
            for group, metrics in group_metrics.items()
            if metrics.get("needs_manual_review_count", 0) > 0 and group not in {"B_anchor_unanswerable"}
        ],
        "boost_penalty_side_effect_note": (
            "Review top2_changed_cases and likely_anchor_help_cases; the script does not tune boost or penalty."
        ),
    }


def write_reports(comparison: dict[str, Any], json_path: Path = OUT_JSON, md_path: Path = OUT_MD) -> None:
    json_path.write_text(json.dumps(comparison, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown(comparison), encoding="utf-8")


def render_markdown(comparison: dict[str, Any]) -> str:
    lines = [
        "# RAG Anchor Evidence A/B Comparison",
        "",
        f"- Generated at: `{comparison['generated_at']}`",
        f"- Baseline: `{comparison['baseline_report']}`",
        f"- Experiment: `{comparison['experiment_report']}`",
        "",
        "## Metrics",
        "",
        "| Group | Total | Hard | Soft | Negative | No Anchor | Top1 Hit | Top2 Hit | No-answer Anchor Rejected | No-answer Passed | False Rejected | ANCHOR_EVIDENCE_MISSING | Hard Outside TopK | Negative Penalties | Missing source_id |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name, metrics in comparison["metrics"].items():
        lines.append(
            f"| {name} | {metrics['total_cases']} | {metrics.get('hard_anchor_case_count', 0)} | "
            f"{metrics.get('soft_anchor_case_count', 0)} | {metrics.get('negative_anchor_case_count', 0)} | "
            f"{metrics.get('no_anchor_case_count', 0)} | {metrics['top1_title_weak_hit_count']} | "
            f"{metrics['top2_title_weak_hit_count']} | {metrics['expected_no_answer_anchor_rejected']} | "
            f"{metrics['expected_no_answer_not_rejected']} | {metrics['expected_answer_false_rejected']} | "
            f"{metrics['anchor_evidence_missing_count']} | {metrics.get('hard_evidence_exists_outside_topk_count', 0)} | "
            f"{metrics.get('negative_anchor_penalty_count', 0)} | {metrics['missing_source_topk_count']} |"
        )
    lines.extend(["", "## Top2 Changes", ""])
    for key, value in comparison["top2_change_counts"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Analysis", ""])
    analysis = comparison.get("analysis", {})
    for key, value in analysis.items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## BM25 Analysis", ""])
    for key, value in comparison.get("bm25_analysis", {}).items():
        lines.append(f"- {key}: {value}")
    if comparison.get("three_way_analysis"):
        lines.extend(["", "## Three-way Analysis", ""])
        for key, value in comparison["three_way_analysis"].items():
            lines.append(f"- {key}: {value}")
    lines.extend(["", "## Group Metrics", ""])
    for name, metrics in comparison["metrics"].items():
        lines.append(f"### {name}")
        for group, group_metrics in (metrics.get("group_metrics") or {}).items():
            lines.append(
                f"- {group}: total={group_metrics.get('total')}, top2={group_metrics.get('top2_title_weak_hit_count')}, "
                f"false_rejected={group_metrics.get('expected_answer_false_rejected_count')}, "
                f"no_answer_rejected={group_metrics.get('expected_no_answer_correctly_rejected_count')}, "
                f"no_answer_accepted={group_metrics.get('expected_no_answer_still_accepted_count')}, "
                f"anchor_missing={group_metrics.get('anchor_evidence_missing_count')}"
            )
    lines.extend(["", "## Focus Cases", ""])
    for item in comparison["focus_cases"]:
        lines.append(f"### {item['case_id']}")
        lines.append(f"- Question: {item['question']}")
        lines.append(f"- Anchors: {item['extracted_anchors']}")
        lines.append(f"- Baseline Top2: {item['baseline_top2']}")
        lines.append(f"- Experiment Top2: {item['experiment_top2']}")
        lines.append(f"- Rejected: {item['experiment_rejected']} reason={item['experiment_rejection_reason']}")
        for doc in item["experiment_documents"]:
            lines.append(
                f"  - {doc['title']} | score={doc['final_rerank_score']} "
                f"adjust={doc['anchor_adjustment']} adjusted={doc['evidence_adjusted_score']} "
                f"status={doc['anchor_evidence_status']} matched={doc['matched_anchor_terms']}"
            )
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare baseline and experimental RAG evaluation reports.")
    parser.add_argument("--baseline", help="Baseline report JSON path.")
    parser.add_argument("--legacy", help="Legacy anchor report JSON path.")
    parser.add_argument("--experiment", help="Experimental report JSON path.")
    parser.add_argument("--output-prefix", help="Write comparison to testdata/<prefix>.json/.md.")
    parser.add_argument("--expected-total-cases", type=int, help="Reject comparison unless both reports have this total_cases value.")
    args = parser.parse_args()
    baseline = Path(args.baseline) if args.baseline else (BASELINE_REPORT if BASELINE_REPORT.exists() else FALLBACK_BASELINE_REPORT)
    experiment = Path(args.experiment) if args.experiment else EXPERIMENT_REPORT
    try:
        if args.legacy:
            comparison = build_three_way_comparison_from_paths(baseline, Path(args.legacy), experiment)
        else:
            expected_total_cases = infer_expected_total_cases(args)
            baseline_report = load_json(baseline)
            experiment_report = load_json(experiment)
            validate_comparable_reports(
                baseline_report,
                experiment_report,
                expected_total_cases=expected_total_cases,
            )
            comparison = build_comparison_from_paths(baseline, experiment)
    except ValueError as exc:
        print(f"RAG comparison refused: {exc}")
        return 2
    if args.output_prefix:
        safe_prefix = Path(args.output_prefix).name
        json_path = TESTDATA / f"{safe_prefix}.json"
        md_path = TESTDATA / f"{safe_prefix}.md"
    else:
        json_path = OUT_JSON
        md_path = OUT_MD
    write_reports(comparison, json_path=json_path, md_path=md_path)
    print("RAG anchor evidence comparison completed")
    print(f"metrics={comparison['metrics']}")
    print(f"top2_change_counts={comparison['top2_change_counts']}")
    print(f"json_report={json_path}")
    print(f"md_report={md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
KNOWLEDGE_ROOT = SCRIPT_PATH.parents[1]
TESTDATA = KNOWLEDGE_ROOT / "testdata"

BASELINE_REPORT = TESTDATA / "rag_eval_report_v2_82_hsn_bm25_experimental.json"
EXPERIMENT_REPORT = TESTDATA / "rag_eval_report_v2_82_hsn_bm25_siliconflow_reranker.json"
OUT_JSON = TESTDATA / "rag_siliconflow_reranker_v2_82_comparison.json"
OUT_MD = TESTDATA / "rag_siliconflow_reranker_v2_82_comparison.md"

FOCUS_CASES = {
    "case_001", "case_004", "case_006", "case_007", "case_011", "case_012", "case_015",
    "case_025", "case_026", "case_027", "case_030", "case_039", "case_040",
    "case_069", "case_070", "case_071", "case_072", "case_074", "case_080",
    "case_005", "case_009", "case_010", "case_014",
    "case_022", "case_023", "case_024",
}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def result_map(report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {item["case_id"]: item for item in report.get("results", [])}


def top_docs(result: dict[str, Any]) -> list[dict[str, Any]]:
    return result.get("final_documents") or result.get("documents_before_threshold") or []


def top_titles(result: dict[str, Any]) -> list[str]:
    return [doc.get("title") or "" for doc in top_docs(result)[:2]]


def title_hit(result: dict[str, Any], rank: int) -> bool:
    return bool(result.get("top1_title_weak_hit") if rank == 1 else result.get("top2_title_weak_hit"))


def validate_comparable_reports(baseline: dict[str, Any], experiment: dict[str, Any]) -> None:
    errors = []
    baseline_summary = baseline.get("summary", {})
    experiment_summary = experiment.get("summary", {})
    baseline_settings = baseline.get("settings", {})
    experiment_settings = experiment.get("settings", {})
    if baseline_summary.get("total_cases") != 82 or experiment_summary.get("total_cases") != 82:
        errors.append(
            f"total_cases must both be 82, got baseline={baseline_summary.get('total_cases')} "
            f"experiment={experiment_summary.get('total_cases')}"
        )
    if baseline.get("cases_file") != experiment.get("cases_file"):
        errors.append("cases_file mismatch")
    comparable_settings = [
        "collection_name",
        "RAG_ANCHOR_EVIDENCE_MODE",
        "EMBEDDING_MODEL",
        "VECTOR_DISTANCE_SPACE",
        "RAG_VECTOR_CANDIDATE_TOP_K",
        "RAG_TITLE_CANDIDATE_TOP_K",
        "RAG_FINAL_TOP_K",
        "RAG_MIN_RERANK_SCORE",
        "RAG_BM25_MODE",
        "RAG_BM25_CANDIDATE_TOP_K",
    ]
    for key in comparable_settings:
        if baseline_settings.get(key) != experiment_settings.get(key):
            errors.append(f"{key} mismatch: {baseline_settings.get(key)} != {experiment_settings.get(key)}")
    if baseline_summary.get("bm25_mode") != "experimental" or experiment_summary.get("bm25_mode") != "experimental":
        errors.append("both reports must use bm25_mode=experimental")
    if baseline_summary.get("anchor_evidence_mode") != "hard-soft-negative":
        errors.append("baseline anchor_evidence_mode must be hard-soft-negative")
    if experiment_summary.get("anchor_evidence_mode") != "hard-soft-negative":
        errors.append("experiment anchor_evidence_mode must be hard-soft-negative")
    if experiment_summary.get("reranker_mode") != "experimental":
        errors.append("experiment reranker_mode must be experimental")
    if experiment_summary.get("reranker_provider") != "siliconflow":
        errors.append("experiment reranker_provider must be siliconflow")
    if experiment_summary.get("reranker_success_count") != 82:
        errors.append(f"reranker_success_count must be 82, got {experiment_summary.get('reranker_success_count')}")
    if experiment_summary.get("reranker_failure_count") != 0:
        errors.append(f"reranker_failure_count must be 0, got {experiment_summary.get('reranker_failure_count')}")
    if errors:
        raise ValueError("; ".join(errors))


def summarize_doc(doc: dict[str, Any]) -> dict[str, Any]:
    return {
        "title": doc.get("title"),
        "retrieval_routes": doc.get("retrieval_routes") or [],
        "bm25_score": doc.get("bm25_score"),
        "embedding_rerank_score": doc.get("embedding_rerank_score"),
        "reranker_score": doc.get("reranker_score"),
        "anchor_adjustment": doc.get("anchor_adjustment"),
        "evidence_adjusted_score": doc.get("evidence_adjusted_score"),
    }


def classify_case(baseline: dict[str, Any], experiment: dict[str, Any]) -> str:
    baseline_hit = bool(baseline.get("top2_title_weak_hit"))
    experiment_hit = bool(experiment.get("top2_title_weak_hit"))
    if experiment_hit and not baseline_hit:
        return "RERANKER_IMPROVED"
    if baseline_hit and not experiment_hit:
        return "RERANKER_REGRESSION"
    if top_titles(baseline) != top_titles(experiment):
        return "NEEDS_MANUAL_REVIEW"
    return "RERANKER_NO_EFFECT"


def build_comparison(baseline_path: Path, experiment_path: Path) -> dict[str, Any]:
    baseline = load_json(baseline_path)
    experiment = load_json(experiment_path)
    validate_comparable_reports(baseline, experiment)
    baseline_map = result_map(baseline)
    experiment_map = result_map(experiment)
    case_ids = sorted(set(baseline_map) & set(experiment_map))
    comparisons = []
    for case_id in case_ids:
        base_result = baseline_map[case_id]
        exp_result = experiment_map[case_id]
        comparisons.append({
            "case_id": case_id,
            "question": exp_result.get("original_question"),
            "candidate_count": exp_result.get("candidate_count_after_dedup"),
            "baseline_top2": [summarize_doc(doc) for doc in top_docs(base_result)[:2]],
            "reranker_top2": [summarize_doc(doc) for doc in top_docs(exp_result)[:2]],
            "top2_changed": top_titles(base_result) != top_titles(exp_result),
            "classification": classify_case(base_result, exp_result),
            "bm25_added_to_top2": any("bm25" in (doc.get("retrieval_routes") or []) for doc in top_docs(exp_result)[:2]),
        })

    classifications = Counter(item["classification"] for item in comparisons)
    top1_delta = int(sum(1 for item in experiment_map.values() if title_hit(item, 1))) - int(
        sum(1 for item in baseline_map.values() if title_hit(item, 1))
    )
    top2_delta = int(sum(1 for item in experiment_map.values() if title_hit(item, 2))) - int(
        sum(1 for item in baseline_map.values() if title_hit(item, 2))
    )
    baseline_summary = baseline["summary"]
    experiment_summary = experiment["summary"]
    return {
        "status": "success",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "baseline_report": str(baseline_path),
        "experiment_report": str(experiment_path),
        "metrics": {
            "top1_title_weak_hit_delta": top1_delta,
            "top2_title_weak_hit_delta": top2_delta,
            "expected_answer_false_rejected_delta": (
                experiment_summary.get("expected_answer_false_rejected", 0)
                - baseline_summary.get("expected_answer_false_rejected", 0)
            ),
            "expected_no_answer_anchor_rejected_delta": (
                experiment_summary.get("expected_no_answer_anchor_rejected", 0)
                - baseline_summary.get("expected_no_answer_anchor_rejected", 0)
            ),
            "expected_no_answer_still_accepted_delta": (
                experiment_summary.get("expected_no_answer_not_rejected", 0)
                - baseline_summary.get("expected_no_answer_not_rejected", 0)
            ),
            "top2_changed_count": sum(1 for item in comparisons if item["top2_changed"]),
            "bm25_added_to_top2_count": sum(1 for item in comparisons if item["bm25_added_to_top2"]),
            "reranker_latency_avg_ms": experiment_summary.get("reranker_latency_avg_ms"),
            "reranker_latency_p95_ms": experiment_summary.get("reranker_latency_p95_ms"),
            "reranker_success_count": experiment_summary.get("reranker_success_count"),
            "reranker_failure_count": experiment_summary.get("reranker_failure_count"),
            "reranker_invalid_result_count": experiment_summary.get("reranker_invalid_result_count"),
        },
        "classification_counts": dict(classifications),
        "focus_cases": [item for item in comparisons if item["case_id"] in FOCUS_CASES],
        "case_comparisons": comparisons,
    }


def write_reports(comparison: dict[str, Any], json_path: Path, md_path: Path) -> None:
    json_path.write_text(json.dumps(comparison, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown(comparison), encoding="utf-8")


def render_markdown(comparison: dict[str, Any]) -> str:
    lines = [
        "# SiliconFlow Reranker A/B Comparison",
        "",
        f"- Generated at: `{comparison['generated_at']}`",
        f"- Baseline: `{comparison['baseline_report']}`",
        f"- Experiment: `{comparison['experiment_report']}`",
        "",
        "## Metrics",
        "",
    ]
    for key, value in comparison["metrics"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Classification Counts", ""])
    for key, value in comparison["classification_counts"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Focus Cases", ""])
    for item in comparison["focus_cases"]:
        lines.append(f"### {item['case_id']}")
        lines.append(f"- Question: {item['question']}")
        lines.append(f"- Candidate count: {item['candidate_count']}")
        lines.append(f"- Classification: `{item['classification']}`")
        lines.append(f"- Baseline Top2: {[doc['title'] for doc in item['baseline_top2']]}")
        lines.append(f"- Reranker Top2: {[doc['title'] for doc in item['reranker_top2']]}")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare BM25 baseline with SiliconFlow reranker experiment.")
    parser.add_argument("--baseline", default=str(BASELINE_REPORT))
    parser.add_argument("--experiment", default=str(EXPERIMENT_REPORT))
    parser.add_argument("--output-prefix", default="rag_siliconflow_reranker_v2_82_comparison")
    args = parser.parse_args()
    output_prefix = Path(args.output_prefix).name
    json_path = TESTDATA / f"{output_prefix}.json"
    md_path = TESTDATA / f"{output_prefix}.md"
    comparison = build_comparison(Path(args.baseline), Path(args.experiment))
    write_reports(comparison, json_path, md_path)
    print("SiliconFlow reranker comparison completed")
    print(f"metrics={comparison['metrics']}")
    print(f"classification_counts={comparison['classification_counts']}")
    print(f"json_report={json_path}")
    print(f"md_report={md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

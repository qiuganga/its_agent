from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
KNOWLEDGE_ROOT = SCRIPT_PATH.parents[1]
TESTDATA = KNOWLEDGE_ROOT / "testdata"

BASELINE_REPORT = TESTDATA / "rag_eval_report_v2_82_hsn_bm25_siliconflow_reranker.json"
ALIAS_REPORT = TESTDATA / "rag_eval_report_v2_82_hsn_bm25_siliconflow_reranker_alias_v2.json"
OUT_JSON = TESTDATA / "rag_alias_mapping_v2_82_comparison.json"
OUT_MD = TESTDATA / "rag_alias_mapping_v2_82_comparison.md"

ALIAS_PATTERNS = {
    "Windows 7": re.compile(r"\b(?:win7|windows\s*7)\b", re.IGNORECASE),
    "Windows XP": re.compile(r"\b(?:xp|windows\s*xp)\b", re.IGNORECASE),
    "打印机": re.compile(r"(?:\bprinter\b|打印机)", re.IGNORECASE),
}


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"report file not found: {path}")
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def result_map(report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(item["case_id"]): item for item in report.get("results", [])}


def top_docs(result: dict[str, Any]) -> list[dict[str, Any]]:
    return result.get("final_documents") or result.get("documents_before_threshold") or []


def summarize_doc(doc: dict[str, Any]) -> dict[str, Any]:
    return {
        "title": doc.get("title"),
        "source_id": doc.get("source_id"),
        "retrieval_route": doc.get("retrieval_route"),
        "retrieval_routes": doc.get("retrieval_routes") or [],
        "reranker_score": doc.get("reranker_score"),
        "final_rerank_score": doc.get("final_rerank_score"),
        "mmr_score": doc.get("mmr_score"),
        "anchor_evidence_status": doc.get("anchor_evidence_status"),
    }


def top_titles(result: dict[str, Any]) -> list[str]:
    return [str(doc.get("title") or "") for doc in top_docs(result)[:2]]


def top1_title(result: dict[str, Any]) -> str | None:
    titles = top_titles(result)
    return titles[0] if titles else None


def is_rejected(result: dict[str, Any]) -> bool:
    return bool(result.get("rejected_by_low_confidence") or result.get("rejected_by_anchor_evidence"))


def validate_comparable_reports(baseline: dict[str, Any], alias: dict[str, Any]) -> None:
    errors: list[str] = []
    baseline_summary = baseline.get("summary", {})
    alias_summary = alias.get("summary", {})
    baseline_settings = baseline.get("settings", {})
    alias_settings = alias.get("settings", {})

    if baseline_summary.get("total_cases") != 82 or alias_summary.get("total_cases") != 82:
        errors.append(
            f"total_cases must both be 82, got baseline={baseline_summary.get('total_cases')} "
            f"alias={alias_summary.get('total_cases')}"
        )
    if baseline.get("cases_file") != alias.get("cases_file"):
        errors.append(f"cases_file mismatch: {baseline.get('cases_file')} != {alias.get('cases_file')}")

    comparable_settings = [
        "collection_name",
        "RAG_BM25_MODE",
        "RAG_ANCHOR_EVIDENCE_MODE",
        "RAG_RERANKER_MODE",
        "RAG_RERANKER_PROVIDER",
        "RAG_RERANKER_MODEL",
        "RAG_MIN_RERANK_SCORE",
        "RAG_FINAL_TOP_K",
    ]
    for key in comparable_settings:
        if baseline_settings.get(key) != alias_settings.get(key):
            errors.append(f"{key} mismatch: {baseline_settings.get(key)} != {alias_settings.get(key)}")

    if baseline_settings.get("collection_name") != "its-knowledge-clean-v1":
        errors.append("baseline collection_name must be its-knowledge-clean-v1")
    if alias_settings.get("collection_name") != "its-knowledge-clean-v1":
        errors.append("alias collection_name must be its-knowledge-clean-v1")
    if baseline_summary.get("bm25_mode") != "experimental" or alias_summary.get("bm25_mode") != "experimental":
        errors.append("both reports must use bm25_mode=experimental")
    if baseline_summary.get("anchor_evidence_mode") != "hard-soft-negative":
        errors.append("baseline anchor_evidence_mode must be hard-soft-negative")
    if alias_summary.get("anchor_evidence_mode") != "hard-soft-negative":
        errors.append("alias anchor_evidence_mode must be hard-soft-negative")
    if baseline_summary.get("reranker_mode") != "experimental" or alias_summary.get("reranker_mode") != "experimental":
        errors.append("both reports must use reranker_mode=experimental")
    if baseline_summary.get("reranker_provider") != "siliconflow" or alias_summary.get("reranker_provider") != "siliconflow":
        errors.append("both reports must use reranker_provider=siliconflow")

    if errors:
        raise ValueError("; ".join(errors))


def alias_hits_for_case(result: dict[str, Any]) -> list[str]:
    text = " ".join(
        [
            str(result.get("original_question") or ""),
            str(result.get("normalized_question") or ""),
            " ".join(str(item) for item in result.get("query_variants") or []),
        ]
    )
    return [name for name, pattern in ALIAS_PATTERNS.items() if pattern.search(text)]


def alias_applied(baseline: dict[str, Any], alias: dict[str, Any]) -> bool:
    return str(baseline.get("normalized_question") or "") != str(alias.get("normalized_question") or "")


def classify_case(baseline: dict[str, Any], alias: dict[str, Any]) -> str:
    base_hit = bool(baseline.get("top2_title_weak_hit"))
    alias_hit = bool(alias.get("top2_title_weak_hit"))
    base_rejected = is_rejected(baseline)
    alias_rejected = is_rejected(alias)
    if (alias_hit and not base_hit) or (base_rejected and not alias_rejected and alias.get("expected_answerability") == "answerable"):
        return "ALIAS_IMPROVED"
    if (base_hit and not alias_hit) or (
        not base_rejected and alias_rejected and alias.get("expected_answerability") == "answerable"
    ):
        return "ALIAS_REGRESSION"
    if top_titles(baseline) != top_titles(alias) or base_rejected != alias_rejected:
        return "ALIAS_CHANGED_BUT_NEEDS_MANUAL_REVIEW"
    return "ALIAS_NO_EFFECT"


def latency_delta(baseline_summary: dict[str, Any], alias_summary: dict[str, Any], key: str) -> float | None:
    before = baseline_summary.get(key)
    after = alias_summary.get(key)
    if before is None or after is None:
        return None
    return round(float(after) - float(before), 4)


def build_comparison(baseline_path: Path = BASELINE_REPORT, alias_path: Path = ALIAS_REPORT) -> dict[str, Any]:
    baseline = load_json(baseline_path)
    alias = load_json(alias_path)
    validate_comparable_reports(baseline, alias)

    baseline_results = result_map(baseline)
    alias_results = result_map(alias)
    case_ids = sorted(set(baseline_results) & set(alias_results))
    if len(case_ids) != 82:
        raise ValueError(f"matched case count must be 82, got {len(case_ids)}")

    comparisons: list[dict[str, Any]] = []
    for case_id in case_ids:
        base = baseline_results[case_id]
        aliased = alias_results[case_id]
        alias_hit_names = alias_hits_for_case(aliased)
        comparison = {
            "case_id": case_id,
            "original_question": aliased.get("original_question"),
            "normalized_query_before": base.get("normalized_question"),
            "alias_query_after": aliased.get("normalized_question"),
            "alias_applied": alias_applied(base, aliased),
            "new_alias_hit_names": alias_hit_names,
            "new_alias_hit": bool(alias_hit_names),
            "baseline_top2": [summarize_doc(doc) for doc in top_docs(base)[:2]],
            "alias_v2_top2": [summarize_doc(doc) for doc in top_docs(aliased)[:2]],
            "top1_changed": top1_title(base) != top1_title(aliased),
            "top2_changed": top_titles(base) != top_titles(aliased),
            "top2_weak_hit_before": bool(base.get("top2_title_weak_hit")),
            "top2_weak_hit_after": bool(aliased.get("top2_title_weak_hit")),
            "weak_hit_improved": bool(aliased.get("top2_title_weak_hit")) and not bool(base.get("top2_title_weak_hit")),
            "false_rejection_changed": (
                base.get("expected_answerability") == "answerable"
                and is_rejected(base) != is_rejected(aliased)
            ),
            "no_answer_false_accept_changed": (
                base.get("expected_answerability") == "unanswerable"
                and is_rejected(base) != is_rejected(aliased)
            ),
            "retrieval_routes": sorted(
                {
                    route
                    for doc in top_docs(aliased)[:2]
                    for route in (doc.get("retrieval_routes") or [doc.get("retrieval_route")])
                    if route
                }
            ),
            "reranker_scores": [doc.get("reranker_score") for doc in top_docs(aliased)[:2]],
            "anchor_statuses": [doc.get("anchor_evidence_status") for doc in top_docs(aliased)[:2]],
        }
        comparison["classification"] = classify_case(base, aliased)
        comparisons.append(comparison)

    baseline_summary = baseline["summary"]
    alias_summary = alias["summary"]
    classifications = Counter(item["classification"] for item in comparisons)
    alias_focus_cases = [item for item in comparisons if item["new_alias_hit"]]

    metrics = {
        "top1_title_weak_hit_before": baseline_summary.get("top1_title_weak_hit_count"),
        "top1_title_weak_hit_after": alias_summary.get("top1_title_weak_hit_count"),
        "top1_title_weak_hit_delta": alias_summary.get("top1_title_weak_hit_count", 0)
        - baseline_summary.get("top1_title_weak_hit_count", 0),
        "top2_title_weak_hit_before": baseline_summary.get("top2_title_weak_hit_count"),
        "top2_title_weak_hit_after": alias_summary.get("top2_title_weak_hit_count"),
        "top2_title_weak_hit_delta": alias_summary.get("top2_title_weak_hit_count", 0)
        - baseline_summary.get("top2_title_weak_hit_count", 0),
        "expected_answer_false_rejected_before": baseline_summary.get("expected_answer_false_rejected"),
        "expected_answer_false_rejected_after": alias_summary.get("expected_answer_false_rejected"),
        "expected_answer_false_rejected_delta": alias_summary.get("expected_answer_false_rejected", 0)
        - baseline_summary.get("expected_answer_false_rejected", 0),
        "expected_no_answer_anchor_rejected_delta": alias_summary.get("expected_no_answer_anchor_rejected", 0)
        - baseline_summary.get("expected_no_answer_anchor_rejected", 0),
        "expected_no_answer_still_accepted_delta": alias_summary.get("expected_no_answer_not_rejected", 0)
        - baseline_summary.get("expected_no_answer_not_rejected", 0),
        "accepted_delta": alias_summary.get("accepted_count", 0) - baseline_summary.get("accepted_count", 0),
        "rejected_delta": alias_summary.get("total_rejected_count", 0) - baseline_summary.get("total_rejected_count", 0),
        "top1_changed_count": sum(1 for item in comparisons if item["top1_changed"]),
        "top2_changed_count": sum(1 for item in comparisons if item["top2_changed"]),
        "alias_applied_case_count": sum(1 for item in comparisons if item["alias_applied"]),
        "new_alias_hit_case_count": sum(1 for item in comparisons if item["new_alias_hit"]),
        "reranker_latency_avg_ms_before": baseline_summary.get("reranker_latency_avg_ms"),
        "reranker_latency_avg_ms_after": alias_summary.get("reranker_latency_avg_ms"),
        "reranker_latency_avg_ms_delta": latency_delta(baseline_summary, alias_summary, "reranker_latency_avg_ms"),
        "reranker_latency_p95_ms_before": baseline_summary.get("reranker_latency_p95_ms"),
        "reranker_latency_p95_ms_after": alias_summary.get("reranker_latency_p95_ms"),
        "reranker_latency_p95_ms_delta": latency_delta(baseline_summary, alias_summary, "reranker_latency_p95_ms"),
        "source_id_missing_before_rerank_delta": alias_summary.get("source_id_missing_before_rerank_total", 0)
        - baseline_summary.get("source_id_missing_before_rerank_total", 0),
    }

    return {
        "status": "success",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "baseline_report": str(baseline_path),
        "alias_report": str(alias_path),
        "metrics": metrics,
        "classification_counts": dict(sorted(classifications.items())),
        "improved_cases": [item for item in comparisons if item["classification"] == "ALIAS_IMPROVED"],
        "regression_cases": [item for item in comparisons if item["classification"] == "ALIAS_REGRESSION"],
        "manual_review_cases": [
            item for item in comparisons if item["classification"] == "ALIAS_CHANGED_BUT_NEEDS_MANUAL_REVIEW"
        ],
        "alias_focus_cases": alias_focus_cases,
        "comparisons": comparisons,
        "notes": [
            "This comparison only reads existing evaluation reports.",
            "It does not call /query, LLM, Embedding, Reranker, Chroma, or MCP.",
            "Weak title hit is an automatic weak label and still needs manual review.",
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    metrics = report["metrics"]
    lines = [
        "# Alias Mapping v2 A/B Comparison",
        "",
        f"- Baseline: `{report['baseline_report']}`",
        f"- Alias v2: `{report['alias_report']}`",
        "",
        "## Metrics",
        "",
        "| Metric | Before | After | Delta |",
        "| --- | ---: | ---: | ---: |",
        f"| Top1 weak hit | {metrics['top1_title_weak_hit_before']} | {metrics['top1_title_weak_hit_after']} | {metrics['top1_title_weak_hit_delta']} |",
        f"| Top2 weak hit | {metrics['top2_title_weak_hit_before']} | {metrics['top2_title_weak_hit_after']} | {metrics['top2_title_weak_hit_delta']} |",
        f"| False rejected answerable | {metrics['expected_answer_false_rejected_before']} | {metrics['expected_answer_false_rejected_after']} | {metrics['expected_answer_false_rejected_delta']} |",
        f"| Accepted count | - | - | {metrics['accepted_delta']} |",
        f"| Rejected count | - | - | {metrics['rejected_delta']} |",
        f"| Top1 changed cases | - | - | {metrics['top1_changed_count']} |",
        f"| Top2 changed cases | - | - | {metrics['top2_changed_count']} |",
        f"| Alias applied cases | - | - | {metrics['alias_applied_case_count']} |",
        f"| New alias hit cases | - | - | {metrics['new_alias_hit_case_count']} |",
        f"| Source id missing before rerank | - | - | {metrics['source_id_missing_before_rerank_delta']} |",
        "",
        "## Classification Counts",
        "",
    ]
    for key, value in report["classification_counts"].items():
        lines.append(f"- {key}: {value}")

    def section(title: str, items: list[dict[str, Any]]) -> None:
        lines.extend(["", f"## {title}", ""])
        if not items:
            lines.append("- None")
            return
        for item in items[:30]:
            lines.append(
                f"- {item['case_id']} | {item['classification']} | aliases={','.join(item['new_alias_hit_names']) or '-'} "
                f"| top2_changed={item['top2_changed']} | before={item['normalized_query_before']} | after={item['alias_query_after']}"
            )

    section("Improved Cases", report["improved_cases"])
    section("Regression Cases", report["regression_cases"])
    section("Changed But Needs Manual Review", report["manual_review_cases"])
    section("New Alias Focus Cases", report["alias_focus_cases"])

    lines.extend(["", "> This report does not change production retrieval logic."])
    return "\n".join(lines) + "\n"


def write_reports(report: dict[str, Any], out_json: Path = OUT_JSON, out_md: Path = OUT_MD) -> None:
    out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    out_md.write_text(render_markdown(report), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare baseline and Alias v2 RAG evaluation reports.")
    parser.add_argument("--baseline", type=Path, default=BASELINE_REPORT)
    parser.add_argument("--alias-report", type=Path, default=ALIAS_REPORT)
    parser.add_argument("--out-json", type=Path, default=OUT_JSON)
    parser.add_argument("--out-md", type=Path, default=OUT_MD)
    args = parser.parse_args()

    report = build_comparison(args.baseline, args.alias_report)
    write_reports(report, args.out_json, args.out_md)
    metrics = report["metrics"]
    print("Alias mapping report comparison completed")
    print(f"top1_delta={metrics['top1_title_weak_hit_delta']}")
    print(f"top2_delta={metrics['top2_title_weak_hit_delta']}")
    print(f"alias_applied={metrics['alias_applied_case_count']}")
    print(f"new_alias_hits={metrics['new_alias_hit_case_count']}")
    print(f"out_json={args.out_json}")
    print(f"out_md={args.out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

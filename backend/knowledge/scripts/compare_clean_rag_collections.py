from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

import chromadb


SCRIPT_PATH = Path(__file__).resolve()
KNOWLEDGE_ROOT = SCRIPT_PATH.parents[1]
REPO_ROOT = KNOWLEDGE_ROOT.parents[1]
if str(KNOWLEDGE_ROOT) not in sys.path:
    sys.path.insert(0, str(KNOWLEDGE_ROOT))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from config.settings import settings


TESTDATA = KNOWLEDGE_ROOT / "testdata"
MANIFEST_JSON = TESTDATA / "rag_cleaning_manifest.json"
REPORTS = {
    "old": TESTDATA / "rag_eval_report_old_collection_recheck.json",
    "clean": TESTDATA / "rag_eval_report_clean_v1.json",
    "clean_small_chunk": TESTDATA / "rag_eval_report_clean_chunk1000_v1.json",
}
COLLECTIONS = {
    "old": "its-knowledge",
    "clean": "its-knowledge-clean-v1",
    "clean_small_chunk": "its-knowledge-clean-chunk1000-v1",
}
OUT_JSON = TESTDATA / "rag_clean_collection_comparison.json"
OUT_MD = TESTDATA / "rag_clean_collection_comparison.md"
FOCUS_CASES = [
    "case_001",
    "case_002",
    "case_003",
    "case_005",
    "case_006",
    "case_009",
    "case_011",
    "case_012",
    "case_015",
    "case_018",
    "case_022",
    "case_023",
    "case_024",
]


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def result_map(report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {item["case_id"]: item for item in report.get("results", [])}


def collection_stats(collection_name: str) -> dict[str, Any]:
    client = chromadb.PersistentClient(path=settings.VECTOR_STORE_PATH)
    try:
        collection = client.get_collection(collection_name)
    except Exception as exc:
        return {"collection_name": collection_name, "exists": False, "error": str(exc)}
    count = int(collection.count())
    sample = collection.get(limit=min(20, count), include=["metadatas"]) if count else {"metadatas": []}
    metadatas = sample.get("metadatas", []) if isinstance(sample, dict) else []
    required = {
        "source_id",
        "source_path",
        "document_id",
        "chunk_id",
        "chunk_index",
        "title",
        "keywords",
        "source_type",
        "cleaning_version",
        "collection_experiment",
        "original_char_count",
        "cleaned_char_count",
        "effective_content_chars",
        "content_hash",
    }
    missing_count = 0
    for metadata in metadatas:
        if any(metadata is None or metadata.get(field) is None for field in required):
            missing_count += 1
    return {
        "collection_name": collection_name,
        "exists": True,
        "chunk_count": count,
        "sample_size": len(metadatas),
        "sample_metadata_complete_rate": round((len(metadatas) - missing_count) / len(metadatas), 4) if metadatas else None,
        "sample_metadata_missing_count": missing_count,
    }


def top_docs(result: dict[str, Any]) -> list[dict[str, Any]]:
    return result.get("final_documents") or result.get("documents_before_threshold") or []


def title_list(result: dict[str, Any]) -> list[str]:
    return [(doc.get("title") or "") for doc in top_docs(result)[:2]]


def score_list(result: dict[str, Any]) -> list[float | None]:
    return [to_float(doc.get("final_rerank_score")) for doc in top_docs(result)[:2]]


def to_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def low_effective_topk_stats(report: dict[str, Any], manifest: dict[str, Any] | None) -> dict[str, int]:
    count = 0
    unknown = 0
    manifest_by_source = {}
    if manifest:
        manifest_by_source = {
            item.get("source_id"): item
            for item in manifest.get("records", [])
            if item.get("source_id")
        }
    for result in report.get("results", []):
        for doc in top_docs(result):
            effective = doc.get("effective_content_chars")
            if effective is None:
                source_id = doc.get("source_id")
                manifest_record = manifest_by_source.get(source_id)
                effective = manifest_record.get("effective_content_chars") if manifest_record else None
            if isinstance(effective, (int, float)) and effective < 80:
                count += 1
            elif effective is None:
                unknown += 1
    return {"count": count, "unknown": unknown}


def missing_source_topk_count(report: dict[str, Any]) -> int:
    count = 0
    for result in report.get("results", []):
        for doc in top_docs(result):
            if not doc.get("source_id"):
                count += 1
    return count


def report_metrics(name: str, report: dict[str, Any], manifest: dict[str, Any] | None) -> dict[str, Any]:
    summary = report.get("summary", {})
    collection = report.get("settings", {}).get("collection_name") or COLLECTIONS[name]
    stats = collection_stats(collection)
    manifest_summary = manifest.get("summary", {}) if manifest and name != "old" else {}
    indexable_docs = manifest_summary.get("indexable_documents")
    skipped_docs = manifest_summary.get("skipped_documents")
    low_effective = low_effective_topk_stats(report, manifest)
    return {
        "collection_name": collection,
        "indexable_documents": indexable_docs,
        "skipped_documents": skipped_docs,
        "chunk_count": stats.get("chunk_count"),
        "average_chunks_per_document": round(stats.get("chunk_count", 0) / indexable_docs, 4)
        if indexable_docs else None,
        "metadata_complete_rate": stats.get("sample_metadata_complete_rate"),
        "top1_title_weak_hit_count": summary.get("top1_title_weak_hit_count"),
        "top2_title_weak_hit_count": summary.get("top2_title_weak_hit_count"),
        "expected_no_answer_not_rejected": summary.get("expected_no_answer_not_rejected"),
        "expected_no_answer_correctly_rejected": summary.get("expected_no_answer_correctly_rejected"),
        "low_effective_topk_count": low_effective["count"],
        "low_effective_topk_unknown_count": low_effective["unknown"],
        "missing_source_topk_count": missing_source_topk_count(report),
        "accepted_count": summary.get("accepted_count"),
        "low_confidence_rejected_count": summary.get("low_confidence_rejected_count"),
    }


def classify_case(old: dict[str, Any], clean: dict[str, Any], small: dict[str, Any]) -> str:
    old_hit = bool(old.get("top2_title_weak_hit"))
    clean_hit = bool(clean.get("top2_title_weak_hit"))
    small_hit = bool(small.get("top2_title_weak_hit"))
    if (clean_hit or small_hit) and not old_hit:
        return "positive"
    if old_hit and not clean_hit and not small_hit:
        return "negative"
    if title_list(old) == title_list(clean) == title_list(small):
        return "unchanged"
    return "requires_manual_review"


def compare_cases(reports: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    maps = {name: result_map(report) for name, report in reports.items()}
    case_ids = sorted(set(maps["old"]) & set(maps["clean"]) & set(maps["clean_small_chunk"]))
    comparisons = []
    for case_id in case_ids:
        old = maps["old"][case_id]
        clean = maps["clean"][case_id]
        small = maps["clean_small_chunk"][case_id]
        comparisons.append({
            "case_id": case_id,
            "question": old.get("original_question"),
            "category": old.get("category"),
            "classification": classify_case(old, clean, small),
            "old": summarize_case_result(old),
            "clean": summarize_case_result(clean),
            "clean_small_chunk": summarize_case_result(small),
        })
    return comparisons


def summarize_case_result(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "normalized_question": result.get("normalized_question"),
        "dual_retrieval_enabled": result.get("dual_retrieval_enabled"),
        "candidate_count_before_dedup": result.get("candidate_count_before_dedup"),
        "candidate_count_after_dedup": result.get("candidate_count_after_dedup"),
        "top_titles": title_list(result),
        "top_scores": score_list(result),
        "top1_title_weak_hit": result.get("top1_title_weak_hit"),
        "top2_title_weak_hit": result.get("top2_title_weak_hit"),
        "rejected_by_low_confidence": result.get("rejected_by_low_confidence"),
    }


def build_comparison() -> dict[str, Any]:
    reports = {name: load_json(path) for name, path in REPORTS.items()}
    manifest = load_json(MANIFEST_JSON) if MANIFEST_JSON.exists() else None
    case_comparisons = compare_cases(reports)
    classification_counts = Counter(item["classification"] for item in case_comparisons)
    return {
        "status": "success",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "reports": {name: str(path) for name, path in REPORTS.items()},
        "metrics": {name: report_metrics(name, report, manifest) for name, report in reports.items()},
        "classification_counts": dict(classification_counts),
        "focus_cases": [item for item in case_comparisons if item["case_id"] in FOCUS_CASES],
        "case_comparisons": case_comparisons,
        "notes": [
            "expected_title_contains is a weak title label, not a ground-truth relevance score.",
            "No-answer not rejected is recorded but not counted as cleaning failure because rejection strategy is unchanged.",
        ],
    }


def write_reports(comparison: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(comparison, ensure_ascii=False, indent=2), encoding="utf-8")
    OUT_MD.write_text(render_markdown(comparison), encoding="utf-8")


def render_markdown(comparison: dict[str, Any]) -> str:
    lines = [
        "# RAG Clean Collection A/B/C Comparison",
        "",
        f"- Generated at: `{comparison['generated_at']}`",
        "",
        "## Metrics",
        "",
        "| Group | Collection | Indexable Docs | Skipped Docs | Chunks | Avg Chunks/Doc | Metadata Rate | Top1 Hit | Top2 Hit | No-answer Passed | No-answer Rejected |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name, metrics in comparison["metrics"].items():
        lines.append(
            f"| {name} | {metrics['collection_name']} | {metrics['indexable_documents']} | "
            f"{metrics['skipped_documents']} | {metrics['chunk_count']} | {metrics['average_chunks_per_document']} | "
            f"{metrics['metadata_complete_rate']} | {metrics['top1_title_weak_hit_count']} | "
            f"{metrics['top2_title_weak_hit_count']} | {metrics['expected_no_answer_not_rejected']} | "
            f"{metrics['expected_no_answer_correctly_rejected']} |"
        )
    lines.extend(["", "## Classification Counts", ""])
    for key, value in comparison["classification_counts"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Focus Cases", ""])
    for item in comparison["focus_cases"]:
        lines.append(f"### {item['case_id']}")
        lines.append(f"- Question: {item['question']}")
        lines.append(f"- Classification: `{item['classification']}`")
        for group in ("old", "clean", "clean_small_chunk"):
            data = item[group]
            lines.append(
                f"- {group}: top={data['top_titles']} scores={data['top_scores']} "
                f"top2_hit={data['top2_title_weak_hit']} candidates={data['candidate_count_after_dedup']}"
            )
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    comparison = build_comparison()
    write_reports(comparison)
    print("RAG clean collection comparison completed")
    print(f"classification_counts={comparison['classification_counts']}")
    print(f"json_report={OUT_JSON}")
    print(f"md_report={OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

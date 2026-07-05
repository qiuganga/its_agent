from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable


SCRIPT_PATH = Path(__file__).resolve()
KNOWLEDGE_ROOT = SCRIPT_PATH.parents[1]
REPO_ROOT = KNOWLEDGE_ROOT.parents[1]
if str(KNOWLEDGE_ROOT) not in sys.path:
    sys.path.insert(0, str(KNOWLEDGE_ROOT))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from config.settings import settings
from services.query_normalization_service import query_normalization_service
from services.retrieval_service import RetrievalService


CASES_PATH = KNOWLEDGE_ROOT / "testdata" / "rag_eval_cases.json"
REPORT_JSON_PATH = KNOWLEDGE_ROOT / "testdata" / "rag_diagnosis_report.json"
REPORT_MD_PATH = KNOWLEDGE_ROOT / "testdata" / "rag_diagnosis_report.md"
SUMMARY_LIMIT = 300

GENERIC_ANCHOR_STOPWORDS = {
    "电脑",
    "系统",
    "问题",
    "怎么办",
    "处理",
    "异常",
    "无法",
    "不能",
    "怎么",
    "什么",
    "解决",
    "故障",
    "情况",
    "相关",
    "使用",
    "进行",
    "出现",
}

ENGLISH_ANCHOR_ALLOWLIST = {
    "Windows",
    "BIOS",
    "Bluetooth",
    "Wi-Fi",
    "WiFi",
    "Excel",
    "Word",
    "Outlook",
    "PowerPoint",
    "IE",
    "USB",
}


@dataclass(frozen=True)
class QueryStage:
    query: str
    is_normalized_query: bool
    vector_candidates: list[Any]
    title_candidates: list[Any]
    merged_candidates: list[Any]
    reranked_documents: list[Any]


def load_cases() -> list[dict[str, Any]]:
    with CASES_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def resource_status() -> dict[str, Any]:
    crawl_dir = KNOWLEDGE_ROOT / "data" / "crawl"
    chroma_dir = KNOWLEDGE_ROOT / "chroma_kb"
    env_path = KNOWLEDGE_ROOT / ".env"
    return {
        "crawl_dir_exists": crawl_dir.exists(),
        "crawl_markdown_count": len(list(crawl_dir.rglob("*.md"))) if crawl_dir.exists() else 0,
        "chroma_dir_exists": chroma_dir.exists(),
        "chroma_file_count": len([p for p in chroma_dir.rglob("*") if p.is_file()]) if chroma_dir.exists() else 0,
        "env_exists": env_path.exists(),
    }


def normalize_question(original_question: str) -> tuple[str, list[str]]:
    normalized_question = query_normalization_service.normalize(original_question)
    variants: list[str] = []
    seen = set()
    for query in (original_question, normalized_question):
        cleaned = re.sub(r"\s+", " ", (query or "").strip())
        if cleaned and cleaned not in seen:
            variants.append(cleaned)
            seen.add(cleaned)
    return normalized_question, variants


def collect_query_stage(service: RetrievalService, query: str, original_question: str) -> QueryStage:
    vector_candidates = service._search_based_vector(query)
    title_candidates = service._search_based_title(query)
    is_normalized_query = query != original_question
    for document in vector_candidates + title_candidates:
        document.metadata = dict(document.metadata or {})
        document.metadata["matched_by_normalized_query"] = is_normalized_query

    merged_candidates = service._deduplicate(vector_candidates + title_candidates)
    reranked_documents = service.rerank_candidates(original_question, list(merged_candidates))
    return QueryStage(
        query=query,
        is_normalized_query=is_normalized_query,
        vector_candidates=vector_candidates,
        title_candidates=title_candidates,
        merged_candidates=merged_candidates,
        reranked_documents=reranked_documents,
    )


def diagnose_case(service: RetrievalService, case: dict[str, Any], show_content: bool = False) -> dict[str, Any]:
    original_question = case["question"].strip()
    normalized_question, query_variants = normalize_question(original_question)
    stages = [collect_query_stage(service, query, original_question) for query in query_variants]

    all_candidates = []
    for stage in stages:
        all_candidates.extend(stage.vector_candidates)
        all_candidates.extend(stage.title_candidates)

    merged_candidates = service._deduplicate(all_candidates)
    final_documents_before_threshold = service.rerank_candidates(original_question, list(merged_candidates))
    top_score = max(
        (to_float_or_none(doc.metadata.get("final_rerank_score")) or 0.0 for doc in final_documents_before_threshold),
        default=None,
    )
    rejected_by_low_confidence = top_score is None or top_score < settings.RAG_MIN_RERANK_SCORE
    final_documents = [] if rejected_by_low_confidence else final_documents_before_threshold
    anchor_terms = extract_anchor_terms(original_question)
    expected_title_contains = case.get("expected_title_contains") or []

    stage_records = [
        {
            "query": stage.query,
            "is_normalized_query": stage.is_normalized_query,
            "vector_candidate_count": len(stage.vector_candidates),
            "title_candidate_count": len(stage.title_candidates),
            "merged_dedup_candidate_count": len(stage.merged_candidates),
            "reranked_topk": documents_to_records(
                stage.reranked_documents,
                anchor_terms=anchor_terms,
                expected_title_contains=expected_title_contains,
                show_content=show_content,
            ),
            "vector_candidates": documents_to_records(
                stage.vector_candidates,
                anchor_terms=anchor_terms,
                expected_title_contains=expected_title_contains,
                show_content=show_content,
            ),
            "title_candidates": documents_to_records(
                stage.title_candidates,
                anchor_terms=anchor_terms,
                expected_title_contains=expected_title_contains,
                show_content=show_content,
            ),
        }
        for stage in stages
    ]
    final_records = documents_to_records(
        final_documents,
        anchor_terms=anchor_terms,
        expected_title_contains=expected_title_contains,
        show_content=show_content,
    )
    pre_threshold_records = documents_to_records(
        final_documents_before_threshold,
        anchor_terms=anchor_terms,
        expected_title_contains=expected_title_contains,
        show_content=show_content,
    )
    classification = classify_case(
        case=case,
        stage_records=stage_records,
        final_records=final_records,
        pre_threshold_records=pre_threshold_records,
        rejected_by_low_confidence=rejected_by_low_confidence,
    )
    return {
        "id": case.get("id"),
        "question": case.get("question"),
        "expected_title_contains": expected_title_contains,
        "expected_keywords": case.get("expected_keywords") or [],
        "category": case.get("category") or "",
        "expected_no_answer": bool(case.get("expected_no_answer")),
        "original_question": original_question,
        "normalized_question": normalized_question,
        "query_variants": query_variants,
        "dual_retrieval_enabled": len(query_variants) > 1,
        "vector_candidate_count": sum(stage["vector_candidate_count"] for stage in stage_records),
        "title_candidate_count": sum(stage["title_candidate_count"] for stage in stage_records),
        "merged_dedup_candidate_count": len(merged_candidates),
        "top_score": top_score,
        "rejected_by_low_confidence": rejected_by_low_confidence,
        "final_topk_count": len(final_records),
        "anchor_terms": anchor_terms,
        "query_stages": stage_records,
        "final_topk": final_records,
        "final_topk_before_threshold": pre_threshold_records,
        "classification": classification,
    }


def documents_to_records(
    documents: Iterable[Any],
    *,
    anchor_terms: list[str],
    expected_title_contains: list[str],
    show_content: bool,
) -> list[dict[str, Any]]:
    return [
        document_to_record(
            document,
            fallback_rank=index,
            anchor_terms=anchor_terms,
            expected_title_contains=expected_title_contains,
            show_content=show_content,
        )
        for index, document in enumerate(documents, start=1)
    ]


def document_to_record(
    document: Any,
    *,
    fallback_rank: int,
    anchor_terms: list[str],
    expected_title_contains: list[str],
    show_content: bool,
) -> dict[str, Any]:
    metadata = dict(getattr(document, "metadata", None) or {})
    content = getattr(document, "page_content", "") or ""
    title = metadata.get("title") or ""
    evidence = anchor_evidence_for_text(anchor_terms, f"{title}\n{content}")
    record = {
        "rank": metadata.get("final_rank") or metadata.get("rank") or fallback_rank,
        "title": title,
        "source_id": metadata.get("source_id"),
        "document_id": metadata.get("document_id"),
        "chunk_index": metadata.get("chunk_index"),
        "retrieval_route": metadata.get("retrieval_route"),
        "chroma_distance": to_float_or_none(metadata.get("chroma_distance")),
        "title_rough_score": to_float_or_none(metadata.get("title_rough_score") or metadata.get("roughing_score")),
        "title_semantic_score": to_float_or_none(metadata.get("title_semantic_score") or metadata.get("sim_score")),
        "title_final_score": to_float_or_none(metadata.get("title_final_score") or metadata.get("final_score")),
        "final_rerank_score": to_float_or_none(metadata.get("final_rerank_score")),
        "mmr_score": to_float_or_none(metadata.get("mmr_score")),
        "matched_by_normalized_query": bool(metadata.get("matched_by_normalized_query")),
        "expected_title_hit": title_has_expected_term(title, expected_title_contains),
        "anchor_terms": anchor_terms,
        "matched_anchor_terms": evidence["matched_anchor_terms"],
        "anchor_coverage_ratio": evidence["anchor_coverage_ratio"],
        "anchor_evidence_status": evidence["anchor_evidence_status"],
        "content_summary": summarize_content(content, show_content=show_content),
    }
    return record


def extract_anchor_terms(text: str) -> list[str]:
    if not text:
        return []

    anchors: list[str] = []
    seen = set()

    patterns = [
        r"\b0x[0-9A-Fa-f]{6,}\b",
        r"\b[A-Z]\d{3,}\b",
        r"\b(?:ThinkPad\s+X\d|K\d{3,}|A\d{4,})\b",
        r"\b(?:Windows|BIOS|Bluetooth|Wi-?Fi|Excel|Word|Outlook|PowerPoint|IE|USB)\b",
    ]
    for pattern in patterns:
        for match in re.findall(pattern, text, flags=re.IGNORECASE):
            add_anchor(anchors, seen, canonical_anchor(match))

    for allowed in ENGLISH_ANCHOR_ALLOWLIST:
        if re.search(rf"\b{re.escape(allowed)}\b", text, flags=re.IGNORECASE):
            add_anchor(anchors, seen, allowed)

    for term in re.findall(r"[\u4e00-\u9fff]{4,}", text):
        cleaned = strip_generic_edges(term)
        if cleaned and cleaned not in GENERIC_ANCHOR_STOPWORDS:
            add_anchor(anchors, seen, cleaned)

    return anchors


def canonical_anchor(term: str) -> str:
    cleaned = re.sub(r"\s+", " ", term.strip())
    if re.fullmatch(r"0x[0-9a-f]+", cleaned, flags=re.IGNORECASE):
        return cleaned.upper().replace("X", "x")
    if cleaned.lower() in {"wifi", "wi-fi"}:
        return "Wi-Fi"
    return cleaned


def add_anchor(anchors: list[str], seen: set[str], term: str) -> None:
    if not term:
        return
    key = term.lower()
    if key in seen:
        return
    seen.add(key)
    anchors.append(term)


def strip_generic_edges(term: str) -> str:
    cleaned = term.strip()
    changed = True
    while changed:
        changed = False
        for generic in sorted(GENERIC_ANCHOR_STOPWORDS, key=len, reverse=True):
            if cleaned.startswith(generic) and len(cleaned) - len(generic) >= 4:
                cleaned = cleaned[len(generic):]
                changed = True
            if cleaned.endswith(generic) and len(cleaned) - len(generic) >= 4:
                cleaned = cleaned[:-len(generic)]
                changed = True
    return cleaned


def anchor_evidence_for_text(anchor_terms: list[str], text: str) -> dict[str, Any]:
    if not anchor_terms:
        return {
            "matched_anchor_terms": [],
            "anchor_coverage_ratio": None,
            "anchor_evidence_status": "NO_STRONG_ANCHOR",
        }

    lowered = (text or "").lower()
    matched = [term for term in anchor_terms if term.lower() in lowered]
    coverage = len(matched) / len(anchor_terms)
    if len(matched) == len(anchor_terms):
        status = "FULL_ANCHOR_EVIDENCE"
    elif matched:
        status = "PARTIAL_ANCHOR_EVIDENCE"
    else:
        status = "NO_ANCHOR_EVIDENCE"
    return {
        "matched_anchor_terms": matched,
        "anchor_coverage_ratio": round(coverage, 4),
        "anchor_evidence_status": status,
    }


def summarize_content(content: str, *, show_content: bool, limit: int = SUMMARY_LIMIT) -> str:
    normalized = re.sub(r"\s+", " ", (content or "")).strip()
    if show_content:
        return normalized
    if len(normalized) <= limit:
        return normalized
    return normalized[:limit].rstrip() + "..."


def classify_case(
    *,
    case: dict[str, Any],
    stage_records: list[dict[str, Any]],
    final_records: list[dict[str, Any]],
    pre_threshold_records: list[dict[str, Any]],
    rejected_by_low_confidence: bool,
) -> dict[str, bool]:
    expected_no_answer = bool(case.get("expected_no_answer"))
    expected_terms = case.get("expected_title_contains") or []
    expected_in_candidates = any(
        record["expected_title_hit"]
        for stage in stage_records
        for key in ("vector_candidates", "title_candidates", "reranked_topk")
        for record in stage.get(key, [])
    )
    expected_in_final = any(record["expected_title_hit"] for record in final_records)
    any_final_anchor_missing = any(
        record["anchor_evidence_status"] in {"NO_ANCHOR_EVIDENCE", "PARTIAL_ANCHOR_EVIDENCE"}
        for record in final_records
    )

    flags = {
        "likely_no_knowledge": False,
        "candidate_recall_problem": False,
        "rerank_problem": False,
        "chunk_quality_problem": False,
        "likely_false_positive": False,
        "requires_manual_review": True,
    }

    if expected_no_answer:
        if final_records:
            flags["likely_false_positive"] = True
            flags["requires_manual_review"] = True
        else:
            flags["likely_no_knowledge"] = True
            flags["requires_manual_review"] = False
        return flags

    if not expected_terms:
        flags["requires_manual_review"] = True
        return flags

    if rejected_by_low_confidence and not pre_threshold_records:
        flags["candidate_recall_problem"] = True
        flags["requires_manual_review"] = True
        return flags

    if not expected_in_candidates:
        flags["candidate_recall_problem"] = True
        flags["requires_manual_review"] = True
        return flags

    if expected_in_candidates and not expected_in_final:
        flags["rerank_problem"] = True
        flags["requires_manual_review"] = True
        return flags

    if expected_in_final and any_final_anchor_missing:
        flags["chunk_quality_problem"] = True
        flags["requires_manual_review"] = True
        return flags

    flags["requires_manual_review"] = False
    return flags


def title_has_expected_term(title: str, expected_terms: list[str]) -> bool:
    return bool(expected_terms and any(term and term in (title or "") for term in expected_terms))


def to_float_or_none(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def get_collection_count(service: RetrievalService) -> int | None:
    try:
        collection = service.chroma_vector._collection()
        if collection is None:
            return None
        return int(collection.count())
    except Exception:
        return None


def build_report(case_results: list[dict[str, Any]], resources: dict[str, Any], collection_count: int | None) -> dict[str, Any]:
    classification_counts = Counter()
    for result in case_results:
        for name, enabled in result["classification"].items():
            if enabled:
                classification_counts[name] += 1

    suspicious_cases = sorted(
        case_results,
        key=lambda item: suspicious_score(item),
        reverse=True,
    )[:10]
    correct_loss = correct_loss_statistics(case_results)
    return {
        "status": "success",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "resources": resources,
        "collection_count": collection_count,
        "settings": {
            "RAG_VECTOR_CANDIDATE_TOP_K": settings.RAG_VECTOR_CANDIDATE_TOP_K,
            "RAG_TITLE_CANDIDATE_TOP_K": settings.RAG_TITLE_CANDIDATE_TOP_K,
            "RAG_FINAL_TOP_K": settings.RAG_FINAL_TOP_K,
            "RAG_MIN_RERANK_SCORE": settings.RAG_MIN_RERANK_SCORE,
            "RAG_MMR_LAMBDA": settings.RAG_MMR_LAMBDA,
            "RAG_MAX_CHUNKS_PER_DOCUMENT": settings.RAG_MAX_CHUNKS_PER_DOCUMENT,
        },
        "summary": {
            "total_cases": len(case_results),
            "dual_retrieval_count": sum(1 for item in case_results if item["dual_retrieval_enabled"]),
            "single_retrieval_count": sum(1 for item in case_results if not item["dual_retrieval_enabled"]),
            "low_confidence_rejected_count": sum(1 for item in case_results if item["rejected_by_low_confidence"]),
            "accepted_count": sum(1 for item in case_results if not item["rejected_by_low_confidence"]),
            "classification_counts": dict(classification_counts),
            "correct_loss_statistics": correct_loss,
        },
        "suspicious_cases": [
            {
                "id": item["id"],
                "question": item["question"],
                "top_score": item["top_score"],
                "classification": item["classification"],
                "top_titles": [doc["title"] for doc in item["final_topk_before_threshold"][:2]],
            }
            for item in suspicious_cases
        ],
        "results": case_results,
        "notes": [
            "This diagnosis does not call the answer LLM or /query endpoint.",
            "content_summary is truncated by default. Use --show-content only for manual inspection.",
            "Automatic classification is conservative and does not replace manual relevance review.",
        ],
    }


def suspicious_score(item: dict[str, Any]) -> int:
    score = 0
    classification = item["classification"]
    if classification.get("likely_false_positive"):
        score += 50
    if classification.get("candidate_recall_problem"):
        score += 40
    if classification.get("rerank_problem"):
        score += 35
    if classification.get("chunk_quality_problem"):
        score += 25
    if classification.get("requires_manual_review"):
        score += 10
    if item.get("expected_no_answer") and not item.get("rejected_by_low_confidence"):
        score += 30
    return score


def correct_loss_statistics(case_results: list[dict[str, Any]]) -> dict[str, int]:
    stats = Counter({
        "knowledge_missing": 0,
        "candidate_recall_failed": 0,
        "rerank_failed": 0,
        "chunk_quality_problem": 0,
        "requires_manual_review": 0,
    })
    for item in case_results:
        flags = item["classification"]
        if flags.get("likely_no_knowledge"):
            stats["knowledge_missing"] += 1
        if flags.get("candidate_recall_problem"):
            stats["candidate_recall_failed"] += 1
        if flags.get("rerank_problem"):
            stats["rerank_failed"] += 1
        if flags.get("chunk_quality_problem"):
            stats["chunk_quality_problem"] += 1
        if flags.get("requires_manual_review"):
            stats["requires_manual_review"] += 1
    return dict(stats)


def write_reports(report: dict[str, Any]) -> None:
    REPORT_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    with REPORT_JSON_PATH.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)
    with REPORT_MD_PATH.open("w", encoding="utf-8") as handle:
        handle.write(render_markdown(report))


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# RAG Retrieval Diagnosis Report",
        "",
        f"- Status: `{report.get('status')}`",
        f"- Generated at: `{report.get('generated_at', '')}`",
    ]
    if report.get("status") != "success":
        lines.extend([
            f"- Failure type: `{report.get('failure_type')}`",
            f"- Failure message: `{report.get('failure_message')}`",
        ])
        return "\n".join(lines)

    summary = report["summary"]
    lines.extend([
        "",
        "## Summary",
        "",
        f"- Total cases: {summary['total_cases']}",
        f"- Dual retrieval count: {summary['dual_retrieval_count']}",
        f"- Single retrieval count: {summary['single_retrieval_count']}",
        f"- Accepted count: {summary['accepted_count']}",
        f"- Low-confidence rejected count: {summary['low_confidence_rejected_count']}",
        f"- Classification counts: {summary['classification_counts']}",
        f"- Correct loss statistics: {summary['correct_loss_statistics']}",
        "",
        "## No-answer Cases",
        "",
    ])
    for item in [case for case in report["results"] if case["expected_no_answer"]]:
        lines.append(f"### {item['id']}")
        lines.append(f"- Question: {item['question']}")
        lines.append(f"- Rejected by low confidence: {item['rejected_by_low_confidence']}")
        lines.append(f"- Top score: {item['top_score']}")
        lines.append(f"- Classification: {item['classification']}")
        for doc in item["final_topk_before_threshold"][:2]:
            lines.append(
                f"  - {doc['title']} | score={doc['final_rerank_score']} | "
                f"anchor={doc['anchor_evidence_status']} | matched={doc['matched_anchor_terms']}"
            )
        lines.append("")

    lines.extend([
        "## Top Suspicious Cases",
        "",
    ])
    for item in report["suspicious_cases"][:10]:
        lines.append(
            f"- {item['id']} | score={item['top_score']} | titles={item['top_titles']} | "
            f"classification={item['classification']}"
        )

    lines.extend([
        "",
        "## Case Details",
        "",
    ])
    for item in report["results"]:
        lines.append(f"### {item['id']}")
        lines.append(f"- Original: {item['original_question']}")
        lines.append(f"- Normalized: {item['normalized_question']}")
        lines.append(f"- Dual retrieval: {item['dual_retrieval_enabled']}")
        lines.append(
            f"- Candidates: vector={item['vector_candidate_count']}, "
            f"title={item['title_candidate_count']}, dedup={item['merged_dedup_candidate_count']}"
        )
        lines.append(f"- Classification: {item['classification']}")
        lines.append("- Final TopK before threshold:")
        for doc in item["final_topk_before_threshold"][:2]:
            lines.append(
                f"  - {doc['title']} | source={doc['source_id']} | route={doc['retrieval_route']} | "
                f"distance={doc['chroma_distance']} | rerank={doc['final_rerank_score']} | "
                f"mmr={doc['mmr_score']} | anchor={doc['anchor_evidence_status']} | "
                f"expected_title_hit={doc['expected_title_hit']}"
            )
            lines.append(f"    Summary: {doc['content_summary']}")
        lines.append("")

    lines.extend([
        "## Recommended Next Steps",
        "",
        "1. Add anchor-based rejection or down-ranking for expected no-answer style queries.",
        "2. Manually inspect candidate recall failures before changing thresholds.",
        "3. Improve chunk boundaries for cases where title is correct but anchor evidence is partial.",
        "4. Consider increasing candidate pools only if correct documents are absent from candidates.",
        "5. Consider a stronger Cross-Encoder reranker if correct candidates enter the pool but lose final TopK.",
    ])
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Diagnose RAG retrieval stage loss without calling answer LLM.")
    parser.add_argument("--case-id", help="Run one case id from rag_eval_cases.json.")
    parser.add_argument("--show-content", action="store_true", help="Include full retrieved content in report records.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    resources = resource_status()
    missing = []
    if not resources["crawl_dir_exists"] or resources["crawl_markdown_count"] == 0:
        missing.append("Markdown knowledge base is missing or empty")
    if not resources["chroma_dir_exists"] or resources["chroma_file_count"] == 0:
        missing.append("Chroma vector store is missing or empty")
    if not resources["env_exists"]:
        missing.append(".env is missing")
    if missing:
        report = {
            "status": "failed",
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "failure_type": "resource_missing",
            "failure_message": "; ".join(missing),
            "resources": resources,
        }
        write_reports(report)
        print(report["failure_message"])
        return 2

    try:
        cases = load_cases()
        if args.case_id:
            cases = [case for case in cases if case.get("id") == args.case_id]
            if not cases:
                raise ValueError(f"case id not found: {args.case_id}")

        service = RetrievalService()
        collection_count = get_collection_count(service)
        if collection_count == 0:
            raise RuntimeError("Chroma collection is empty")

        results = [diagnose_case(service, case, show_content=args.show_content) for case in cases]
        report = build_report(results, resources, collection_count)
    except Exception as exc:
        report = {
            "status": "failed",
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "failure_type": classify_exception(exc),
            "failure_message": str(exc),
            "resources": resources,
        }
        write_reports(report)
        print(f"RAG diagnosis failed: {report['failure_type']} - {report['failure_message']}")
        return 2

    write_reports(report)
    summary = report["summary"]
    print("RAG diagnosis completed")
    print(f"cases={summary['total_cases']}")
    print(f"dual={summary['dual_retrieval_count']} single={summary['single_retrieval_count']}")
    print(f"accepted={summary['accepted_count']} rejected={summary['low_confidence_rejected_count']}")
    print(f"classification_counts={summary['classification_counts']}")
    print(f"json_report={REPORT_JSON_PATH}")
    print(f"md_report={REPORT_MD_PATH}")
    return 0


def classify_exception(exc: Exception) -> str:
    message = str(exc).lower()
    if "no module named" in message or "modulenotfounderror" in message:
        return "dependency_or_import_error"
    if "api" in message and ("key" in message or "token" in message):
        return "embedding_api_config_missing"
    if "insufficient" in message or "balance" in message or "quota" in message or "403" in message:
        return "embedding_api_permission_or_balance_error"
    if "connection" in message or "timeout" in message or "network" in message:
        return "embedding_api_network_unavailable"
    if "chroma" in message:
        return "chroma_runtime_error"
    return "other_exception"


if __name__ == "__main__":
    raise SystemExit(main())

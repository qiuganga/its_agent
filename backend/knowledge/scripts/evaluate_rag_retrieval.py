from __future__ import annotations

import json
import os
import statistics
import sys
import traceback
import argparse
from collections import Counter
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

from config.settings import settings
from repositories.vector_store_repository import VectorStoreRepository
from services.anchor_evidence_service import (
    ANCHOR_TYPE_HARD,
    ANCHOR_TYPE_NEGATIVE,
    ANCHOR_TYPE_SOFT,
    extract_anchors,
    extract_strong_anchors,
)
from services.query_normalization_service import query_normalization_service
from services.retrieval_service import RetrievalService


CASES_PATH = KNOWLEDGE_ROOT / "testdata" / "rag_eval_cases.json"
REPORT_JSON_PATH = KNOWLEDGE_ROOT / "testdata" / "rag_eval_report.json"
REPORT_MD_PATH = KNOWLEDGE_ROOT / "testdata" / "rag_eval_report.md"


def report_paths(output_prefix: str | None) -> tuple[Path, Path]:
    if not output_prefix:
        return REPORT_JSON_PATH, REPORT_MD_PATH
    safe_prefix = Path(output_prefix).name
    return (
        KNOWLEDGE_ROOT / "testdata" / f"{safe_prefix}.json",
        KNOWLEDGE_ROOT / "testdata" / f"{safe_prefix}.md",
    )


def load_cases(cases_file: str | Path | None = None) -> list[dict[str, Any]]:
    path = Path(cases_file) if cases_file else CASES_PATH
    with path.open("r", encoding="utf-8") as handle:
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


def get_collection_count(service: RetrievalService) -> int | None:
    try:
        collection = service.chroma_vector._collection()
        if collection is None:
            return None
        return int(collection.count())
    except Exception:
        return None


def build_variants(original_question: str) -> tuple[str, list[str], bool]:
    normalized_question = query_normalization_service.normalize(original_question)
    variants = [original_question]
    if normalized_question and normalized_question != original_question:
        variants.append(normalized_question)
    return normalized_question, variants, len(variants) > 1


def candidate_key(document) -> Any:
    metadata = document.metadata or {}
    return metadata.get("chunk_id") or (
        metadata.get("document_id"),
        metadata.get("source_id"),
        metadata.get("chunk_index"),
        metadata.get("title"),
    )


def evaluate_variant_set(
    service: RetrievalService,
    original_question: str,
    query_variants: list[str],
    *,
    use_reranker: bool = True,
) -> dict[str, Any]:
    all_candidates = []
    for query in query_variants:
        all_candidates.extend(service.retrieve_candidates(query, original_question=original_question))

    route_counts = Counter((doc.metadata or {}).get("retrieval_route") for doc in all_candidates)
    vector_keys = {candidate_key(doc) for doc in all_candidates if (doc.metadata or {}).get("retrieval_route") == "vector"}
    title_keys = {candidate_key(doc) for doc in all_candidates if (doc.metadata or {}).get("retrieval_route") == "title"}
    bm25_keys = {candidate_key(doc) for doc in all_candidates if (doc.metadata or {}).get("retrieval_route") == "bm25"}
    unique_candidates = service._deduplicate(all_candidates)
    unique_route_counts = Counter()
    for doc in unique_candidates:
        metadata = doc.metadata or {}
        routes = metadata.get("retrieval_routes") or [metadata.get("retrieval_route")]
        for route in routes:
            if route:
                unique_route_counts[route] += 1
    reranked_documents = service.rerank_candidates(
        original_question,
        unique_candidates,
        use_reranker=use_reranker,
    )
    for document in reranked_documents:
        document.metadata = dict(document.metadata or {})
        document.metadata["query_variants"] = list(query_variants)

    top_score = max(
        (float(document.metadata.get("final_rerank_score", 0.0)) for document in reranked_documents),
        default=None,
    )
    low_confidence_rejected = not (top_score is not None and top_score >= settings.RAG_MIN_RERANK_SCORE)
    accepted = not low_confidence_rejected
    anchor_decision = {"ok": True, "reason_code": None}
    if accepted and service.is_anchor_evidence_enabled():
        anchor_decision = service.evaluate_anchor_gate(original_question, reranked_documents)
        accepted = bool(anchor_decision.get("ok", True))
    return {
        "candidate_count_before_dedup": len(all_candidates),
        "candidate_count_after_dedup": len(unique_candidates),
        "vector_candidate_count": route_counts.get("vector", 0),
        "title_candidate_count": route_counts.get("title", 0),
        "bm25_candidate_count": route_counts.get("bm25", 0),
        "unique_vector_candidate_count": unique_route_counts.get("vector", 0),
        "unique_title_candidate_count": unique_route_counts.get("title", 0),
        "unique_bm25_candidate_count": unique_route_counts.get("bm25", 0),
        "bm25_unique_added_count": len(bm25_keys - (vector_keys | title_keys)),
        "bm25_vector_overlap_count": len(bm25_keys & vector_keys),
        "bm25_title_overlap_count": len(bm25_keys & title_keys),
        "source_id_missing_before_rerank": sum(
            1 for document in unique_candidates if not (document.metadata or {}).get("source_id")
        ),
        "top_score": top_score,
        "accepted": accepted,
        "low_confidence_rejected": low_confidence_rejected,
        "anchor_decision": anchor_decision,
        "rejected_by_anchor_evidence": not bool(anchor_decision.get("ok", True)),
        "documents_before_threshold": summarize_documents(reranked_documents),
        "documents": summarize_documents(reranked_documents if accepted else []),
    }


def summarize_documents(documents) -> list[dict[str, Any]]:
    summarized = []
    for document in documents:
        metadata = document.metadata or {}
        summarized.append({
            "final_rank": metadata.get("final_rank"),
            "title": metadata.get("title") or "",
            "source_id": metadata.get("source_id") or "",
            "retrieval_route": metadata.get("retrieval_route"),
            "retrieval_routes": metadata.get("retrieval_routes") or [],
            "bm25_score": to_float_or_none(metadata.get("bm25_score")),
            "matched_by_bm25_query": metadata.get("matched_by_bm25_query"),
            "bm25_query_variants": metadata.get("bm25_query_variants") or [],
            "embedding_rerank_score": to_float_or_none(metadata.get("embedding_rerank_score")),
            "reranker_score": to_float_or_none(metadata.get("reranker_score")),
            "reranker_rank": metadata.get("reranker_rank"),
            "ranking_base_score": to_float_or_none(metadata.get("ranking_base_score")),
            "reranker_provider": metadata.get("reranker_provider"),
            "reranker_model": metadata.get("reranker_model"),
            "final_rerank_score": to_float_or_none(metadata.get("final_rerank_score")),
            "mmr_score": to_float_or_none(metadata.get("mmr_score")),
            "matched_by_normalized_query": bool(metadata.get("matched_by_normalized_query")),
            "anchor_terms": metadata.get("anchor_terms") or [],
            "matched_anchor_terms": metadata.get("matched_anchor_terms") or [],
            "missing_anchor_terms": metadata.get("missing_anchor_terms") or [],
            "anchor_coverage_ratio": to_float_or_none(metadata.get("anchor_coverage_ratio")),
            "anchor_evidence_status": metadata.get("anchor_evidence_status"),
            "anchor_adjustment": to_float_or_none(metadata.get("anchor_adjustment")),
            "hard_anchor_adjustment": to_float_or_none(metadata.get("hard_anchor_adjustment")),
            "soft_anchor_adjustment": to_float_or_none(metadata.get("soft_anchor_adjustment")),
            "negative_anchor_adjustment": to_float_or_none(metadata.get("negative_anchor_adjustment")),
            "evidence_adjusted_score": to_float_or_none(metadata.get("evidence_adjusted_score")),
            "hard_anchor_terms": metadata.get("hard_anchor_terms") or [],
            "soft_anchor_terms": metadata.get("soft_anchor_terms") or [],
            "negative_anchor_terms": metadata.get("negative_anchor_terms") or [],
            "matched_hard_anchor_terms": metadata.get("matched_hard_anchor_terms") or [],
            "matched_soft_anchor_terms": metadata.get("matched_soft_anchor_terms") or [],
            "matched_negative_anchor_terms": metadata.get("matched_negative_anchor_terms") or [],
            "anchor_candidate_window_rank": metadata.get("anchor_candidate_window_rank"),
            "matched_locations": metadata.get("matched_locations") or {},
        })
    return summarized


def to_float_or_none(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def title_hit(documents: list[dict[str, Any]], expected_terms: list[str], max_rank: int) -> bool:
    if not expected_terms:
        return False
    for document in documents[:max_rank]:
        title = document.get("title") or ""
        if any(term and term in title for term in expected_terms):
            return True
    return False


def annotate_hits(documents: list[dict[str, Any]], expected_terms: list[str]) -> list[dict[str, Any]]:
    annotated = []
    for document in documents:
        copied = dict(document)
        title = copied.get("title") or ""
        copied["expected_title_contains_hit"] = bool(
            expected_terms and any(term and term in title for term in expected_terms)
        )
        annotated.append(copied)
    return annotated


def compare_ab(case: dict[str, Any], original_result: dict[str, Any], dual_result: dict[str, Any]) -> dict[str, Any]:
    expected_terms = case.get("expected_title_contains") or []
    original_docs = original_result["documents"]
    dual_docs = dual_result["documents"]
    original_top2_hit = title_hit(original_docs, expected_terms, 2)
    dual_top2_hit = title_hit(dual_docs, expected_terms, 2)
    original_titles = {doc["title"] for doc in original_docs[:2]}
    dual_titles = {doc["title"] for doc in dual_docs[:2]}
    new_expected_hit = bool(dual_top2_hit and not original_top2_hit)
    displaced_expected_hit = bool(original_top2_hit and not dual_top2_hit)
    if new_expected_hit:
        classification = "positive"
    elif displaced_expected_hit:
        classification = "negative"
    elif original_titles != dual_titles:
        classification = "changed"
    else:
        classification = "neutral"
    return {
        "original_topk": original_docs,
        "dual_topk": dual_docs,
        "dual_added_expected_title_hit": new_expected_hit,
        "dual_displaced_expected_title_hit": displaced_expected_hit,
        "classification": classification,
    }


def score_bucket(score: float | None) -> str:
    if score is None:
        return "none"
    if score < 0.25:
        return "<0.25"
    if score < 0.35:
        return "0.25-0.35"
    if score < 0.50:
        return "0.35-0.50"
    return ">=0.50"


def evaluate(
    collection_name: str | None = None,
    anchor_evidence_mode: str = "off",
    bm25_mode: str = "off",
    reranker_mode: str = "off",
    cases_file: str | Path | None = None,
    checkpoint_json_path: Path | None = None,
    checkpoint_md_path: Path | None = None,
) -> dict[str, Any]:
    resources = resource_status()
    missing = []
    if not resources["crawl_dir_exists"] or resources["crawl_markdown_count"] == 0:
        missing.append("Markdown knowledge base is missing or empty")
    if not resources["chroma_dir_exists"] or resources["chroma_file_count"] == 0:
        missing.append("Chroma vector store is missing or empty")
    if not resources["env_exists"]:
        missing.append(".env is missing")
    if missing:
        return {
            "status": "failed",
            "failure_type": "resource_missing",
            "failure_messages": missing,
            "resources": resources,
        }

    cases = load_cases(cases_file)
    vector_store = VectorStoreRepository(collection_name=collection_name) if collection_name else None
    service = RetrievalService(
        chroma_vector=vector_store,
        anchor_evidence_mode=anchor_evidence_mode,
        bm25_mode=bm25_mode,
        reranker_mode=reranker_mode,
    )
    collection_count = get_collection_count(service)
    if collection_count == 0:
        return {
            "status": "failed",
            "failure_type": "empty_chroma_collection",
            "resources": resources,
            "collection_count": collection_count,
        }

    results = load_checkpoint_results(checkpoint_json_path) if checkpoint_json_path else []
    completed_case_ids = {item.get("case_id") for item in results}
    for case in cases:
        if case["id"] in completed_case_ids:
            continue
        original_question = case["question"].strip()
        normalized_question, variants, dual_enabled = build_variants(original_question)
        reranker_latency_before = len(service.reranker_latency_ms)
        if reranker_mode == "experimental":
            single_result = None
            dual_result = evaluate_variant_set(service, original_question, variants, use_reranker=True)
        elif dual_enabled:
            single_result = evaluate_variant_set(service, original_question, [original_question], use_reranker=False)
            dual_result = evaluate_variant_set(service, original_question, variants, use_reranker=True)
        else:
            dual_result = evaluate_variant_set(service, original_question, variants, use_reranker=True)
            single_result = dual_result
        expected_terms = case.get("expected_title_contains") or []
        final_docs = annotate_hits(dual_result["documents"], expected_terms)
        final_docs_before_threshold = annotate_hits(dual_result["documents_before_threshold"], expected_terms)
        result = {
            "case_id": case["id"],
            "category": case.get("category") or "",
            "case_group": derive_case_group(case),
            "expected_answerability": case_expected_answerability(case),
            "expected_no_answer": case_expected_answerability(case) == "unanswerable",
            "original_question": original_question,
            "normalized_question": normalized_question,
            "query_variants": variants,
            "dual_retrieval_enabled": dual_enabled,
            "candidate_count_before_dedup": dual_result["candidate_count_before_dedup"],
            "candidate_count_after_dedup": dual_result["candidate_count_after_dedup"],
            "vector_candidate_count": dual_result["vector_candidate_count"],
            "title_candidate_count": dual_result["title_candidate_count"],
            "bm25_candidate_count": dual_result["bm25_candidate_count"],
            "unique_vector_candidate_count": dual_result["unique_vector_candidate_count"],
            "unique_title_candidate_count": dual_result["unique_title_candidate_count"],
            "unique_bm25_candidate_count": dual_result["unique_bm25_candidate_count"],
            "bm25_unique_added_count": dual_result["bm25_unique_added_count"],
            "bm25_vector_overlap_count": dual_result["bm25_vector_overlap_count"],
            "bm25_title_overlap_count": dual_result["bm25_title_overlap_count"],
            "source_id_missing_before_rerank": dual_result["source_id_missing_before_rerank"],
            "rejected_by_low_confidence": bool(dual_result.get("low_confidence_rejected")),
            "rejected_by_anchor_evidence": bool(dual_result.get("rejected_by_anchor_evidence")),
            "anchor_decision": dual_result.get("anchor_decision") or {"ok": True, "reason_code": None},
            "top_score": dual_result["top_score"],
            "final_topk_count": len(final_docs),
            "final_documents": final_docs,
            "documents_before_threshold": final_docs_before_threshold,
            "top1_title_weak_hit": title_hit(final_docs, expected_terms, 1),
            "top2_title_weak_hit": title_hit(final_docs, expected_terms, 2),
        }
        if reranker_mode == "experimental":
            new_latencies = service.reranker_latency_ms[reranker_latency_before:]
            result["reranker_call_success"] = bool(new_latencies)
            result["reranker_latency_ms"] = new_latencies[-1] if new_latencies else None
        if dual_enabled and single_result is not None:
            result["ab_comparison"] = compare_ab(case, single_result, dual_result)
        elif dual_enabled:
            result["ab_comparison"] = {
                "classification": "not_applicable_reranker_experiment",
                "reason": "single-route rerank is skipped so the 82-case reranker experiment performs one real rerank per case",
            }
        results.append(result)
        if checkpoint_json_path and checkpoint_md_path:
            checkpoint_report = build_report(
                resources,
                collection_count,
                cases,
                results,
                collection_name=collection_name,
                anchor_evidence_mode=anchor_evidence_mode,
                bm25_mode=bm25_mode,
                reranker_mode=reranker_mode,
                reranker_stats={
                    "success_count": sum(1 for item in results if item.get("reranker_call_success")),
                    "failure_count": service.reranker_failure_count,
                    "invalid_result_count": service.reranker_invalid_result_count,
                    "latency_ms": [item.get("reranker_latency_ms") for item in results if item.get("reranker_latency_ms") is not None],
                    "provider": settings.RAG_RERANKER_PROVIDER,
                    "model": settings.RAG_RERANKER_MODEL,
                },
            )
            checkpoint_report["status"] = "running" if len(results) < len(cases) else "success"
            checkpoint_report["cases_file"] = str(cases_file or CASES_PATH)
            write_reports(checkpoint_report, json_path=checkpoint_json_path, md_path=checkpoint_md_path)

    report = build_report(
        resources,
        collection_count,
        cases,
        results,
        collection_name=collection_name,
        anchor_evidence_mode=anchor_evidence_mode,
        bm25_mode=bm25_mode,
        reranker_mode=reranker_mode,
        reranker_stats={
            "success_count": sum(1 for item in results if item.get("reranker_call_success"))
            if reranker_mode == "experimental"
            else service.reranker_success_count,
            "failure_count": service.reranker_failure_count,
            "invalid_result_count": service.reranker_invalid_result_count,
            "latency_ms": [item.get("reranker_latency_ms") for item in results if item.get("reranker_latency_ms") is not None]
            if reranker_mode == "experimental"
            else list(service.reranker_latency_ms),
            "provider": settings.RAG_RERANKER_PROVIDER,
            "model": settings.RAG_RERANKER_MODEL,
        },
    )
    report["cases_file"] = str(cases_file or CASES_PATH)
    return report


def load_checkpoint_results(path: Path | None) -> list[dict[str, Any]]:
    if not path or not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8") as handle:
            report = json.load(handle)
        results = report.get("results") or []
        if isinstance(results, list):
            return [item for item in results if isinstance(item, dict) and item.get("case_id")]
    except Exception:
        return []
    return []


def case_expected_answerability(case: dict[str, Any]) -> str:
    if case.get("expected_answerability") in {"answerable", "unanswerable"}:
        return case["expected_answerability"]
    return "unanswerable" if case.get("expected_no_answer") else "answerable"


def derive_case_group(case: dict[str, Any]) -> str:
    category = case.get("category") or ""
    if category == "anchor_answerable":
        return "A_anchor_answerable"
    if category == "anchor_unanswerable":
        return "B_anchor_unanswerable"
    if category == "generic_answerable":
        return "C_generic_answerable"
    if category == "generic_unanswerable":
        return "D_generic_unanswerable"
    if category == "confusing":
        return "E_confusing"
    if case_expected_answerability(case) == "unanswerable":
        return "B_anchor_unanswerable" if case.get("expected_no_answer") else "D_generic_unanswerable"
    if "容易混淆" in category:
        return "E_confusing"
    anchors = case.get("expected_anchor_terms") or [anchor.term for anchor in extract_strong_anchors(case.get("question", ""))]
    return "A_anchor_answerable" if anchors else "C_generic_answerable"


def build_report(
    resources: dict[str, Any],
    collection_count: int | None,
    cases: list[dict[str, Any]],
    results: list[dict[str, Any]],
    collection_name: str | None = None,
    anchor_evidence_mode: str = "off",
    bm25_mode: str = "off",
    reranker_mode: str = "off",
    reranker_stats: dict[str, Any] | None = None,
) -> dict[str, Any]:
    total = len(results)
    normalization_triggered = sum(1 for item in results if item["dual_retrieval_enabled"])
    normalization_not_triggered = total - normalization_triggered
    accepted = sum(1 for item in results if not item["rejected_by_low_confidence"] and not item.get("rejected_by_anchor_evidence"))
    low_confidence_rejected = sum(1 for item in results if item["rejected_by_low_confidence"])
    anchor_rejected = sum(1 for item in results if item.get("rejected_by_anchor_evidence"))
    expected_no_answer = [item for item in results if item["expected_no_answer"]]
    expected_answer = [item for item in results if not item["expected_no_answer"]]
    top1_hits = sum(1 for item in results if item["top1_title_weak_hit"])
    top2_hits = sum(1 for item in results if item["top2_title_weak_hit"])
    ab_counter = Counter(
        item.get("ab_comparison", {}).get("classification", "not_applicable")
        for item in results
        if item["dual_retrieval_enabled"]
    )
    score_buckets = Counter(score_bucket(item["top_score"]) for item in results)
    category_distribution = Counter(item.get("category") or "" for item in results)
    possible_false_rejections = [
        item["case_id"]
        for item in expected_answer
        if item["rejected_by_low_confidence"] or item.get("rejected_by_anchor_evidence")
    ]
    possible_irrelevant_accepted = [
        item["case_id"]
        for item in expected_no_answer
        if not item["rejected_by_low_confidence"]
        and not item.get("rejected_by_anchor_evidence")
    ]
    anchor_missing_count = sum(
        1
        for item in results
        if (item.get("anchor_decision") or {}).get("reason_code") == "ANCHOR_EVIDENCE_MISSING"
    )
    strong_anchor_count = sum(
        1
        for item in results
        if (item.get("anchor_decision") or {}).get("anchor_evidence", {}).get("anchors")
        or any(doc.get("anchor_terms") for doc in item.get("documents_before_threshold", []))
    )
    hard_anchor_count = 0
    soft_anchor_count = 0
    negative_anchor_count = 0
    no_anchor_count = 0
    for item in results:
        anchors = extract_anchors(item.get("original_question", ""))
        has_hard = any(anchor.anchor_type == ANCHOR_TYPE_HARD for anchor in anchors)
        has_soft = any(anchor.anchor_type == ANCHOR_TYPE_SOFT for anchor in anchors)
        has_negative = any(anchor.anchor_type == ANCHOR_TYPE_NEGATIVE for anchor in anchors)
        hard_anchor_count += int(has_hard)
        soft_anchor_count += int(has_soft)
        negative_anchor_count += int(has_negative)
        no_anchor_count += int(not (has_hard or has_soft or has_negative))
    hard_evidence_outside_topk_count = sum(
        1
        for item in results
        if (item.get("anchor_decision") or {}).get("anchor_evidence", {}).get("hard_evidence_exists_outside_topk")
    )
    negative_anchor_penalty_count = sum(
        1
        for item in results
        for doc in item.get("documents_before_threshold", [])
        if (doc.get("negative_anchor_adjustment") or 0) < 0
    )
    suspicious_cases = rank_suspicious_cases(results)[:5]
    top_scores = [item["top_score"] for item in results if item["top_score"] is not None]
    bm25_candidate_total = sum(int(item.get("bm25_candidate_count") or 0) for item in results)
    bm25_unique_added_total = sum(int(item.get("bm25_unique_added_count") or 0) for item in results)
    bm25_vector_overlap_total = sum(int(item.get("bm25_vector_overlap_count") or 0) for item in results)
    bm25_title_overlap_total = sum(int(item.get("bm25_title_overlap_count") or 0) for item in results)
    reranker_stats = reranker_stats or {}
    reranker_latencies = [int(value) for value in reranker_stats.get("latency_ms", [])]
    reranker_latency_avg = statistics.mean(reranker_latencies) if reranker_latencies else None
    reranker_latency_p95 = percentile(reranker_latencies, 95) if reranker_latencies else None
    summary = {
        "total_cases": total,
        "category_distribution": dict(category_distribution),
        "normalization_triggered": normalization_triggered,
        "normalization_not_triggered": normalization_not_triggered,
        "dual_retrieval_count": normalization_triggered,
        "single_retrieval_count": normalization_not_triggered,
        "accepted_count": accepted,
        "low_confidence_rejected_count": low_confidence_rejected,
        "anchor_rejected_count": anchor_rejected,
        "total_rejected_count": total - accepted,
        "top1_title_weak_hit_count": top1_hits,
        "top1_title_weak_hit_rate": safe_rate(top1_hits, total),
        "top2_title_weak_hit_count": top2_hits,
        "top2_title_weak_hit_rate": safe_rate(top2_hits, total),
        "expected_no_answer_correctly_rejected": sum(1 for item in expected_no_answer if item["rejected_by_low_confidence"]),
        "expected_no_answer_anchor_rejected": sum(1 for item in expected_no_answer if item.get("rejected_by_anchor_evidence")),
        "expected_no_answer_not_rejected": sum(
            1
            for item in expected_no_answer
            if not item["rejected_by_low_confidence"] and not item.get("rejected_by_anchor_evidence")
        ),
        "expected_answer_false_rejected": len(possible_false_rejections),
        "anchor_evidence_mode": anchor_evidence_mode,
        "strong_anchor_case_count": strong_anchor_count,
        "hard_anchor_case_count": hard_anchor_count,
        "soft_anchor_case_count": soft_anchor_count,
        "negative_anchor_case_count": negative_anchor_count,
        "no_anchor_case_count": no_anchor_count,
        "no_strong_anchor_case_count": total - strong_anchor_count,
        "anchor_evidence_missing_count": anchor_missing_count,
        "hard_evidence_exists_outside_topk_count": hard_evidence_outside_topk_count,
        "negative_anchor_penalty_count": negative_anchor_penalty_count,
        "bm25_mode": bm25_mode,
        "bm25_candidate_total": bm25_candidate_total,
        "bm25_unique_added_total": bm25_unique_added_total,
        "bm25_vector_overlap_total": bm25_vector_overlap_total,
        "bm25_title_overlap_total": bm25_title_overlap_total,
        "bm25_vector_overlap_rate": safe_rate(bm25_vector_overlap_total, bm25_candidate_total),
        "bm25_title_overlap_rate": safe_rate(bm25_title_overlap_total, bm25_candidate_total),
        "reranker_mode": reranker_mode,
        "reranker_provider": reranker_stats.get("provider") if reranker_mode == "experimental" else None,
        "reranker_model": reranker_stats.get("model") if reranker_mode == "experimental" else None,
        "reranker_success_count": int(reranker_stats.get("success_count") or 0),
        "reranker_failure_count": int(reranker_stats.get("failure_count") or 0),
        "reranker_invalid_result_count": int(reranker_stats.get("invalid_result_count") or 0),
        "reranker_latency_avg_ms": reranker_latency_avg,
        "reranker_latency_p95_ms": reranker_latency_p95,
        "source_id_missing_before_rerank_total": sum(
            int(item.get("source_id_missing_before_rerank") or 0) for item in results
        ),
        "ab_positive_count": ab_counter.get("positive", 0),
        "ab_neutral_count": ab_counter.get("neutral", 0),
        "ab_changed_count": ab_counter.get("changed", 0),
        "ab_negative_count": ab_counter.get("negative", 0),
        "score_buckets": dict(score_buckets),
        "top_score_min": min(top_scores) if top_scores else None,
        "top_score_median": statistics.median(top_scores) if top_scores else None,
        "top_score_max": max(top_scores) if top_scores else None,
        "possible_false_rejections": possible_false_rejections,
        "possible_irrelevant_accepted": possible_irrelevant_accepted,
        "group_metrics": build_group_metrics(results),
    }
    return {
        "status": "success",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "resources": resources,
        "collection_count": collection_count,
        "settings": {
            "collection_name": collection_name or settings.VECTOR_COLLECTION_NAME,
            "CHUNK_SIZE": settings.CHUNK_SIZE,
            "CHUNK_OVERLAP": settings.CHUNK_OVERLAP,
            "EMBEDDING_MODEL": settings.EMBEDDING_MODEL,
            "VECTOR_DISTANCE_SPACE": settings.VECTOR_DISTANCE_SPACE,
            "RAG_VECTOR_CANDIDATE_TOP_K": settings.RAG_VECTOR_CANDIDATE_TOP_K,
            "RAG_TITLE_CANDIDATE_TOP_K": settings.RAG_TITLE_CANDIDATE_TOP_K,
            "RAG_FINAL_TOP_K": settings.RAG_FINAL_TOP_K,
            "RAG_MIN_RERANK_SCORE": settings.RAG_MIN_RERANK_SCORE,
            "RAG_ANCHOR_EVIDENCE_MODE": anchor_evidence_mode,
            "RAG_ANCHOR_EVIDENCE_WINDOW_SIZE": settings.RAG_ANCHOR_EVIDENCE_WINDOW_SIZE,
            "RAG_ANCHOR_MATCH_BOOST": settings.RAG_ANCHOR_MATCH_BOOST,
            "RAG_ANCHOR_MISSING_PENALTY": settings.RAG_ANCHOR_MISSING_PENALTY,
            "RAG_HARD_ANCHOR_MATCH_BOOST": settings.RAG_HARD_ANCHOR_MATCH_BOOST,
            "RAG_HARD_ANCHOR_MISSING_PENALTY": settings.RAG_HARD_ANCHOR_MISSING_PENALTY,
            "RAG_SOFT_ANCHOR_MATCH_BOOST": settings.RAG_SOFT_ANCHOR_MATCH_BOOST,
            "RAG_SOFT_ANCHOR_MISSING_PENALTY": settings.RAG_SOFT_ANCHOR_MISSING_PENALTY,
            "RAG_NEGATIVE_ANCHOR_MATCH_PENALTY": settings.RAG_NEGATIVE_ANCHOR_MATCH_PENALTY,
            "RAG_ANCHOR_REQUIRE_EVIDENCE_FOR_BLOCK": settings.RAG_ANCHOR_REQUIRE_EVIDENCE_FOR_BLOCK,
            "RAG_BM25_MODE": bm25_mode,
            "RAG_BM25_CANDIDATE_TOP_K": settings.RAG_BM25_CANDIDATE_TOP_K,
            "RAG_RERANKER_MODE": reranker_mode,
            "RAG_RERANKER_PROVIDER": settings.RAG_RERANKER_PROVIDER,
            "RAG_RERANKER_MODEL": settings.RAG_RERANKER_MODEL if reranker_mode == "experimental" else None,
            "RAG_RERANKER_MAX_DOCUMENT_CHARS": settings.RAG_RERANKER_MAX_DOCUMENT_CHARS,
        },
        "summary": summary,
        "threshold_recommendation": build_threshold_recommendation(summary, results),
        "suspicious_cases": suspicious_cases,
        "results": results,
        "notes": [
            "Title weak hit is an automatic weak label based only on expected_title_contains.",
            "It is not equivalent to real business accuracy and requires manual confirmation.",
            "Reports intentionally omit full document text and sensitive environment values.",
        ],
    }


def build_group_metrics(results: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for item in results:
        grouped.setdefault(item.get("case_group") or "unknown", []).append(item)
    metrics = {}
    for group, items in grouped.items():
        expected_answer = [item for item in items if item.get("expected_answerability") == "answerable"]
        expected_no_answer = [item for item in items if item.get("expected_answerability") == "unanswerable"]
        false_rejected = [
            item["case_id"]
            for item in expected_answer
            if item.get("rejected_by_low_confidence") or item.get("rejected_by_anchor_evidence")
        ]
        correctly_rejected = [
            item["case_id"]
            for item in expected_no_answer
            if item.get("rejected_by_low_confidence") or item.get("rejected_by_anchor_evidence")
        ]
        still_accepted = [
            item["case_id"]
            for item in expected_no_answer
            if not item.get("rejected_by_low_confidence") and not item.get("rejected_by_anchor_evidence")
        ]
        manual_review = [
            item["case_id"]
            for item in items
            if (item.get("expected_answerability") == "answerable" and not item.get("top2_title_weak_hit"))
            or (item.get("expected_answerability") == "unanswerable" and item["case_id"] in still_accepted)
        ]
        metrics[group] = {
            "total": len(items),
            "top1_title_weak_hit_count": sum(1 for item in items if item.get("top1_title_weak_hit")),
            "top2_title_weak_hit_count": sum(1 for item in items if item.get("top2_title_weak_hit")),
            "expected_answer_false_rejected_count": len(false_rejected),
            "expected_answer_false_rejected_cases": false_rejected,
            "expected_no_answer_correctly_rejected_count": len(correctly_rejected),
            "expected_no_answer_correctly_rejected_cases": correctly_rejected,
            "expected_no_answer_still_accepted_count": len(still_accepted),
            "expected_no_answer_still_accepted_cases": still_accepted,
            "anchor_evidence_missing_count": sum(
                1
                for item in items
                if (item.get("anchor_decision") or {}).get("reason_code") == "ANCHOR_EVIDENCE_MISSING"
            ),
            "needs_manual_review_count": len(manual_review),
            "needs_manual_review_cases": manual_review,
        }
    return metrics


def safe_rate(count: int, total: int) -> float:
    return round(count / total, 4) if total else 0.0


def percentile(values: list[int], pct: int) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, int(round((pct / 100) * (len(ordered) - 1)))))
    return float(ordered[index])


def rank_suspicious_cases(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    suspicious = []
    for item in results:
        reason = []
        if item["expected_no_answer"] and not item["rejected_by_low_confidence"]:
            reason.append("expected_no_answer_not_rejected")
        if not item["expected_no_answer"] and (item["rejected_by_low_confidence"] or item.get("rejected_by_anchor_evidence")):
            reason.append("expected_answer_rejected")
        if not item["expected_no_answer"] and not item["top2_title_weak_hit"]:
            reason.append("top2_title_weak_miss")
        if item.get("ab_comparison", {}).get("classification") == "negative":
            reason.append("dual_retrieval_possible_negative")
        if reason:
            suspicious.append({
                "case_id": item["case_id"],
                "question": item["original_question"],
                "top_score": item["top_score"],
                "rejected_by_low_confidence": item["rejected_by_low_confidence"],
                "reason": reason,
                "top_titles": [doc["title"] for doc in item["documents_before_threshold"][:2]],
            })
    return suspicious


def build_threshold_recommendation(summary: dict[str, Any], results: list[dict[str, Any]]) -> dict[str, Any]:
    false_rejected = summary["possible_false_rejections"]
    irrelevant_accepted = summary["possible_irrelevant_accepted"]
    near_threshold = [
        item["case_id"]
        for item in results
        if item["top_score"] is not None and 0.25 <= item["top_score"] < 0.35
    ]
    passed_but_weak = [
        item["case_id"]
        for item in results
        if item["top_score"] is not None
        and item["top_score"] >= settings.RAG_MIN_RERANK_SCORE
        and not item["expected_no_answer"]
        and not item["top2_title_weak_hit"]
        and not item.get("rejected_by_anchor_evidence")
    ]
    if false_rejected and not irrelevant_accepted:
        recommendation = "consider_lowering_to_0.30"
    elif irrelevant_accepted and not false_rejected:
        recommendation = "consider_raising_to_0.40"
    else:
        recommendation = "keep_0.35_pending_manual_review"
    return {
        "recommendation": recommendation,
        "cases_between_0.25_and_0.35": near_threshold,
        "possible_false_rejections": false_rejected,
        "passed_but_title_weak_miss": passed_but_weak,
        "expected_no_answer_not_rejected": irrelevant_accepted,
    }


def write_reports(report: dict[str, Any], json_path: Path = REPORT_JSON_PATH, md_path: Path = REPORT_MD_PATH) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    with json_path.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)
    with md_path.open("w", encoding="utf-8") as handle:
        handle.write(render_markdown(report))


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# RAG Retrieval Evaluation Report",
        "",
        f"- Status: `{report.get('status')}`",
        f"- Generated at: `{report.get('generated_at', '')}`",
    ]
    if report.get("status") != "success":
        lines.extend([
            f"- Failure type: `{report.get('failure_type')}`",
            f"- Failure messages: {report.get('failure_messages') or report.get('failure_message')}",
            "",
        ])
        return "\n".join(lines)

    summary = report["summary"]
    settings_summary = report["settings"]
    lines.extend([
        "",
        "## Settings",
        "",
        f"- Collection: {settings_summary.get('collection_name')}",
        f"- CHUNK_SIZE: {settings_summary.get('CHUNK_SIZE')}",
        f"- CHUNK_OVERLAP: {settings_summary.get('CHUNK_OVERLAP')}",
        f"- EMBEDDING_MODEL: {settings_summary.get('EMBEDDING_MODEL')}",
        f"- VECTOR_DISTANCE_SPACE: {settings_summary.get('VECTOR_DISTANCE_SPACE')}",
        f"- RAG_VECTOR_CANDIDATE_TOP_K: {settings_summary['RAG_VECTOR_CANDIDATE_TOP_K']}",
        f"- RAG_TITLE_CANDIDATE_TOP_K: {settings_summary['RAG_TITLE_CANDIDATE_TOP_K']}",
        f"- RAG_FINAL_TOP_K: {settings_summary['RAG_FINAL_TOP_K']}",
        f"- RAG_MIN_RERANK_SCORE: {settings_summary['RAG_MIN_RERANK_SCORE']}",
        f"- RAG_ANCHOR_EVIDENCE_MODE: {settings_summary.get('RAG_ANCHOR_EVIDENCE_MODE')}",
        f"- RAG_BM25_MODE: {settings_summary.get('RAG_BM25_MODE')}",
        f"- RAG_BM25_CANDIDATE_TOP_K: {settings_summary.get('RAG_BM25_CANDIDATE_TOP_K')}",
        f"- RAG_RERANKER_MODE: {settings_summary.get('RAG_RERANKER_MODE')}",
        f"- RAG_RERANKER_PROVIDER: {settings_summary.get('RAG_RERANKER_PROVIDER')}",
        f"- RAG_RERANKER_MODEL: {settings_summary.get('RAG_RERANKER_MODEL')}",
        f"- RAG_RERANKER_MAX_DOCUMENT_CHARS: {settings_summary.get('RAG_RERANKER_MAX_DOCUMENT_CHARS')}",
        "",
        "## Summary",
        "",
        f"- Total cases: {summary['total_cases']}",
        f"- Normalization triggered: {summary['normalization_triggered']}",
        f"- Normalization not triggered: {summary['normalization_not_triggered']}",
        f"- Accepted with final docs: {summary['accepted_count']}",
        f"- Low-confidence rejected: {summary['low_confidence_rejected_count']}",
        f"- Top1 title weak hit: {summary['top1_title_weak_hit_count']} ({summary['top1_title_weak_hit_rate']})",
        f"- Top2 title weak hit: {summary['top2_title_weak_hit_count']} ({summary['top2_title_weak_hit_rate']})",
        f"- Expected no-answer correctly rejected: {summary['expected_no_answer_correctly_rejected']}",
        f"- Expected no-answer anchor rejected: {summary.get('expected_no_answer_anchor_rejected', 0)}",
        f"- Expected no-answer not rejected: {summary['expected_no_answer_not_rejected']}",
        f"- Expected-answer false rejected: {summary['expected_answer_false_rejected']}",
        f"- Strong anchor cases: {summary.get('strong_anchor_case_count', 0)}",
        f"- Hard anchor cases: {summary.get('hard_anchor_case_count', 0)}",
        f"- Soft anchor cases: {summary.get('soft_anchor_case_count', 0)}",
        f"- Negative anchor cases: {summary.get('negative_anchor_case_count', 0)}",
        f"- No anchor cases: {summary.get('no_anchor_case_count', 0)}",
        f"- Hard evidence outside TopK: {summary.get('hard_evidence_exists_outside_topk_count', 0)}",
        f"- Negative anchor penalties: {summary.get('negative_anchor_penalty_count', 0)}",
        f"- ANCHOR_EVIDENCE_MISSING: {summary.get('anchor_evidence_missing_count', 0)}",
        f"- BM25 mode: {summary.get('bm25_mode')}",
        f"- BM25 candidates: {summary.get('bm25_candidate_total', 0)}",
        f"- BM25 unique additions: {summary.get('bm25_unique_added_total', 0)}",
        f"- BM25/vector overlap: {summary.get('bm25_vector_overlap_total', 0)} ({summary.get('bm25_vector_overlap_rate', 0)})",
        f"- BM25/title overlap: {summary.get('bm25_title_overlap_total', 0)} ({summary.get('bm25_title_overlap_rate', 0)})",
        f"- Reranker mode: {summary.get('reranker_mode')}",
        f"- Reranker provider: {summary.get('reranker_provider')}",
        f"- Reranker model: {summary.get('reranker_model')}",
        f"- Reranker success/failure: {summary.get('reranker_success_count', 0)}/{summary.get('reranker_failure_count', 0)}",
        f"- Reranker invalid results: {summary.get('reranker_invalid_result_count', 0)}",
        f"- Reranker latency avg/P95 ms: {summary.get('reranker_latency_avg_ms')}/{summary.get('reranker_latency_p95_ms')}",
        f"- Missing source_id before rerank: {summary.get('source_id_missing_before_rerank_total', 0)}",
        "",
        "## Group Metrics",
        "",
    ])
    for group, metrics in summary.get("group_metrics", {}).items():
        lines.append(
            f"- {group}: total={metrics['total']}, top1={metrics['top1_title_weak_hit_count']}, "
            f"top2={metrics['top2_title_weak_hit_count']}, false_rejected={metrics['expected_answer_false_rejected_count']}, "
            f"no_answer_rejected={metrics['expected_no_answer_correctly_rejected_count']}, "
            f"no_answer_accepted={metrics['expected_no_answer_still_accepted_count']}, "
            f"anchor_missing={metrics['anchor_evidence_missing_count']}, manual_review={metrics['needs_manual_review_count']}"
        )
    lines.extend([
        "",
        "## A/B Comparison",
        "",
        f"- Positive: {summary['ab_positive_count']}",
        f"- Neutral: {summary['ab_neutral_count']}",
        f"- Changed: {summary['ab_changed_count']}",
        f"- Negative: {summary['ab_negative_count']}",
        "",
        "## Score Buckets",
        "",
    ])
    for bucket, count in summary["score_buckets"].items():
        lines.append(f"- {bucket}: {count}")
    lines.extend([
        "",
        "## Threshold Recommendation",
        "",
        f"- Recommendation: `{report['threshold_recommendation']['recommendation']}`",
        f"- Possible false rejections: {report['threshold_recommendation']['possible_false_rejections']}",
        f"- Expected no-answer not rejected: {report['threshold_recommendation']['expected_no_answer_not_rejected']}",
        f"- Passed but title weak miss: {report['threshold_recommendation']['passed_but_title_weak_miss']}",
        "",
        "## Suspicious Cases",
        "",
    ])
    for item in report["suspicious_cases"][:5]:
        lines.append(
            f"- {item['case_id']}: score={item['top_score']}, rejected={item['rejected_by_low_confidence']}, "
            f"reason={item['reason']}, top_titles={item['top_titles']}"
        )
    lines.extend([
        "",
        "## Case Details",
        "",
    ])
    for item in report["results"]:
        top_titles = [doc["title"] for doc in item["final_documents"]]
        lines.append(
            f"- {item['case_id']} | dual={item['dual_retrieval_enabled']} | rejected={item['rejected_by_low_confidence']} "
            f"| anchor_rejected={item.get('rejected_by_anchor_evidence', False)} | score={item['top_score']} "
            f"| bm25={item.get('bm25_candidate_count', 0)} unique={item.get('bm25_unique_added_count', 0)} "
            f"| top_titles={top_titles}"
        )
    lines.extend([
        "",
        "> Title weak hit is an automatic weak label, not final business accuracy.",
    ])
    return "\n".join(lines)


def print_console_summary(report: dict[str, Any], json_path: Path = REPORT_JSON_PATH, md_path: Path = REPORT_MD_PATH) -> None:
    if report.get("status") != "success":
        print("RAG evaluation failed")
        print(f"failure_type={report.get('failure_type')}")
        print(f"messages={report.get('failure_messages') or report.get('failure_message')}")
        print(f"json_report={json_path}")
        print(f"md_report={md_path}")
        return
    summary = report["summary"]
    print("RAG retrieval evaluation completed")
    print(f"cases={summary['total_cases']}")
    print(f"normalization={summary['normalization_triggered']} triggered / {summary['normalization_not_triggered']} unchanged")
    print(
        f"accepted={summary['accepted_count']} "
        f"low_confidence_rejected={summary['low_confidence_rejected_count']} "
        f"anchor_rejected={summary.get('anchor_rejected_count', 0)} "
        f"total_rejected={summary.get('total_rejected_count', summary['low_confidence_rejected_count'])}"
    )
    print(f"anchor_missing={summary.get('anchor_evidence_missing_count', 0)}")
    print(
        "anchors="
        f"hard:{summary.get('hard_anchor_case_count', 0)} "
        f"soft:{summary.get('soft_anchor_case_count', 0)} "
        f"negative:{summary.get('negative_anchor_case_count', 0)} "
        f"none:{summary.get('no_anchor_case_count', 0)}"
    )
    print(
        f"hard_evidence_outside_topk={summary.get('hard_evidence_exists_outside_topk_count', 0)} "
        f"negative_penalties={summary.get('negative_anchor_penalty_count', 0)}"
    )
    print(
        f"bm25_mode={summary.get('bm25_mode')} "
        f"bm25_candidates={summary.get('bm25_candidate_total', 0)} "
        f"bm25_unique_added={summary.get('bm25_unique_added_total', 0)} "
        f"bm25_vector_overlap={summary.get('bm25_vector_overlap_total', 0)} "
        f"bm25_title_overlap={summary.get('bm25_title_overlap_total', 0)}"
    )
    print(
        f"reranker_mode={summary.get('reranker_mode')} "
        f"provider={summary.get('reranker_provider')} "
        f"model={summary.get('reranker_model')} "
        f"success={summary.get('reranker_success_count', 0)} "
        f"failure={summary.get('reranker_failure_count', 0)} "
        f"invalid={summary.get('reranker_invalid_result_count', 0)} "
        f"avg_ms={summary.get('reranker_latency_avg_ms')} "
        f"p95_ms={summary.get('reranker_latency_p95_ms')}"
    )
    print(f"top1_hit={summary['top1_title_weak_hit_count']} top2_hit={summary['top2_title_weak_hit_count']}")
    print(f"ab positive={summary['ab_positive_count']} neutral={summary['ab_neutral_count']} changed={summary['ab_changed_count']} negative={summary['ab_negative_count']}")
    print(f"score_buckets={summary['score_buckets']}")
    print(f"recommendation={report['threshold_recommendation']['recommendation']}")
    print(f"json_report={json_path}")
    print(f"md_report={md_path}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate RAG retrieval against a selected Chroma collection.")
    parser.add_argument("--cases-file", help="Override evaluation cases JSON file.")
    parser.add_argument("--collection-name", help="Override collection name for this evaluation process only.")
    parser.add_argument("--output-prefix", help="Write report to testdata/<prefix>.json/.md instead of default paths.")
    parser.add_argument(
        "--anchor-evidence-mode",
        choices=("off", "experimental", "legacy", "hard-soft-negative"),
        default="off",
        help="Enable anchor evidence mode only for this evaluation run.",
    )
    parser.add_argument(
        "--bm25-mode",
        choices=("off", "experimental"),
        default="off",
        help="Enable experimental BM25 candidate retrieval for this evaluation run.",
    )
    parser.add_argument(
        "--reranker-mode",
        choices=("off", "experimental"),
        default="off",
        help="Enable experimental SiliconFlow reranker only for this evaluation run.",
    )
    args = parser.parse_args()
    json_path, md_path = report_paths(args.output_prefix)
    try:
        report = evaluate(
            collection_name=args.collection_name,
            anchor_evidence_mode=args.anchor_evidence_mode,
            bm25_mode=args.bm25_mode,
            reranker_mode=args.reranker_mode,
            cases_file=args.cases_file,
            checkpoint_json_path=json_path,
            checkpoint_md_path=md_path,
        )
    except Exception as exc:
        report = {
            "status": "failed",
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "failure_type": classify_exception(exc),
            "failure_message": str(exc),
            "traceback_tail": traceback.format_exc().splitlines()[-8:],
            "resources": resource_status(),
        }
    write_reports(report, json_path=json_path, md_path=md_path)
    print_console_summary(report, json_path=json_path, md_path=md_path)
    return 0 if report.get("status") == "success" else 2


def classify_exception(exc: Exception) -> str:
    message = str(exc).lower()
    if "403" in message or "forbidden" in message or "permissiondenied" in message:
        return "embedding_api_permission_or_balance_error"
    if "api" in message and ("key" in message or "token" in message):
        return "embedding_api_config_missing"
    if "insufficient" in message or "balance" in message or "quota" in message:
        return "embedding_api_permission_or_balance_error"
    if "connection" in message or "timeout" in message or "network" in message:
        return "embedding_api_network_unavailable"
    if "no module named" in message or "modulenotfounderror" in message:
        return "dependency_or_import_error"
    if "chroma" in message:
        return "chroma_runtime_error"
    return "other_exception"


if __name__ == "__main__":
    raise SystemExit(main())

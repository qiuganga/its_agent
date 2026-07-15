import logging
import os
import re
from typing import Any, Dict, List

import jieba
from langchain_core.documents import Document
from sklearn.metrics.pairwise import cosine_similarity

from config.settings import settings
from repositories.vector_store_repository import VectorStoreRepository
from repositories.bm25_repository import Bm25Repository
from repositories.reranker_repository import SiliconFlowRerankerRepository
from services.ingestion.ingestion_processor import IngestionProcessor
from services.anchor_evidence_service import (
    apply_anchor_adjustment,
    evaluate_hard_soft_negative_gate,
    evaluate_retrieval_evidence,
)
from utils.embedding_text import (
    build_content_hash,
    build_document_id,
    build_embedding_text,
    has_effective_content,
    strip_existing_source_prefixes,
)
from utils.markdown_utils import MarkDownUtils


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RetrievalService:
    def __init__(
        self,
        chroma_vector: VectorStoreRepository | None = None,
        spliter: IngestionProcessor | None = None,
        *,
        anchor_evidence_enabled: bool | None = None,
        anchor_match_boost: float | None = None,
        anchor_missing_penalty: float | None = None,
        anchor_require_evidence_for_block: bool | None = None,
        anchor_evidence_mode: str | None = None,
        anchor_evidence_window_size: int | None = None,
        bm25_mode: str = "off",
        bm25_repository: Bm25Repository | None = None,
        reranker_mode: str | None = None,
        reranker_repository: SiliconFlowRerankerRepository | None = None,
    ):
        self.chroma_vector = chroma_vector or VectorStoreRepository()
        self.spliter = spliter or IngestionProcessor(vector_store=self.chroma_vector)
        configured_mode = (anchor_evidence_mode or settings.RAG_ANCHOR_EVIDENCE_MODE or "off").strip().lower()
        if configured_mode == "experimental":
            configured_mode = "legacy"
        if configured_mode not in {"off", "legacy", "hard-soft-negative"}:
            configured_mode = "off"
        if anchor_evidence_enabled is True and configured_mode == "off":
            configured_mode = "legacy"
        if anchor_evidence_enabled is False:
            configured_mode = "off"
        self.anchor_evidence_mode = configured_mode
        self.anchor_evidence_enabled = self.anchor_evidence_mode != "off"
        self.anchor_evidence_window_size = (
            settings.RAG_ANCHOR_EVIDENCE_WINDOW_SIZE
            if anchor_evidence_window_size is None
            else int(anchor_evidence_window_size)
        )
        self.anchor_match_boost = (
            settings.RAG_ANCHOR_MATCH_BOOST if anchor_match_boost is None else float(anchor_match_boost)
        )
        self.anchor_missing_penalty = (
            settings.RAG_ANCHOR_MISSING_PENALTY if anchor_missing_penalty is None else float(anchor_missing_penalty)
        )
        self.anchor_require_evidence_for_block = (
            settings.RAG_ANCHOR_REQUIRE_EVIDENCE_FOR_BLOCK
            if anchor_require_evidence_for_block is None
            else bool(anchor_require_evidence_for_block)
        )
        self._last_anchor_window_documents: list[Document] = []
        self.bm25_mode = (bm25_mode or "off").strip().lower()
        if self.bm25_mode not in {"off", "experimental"}:
            self.bm25_mode = "off"
        self.bm25_repository = bm25_repository
        if self.bm25_mode == "experimental":
            self.bm25_repository = self.bm25_repository or Bm25Repository()
            self.bm25_repository.load_index()
        self.reranker_mode = (reranker_mode or settings.RAG_RERANKER_MODE or "off").strip().lower()
        if self.reranker_mode not in {"off", "experimental"}:
            self.reranker_mode = "off"
        self.reranker_repository = reranker_repository
        if self.reranker_mode == "experimental":
            self.reranker_repository = self.reranker_repository or SiliconFlowRerankerRepository()
        self.reranker_success_count = 0
        self.reranker_failure_count = 0
        self.reranker_latency_ms: list[int] = []
        self.reranker_invalid_result_count = 0
        self._fast_bm25_repository: Bm25Repository | None = None

    def rough_ranking(self, user_query, mds_metadata: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not user_query:
            return []

        roughing_word_weight = 0.7
        valid_mds_metadata = []

        for md_metadata in mds_metadata:
            md_metadata_title = md_metadata.get("title", "")
            if not md_metadata_title or not md_metadata_title.strip():
                continue

            user_query_char = set(user_query)
            title_char = set(md_metadata_title)
            unique_char = user_query_char | title_char
            char_score = len(user_query_char & title_char) / len(unique_char) if unique_char else 0

            user_query_word = set(jieba.lcut(user_query))
            title_word = set(jieba.lcut(md_metadata_title))
            unique_word = user_query_word | title_word
            word_score = len(user_query_word & title_word) / len(unique_word) if unique_word else 0

            roughing_score = word_score * roughing_word_weight + char_score * (1 - roughing_word_weight)
            copied = dict(md_metadata)
            copied["roughing_score"] = float(roughing_score)
            valid_mds_metadata.append(copied)

        return sorted(valid_mds_metadata, key=lambda x: x.get("roughing_score", 0), reverse=True)[:settings.TOP_ROUGH]

    def fine_ranking(self, user_query: str, rough_mds_metadata: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not rough_mds_metadata:
            return []

        query_embedding = self.chroma_vector.embedd_document(user_query)
        roughing_title = [item.get("title", "") for item in rough_mds_metadata if item.get("title", "").strip()]
        if not roughing_title:
            return []

        title_embeddings = self.chroma_vector.embedd_documents(roughing_title)
        similarity = cosine_similarity([query_embedding], title_embeddings).flatten()

        valid_results = []
        for index, md_metadata in enumerate(rough_mds_metadata):
            if index >= len(similarity):
                break
            sim = max(float(similarity[index]), 0.0)
            roughing_score = float(md_metadata.get("roughing_score", 0))
            final_score = roughing_score * 0.3 + sim * 0.7
            copied = dict(md_metadata)
            copied["sim_score"] = sim
            copied["final_score"] = float(final_score)
            valid_results.append(copied)

        return sorted(valid_results, key=lambda x: x.get("final_score", 0), reverse=True)[:settings.RAG_TITLE_CANDIDATE_TOP_K]

    def retrieve_candidates(
        self,
        query: str,
        *,
        original_question: str | None = None,
    ) -> List[Document]:
        """Run vector and title retrieval for one query variant without final rerank."""
        based_vector_candidates = self._search_based_vector(query)
        based_title_candidates = self._search_based_title(query)
        based_bm25_candidates = self._search_based_bm25(query)
        is_normalized_match = bool(original_question and query != original_question)
        for document in based_vector_candidates + based_title_candidates + based_bm25_candidates:
            document.metadata = dict(document.metadata or {})
            document.metadata["matched_by_normalized_query"] = is_normalized_match
        return based_vector_candidates + based_title_candidates + based_bm25_candidates

    def rerank_candidates(
        self,
        original_question: str,
        candidates: List[Document],
        *,
        use_reranker: bool = True,
    ) -> List[Document]:
        """Use only the original user question for final semantic rerank and MMR."""
        return self._reranking(candidates, original_question, use_reranker=use_reranker)

    def retrieval(
        self,
        user_question: str | None = None,
        *,
        original_question: str | None = None,
        query_variants: list[str] | None = None,
    ) -> List[Document]:
        original_question = (original_question or user_question or "").strip()
        if not original_question:
            return []

        variants = self._normalize_query_variants(original_question, query_variants)
        all_candidates: List[Document] = []
        for query in variants:
            all_candidates.extend(self.retrieve_candidates(query, original_question=original_question))

        candidate_count_before_dedup = len(all_candidates)
        unique_candidates = self._deduplicate(all_candidates)
        final_documents = self.rerank_candidates(original_question, unique_candidates)

        for document in final_documents:
            document.metadata = dict(document.metadata or {})
            document.metadata["query_variants"] = list(variants)

        top_score = max(
            (float(doc.metadata.get("final_rerank_score", 0.0)) for doc in final_documents),
            default=None,
        )
        accepted = top_score is not None and top_score >= settings.RAG_MIN_RERANK_SCORE
        logger.info(
            "RAG retrieval decision original_question=%s query_variants=%s "
            "candidate_count_before_dedup=%s candidate_count_after_dedup=%s "
            "top_score=%s threshold=%s result=%s",
            original_question,
            variants,
            candidate_count_before_dedup,
            len(unique_candidates),
            top_score,
            settings.RAG_MIN_RERANK_SCORE,
            "accepted" if accepted else "rejected",
        )
        if not accepted:
            return []
        if self.is_anchor_evidence_enabled():
            decision = self.evaluate_anchor_gate(original_question, final_documents)
            if not decision.get("ok", True):
                logger.info(
                    "RAG retrieval blocked by anchor evidence original_question=%s reason_code=%s anchors=%s",
                    original_question,
                    decision.get("reason_code"),
                    decision.get("anchor_evidence", {}).get("anchors"),
                )
                return []
        return final_documents

    def retrieval_fast_local(
        self,
        original_question: str,
        *,
        query_variants: list[str] | None = None,
        top_k: int | None = None,
        candidate_top_k: int | None = None,
    ) -> List[Document]:
        """Fast local retrieval for online agent tools.

        The full retrieval pipeline performs title semantic ranking and
        candidate embedding rerank, which can issue many remote embedding
        requests. This online path keeps the useful semantic recall signal by
        asking Chroma once for the original question, then combines it with
        local BM25 over all query variants and deterministic title/content
        evidence scoring. It does not run title embedding, candidate embedding
        rerank, Reranker, or the answer LLM.
        """
        original_question = (original_question or "").strip()
        if not original_question:
            return []

        variants = self._normalize_query_variants(original_question, query_variants)
        top_k = int(top_k or settings.RAG_FINAL_TOP_K)
        candidate_top_k = int(candidate_top_k or max(settings.RAG_BM25_CANDIDATE_TOP_K, 10))

        repository = self._get_fast_bm25_repository()
        candidates: list[Document] = []
        candidates.extend(self._search_based_vector(original_question))
        for query in variants:
            candidates.extend(repository.search(query, top_k=candidate_top_k, query_variant=query))

        unique_candidates = self._deduplicate(candidates)
        if not unique_candidates:
            return []

        terms = self._fast_query_terms(variants)
        scored: list[tuple[Document, float]] = []
        for document in unique_candidates:
            document.metadata = dict(document.metadata or {})
            score = self._fast_local_score(document, terms)
            document.metadata["ranking_base_score"] = float(score)
            document.metadata["final_rerank_score"] = float(score)
            document.metadata["retrieval_route"] = document.metadata.get("retrieval_route") or "bm25"
            document.metadata["retrieval_routes"] = list(document.metadata.get("retrieval_routes") or ["bm25"])
            scored.append((document, score))

        scored.sort(key=lambda item: item[1], reverse=True)
        selected = [doc for doc, score in scored if score > 0][:top_k]
        for rank, document in enumerate(selected, start=1):
            document.metadata = dict(document.metadata or {})
            document.metadata["final_rank"] = rank
            document.metadata["query_variants"] = list(variants)
        return selected

    def _get_fast_bm25_repository(self) -> Bm25Repository:
        if self._fast_bm25_repository is None:
            repository = Bm25Repository()
            repository.load_index()
            self._fast_bm25_repository = repository
        return self._fast_bm25_repository

    def _fast_query_terms(self, query_variants: list[str]) -> list[str]:
        stop_terms = {
            "怎么",
            "怎么办",
            "如何",
            "电脑",
            "系统",
            "问题",
            "故障",
            "处理",
            "解决",
            "win",
        }
        terms: list[str] = []
        seen: set[str] = set()
        for query in query_variants:
            for item in re.findall(r"0x[0-9A-Fa-f]+|[A-Za-z]+[0-9.]*|[\u4e00-\u9fff]{2,}", query or ""):
                normalized = item.strip().lower()
                if not normalized or normalized in stop_terms or normalized in seen:
                    continue
                seen.add(normalized)
                terms.append(normalized)
            for item in jieba.lcut(query or ""):
                normalized = item.strip().lower()
                if len(normalized) < 2 or normalized in stop_terms or normalized in seen:
                    continue
                if not re.search(r"[\u4e00-\u9fffA-Za-z0-9]", normalized):
                    continue
                seen.add(normalized)
                terms.append(normalized)
        return terms

    def _fast_local_score(self, document: Document, terms: list[str]) -> float:
        metadata = document.metadata or {}
        title = str(metadata.get("title") or "")
        content = str(document.page_content or "")
        title_norm = title.lower()
        content_norm = content.lower()
        bm25_score = float(metadata.get("bm25_score") or 0.0)

        title_hits = 0
        content_hits = 0
        for term in terms:
            if term and term in title_norm:
                title_hits += 1
            if term and term in content_norm:
                content_hits += 1

        score = bm25_score + title_hits * 10.0 + content_hits * 1.5
        if "黑屏" in terms and "黑屏" in title:
            score += 15.0
        if any(term in terms for term in ("开机", "启动", "无法开机")) and any(term in title for term in ("开机", "启动")):
            score += 8.0
        if any(term in terms for term in ("蓝屏", "错误码")) and any(term in title for term in ("蓝屏", "错误")):
            score += 8.0
        if any(term in terms for term in ("无线网络", "wi-fi", "wifi", "网络")) and any(term in title for term in ("无线", "网络", "Wi-Fi", "wifi")):
            score += 8.0
        return score

    def is_anchor_evidence_enabled(self) -> bool:
        return bool(getattr(self, "anchor_evidence_enabled", False))

    def evaluate_anchor_gate(self, original_question: str, documents: List[Document]) -> dict[str, Any]:
        if not self.is_anchor_evidence_enabled() or not getattr(self, "anchor_require_evidence_for_block", True):
            return {"ok": True, "reason_code": None}
        if self.anchor_evidence_mode == "hard-soft-negative":
            return evaluate_hard_soft_negative_gate(
                original_question,
                documents,
                getattr(self, "_last_anchor_window_documents", []) or documents,
            ).as_dict()
        return evaluate_retrieval_evidence(original_question, documents).as_dict()

    def _normalize_query_variants(self, original_question: str, query_variants: list[str] | None) -> list[str]:
        raw_variants = query_variants or [original_question]
        variants = []
        seen = set()
        for query in [original_question, *raw_variants]:
            normalized = re.sub(r"\s+", " ", (query or "").strip())
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            variants.append(normalized)
        return variants

    def _search_based_vector(self, user_question: str) -> List[Document]:
        documents_with_score = self.chroma_vector.search_similarity_with_score(user_question)
        candidates = []
        for document, chroma_distance in documents_with_score:
            if self._is_valid_document(document):
                document.metadata = dict(document.metadata or {})
                document.metadata["retrieval_route"] = "vector"
                try:
                    document.metadata["chroma_distance"] = float(chroma_distance)
                except (TypeError, ValueError):
                    document.metadata["chroma_distance"] = None
                candidates.append(document)
        return candidates

    def _search_based_bm25(self, user_query: str) -> List[Document]:
        if self.bm25_mode != "experimental":
            return []
        if self.bm25_repository is None:
            raise RuntimeError("BM25 experimental mode requires a BM25 repository")
        documents = self.bm25_repository.search(
            user_query,
            top_k=settings.RAG_BM25_CANDIDATE_TOP_K,
            query_variant=user_query,
        )
        for document in documents:
            document.metadata = dict(document.metadata or {})
            document.metadata["retrieval_route"] = "bm25"
        return [document for document in documents if self._is_valid_document(document)]

    def _search_based_title(self, user_query: str) -> List[Document]:
        mds_metadata = MarkDownUtils.collect_md_metadata(settings.CRAWL_OUTPUT_DIR)
        rough_mds_metadata = self.rough_ranking(user_query, mds_metadata)
        fine_mds_metadata = self.fine_ranking(user_query, rough_mds_metadata)
        candidates = []

        for fine_md_metadata in fine_mds_metadata:
            try:
                file_path = fine_md_metadata.get("path", "")
                if not file_path:
                    continue
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                if not content:
                    continue

                if len(content) < 3000:
                    doc = self._build_title_document(content, fine_md_metadata, chunk_index=0)
                    if self._is_valid_document(doc):
                        candidates.append(doc)
                else:
                    candidates.extend(self._deal_long_title_content(content, fine_md_metadata, user_query))
            except Exception as e:
                logger.error("Failed to read title route markdown file: %s", e)

        return candidates

    def _build_title_document(self, content: str, metadata: Dict[str, Any], chunk_index: int) -> Document:
        file_path = metadata.get("path", "")
        source_id = self._source_id_from_path(file_path)
        document_id = build_document_id(source_id)
        canonical_text = build_embedding_text(metadata.get("title") or os.path.basename(file_path), content)
        return Document(
            page_content=canonical_text,
            metadata={
                "path": file_path,
                "source_path": file_path,
                "source_id": source_id,
                "document_id": document_id,
                "title": metadata.get("title", ""),
                "chunk_index": chunk_index,
                "retrieval_route": "title",
                "title_rough_score": float(metadata.get("roughing_score", 0)),
                "title_semantic_score": float(metadata.get("sim_score", 0)),
                "title_final_score": float(metadata.get("final_score", 0)),
            },
        )

    def _deduplicate(self, total_candidates: List[Document]) -> List[Document]:
        seen = set()
        unique_candidates = []
        existing_by_key = {}
        for document in total_candidates:
            if not self._is_valid_document(document):
                continue
            title = document.metadata.get("title", "")
            canonical_text = build_embedding_text(title, document.page_content)
            key = document.metadata.get("chunk_id") or (
                document.metadata.get("document_id"),
                build_content_hash(canonical_text),
            )
            if key not in seen:
                seen.add(key)
                document.metadata = dict(document.metadata or {})
                route = document.metadata.get("retrieval_route")
                document.metadata["retrieval_routes"] = [route] if route else []
                if route == "bm25" and document.metadata.get("bm25_query_variants"):
                    document.metadata["bm25_query_variants"] = list(document.metadata.get("bm25_query_variants") or [])
                existing_by_key[key] = document
                unique_candidates.append(document)
            else:
                existing = existing_by_key[key]
                existing.metadata = dict(existing.metadata or {})
                route = document.metadata.get("retrieval_route")
                routes = list(existing.metadata.get("retrieval_routes") or [])
                if route and route not in routes:
                    routes.append(route)
                existing.metadata["retrieval_routes"] = routes
                existing.metadata["matched_by_normalized_query"] = bool(
                    existing.metadata.get("matched_by_normalized_query")
                    or document.metadata.get("matched_by_normalized_query")
                )
                if document.metadata.get("bm25_score") is not None:
                    existing.metadata["bm25_score"] = max(
                        float(existing.metadata.get("bm25_score") or 0.0),
                        float(document.metadata.get("bm25_score") or 0.0),
                    )
                    existing.metadata["matched_by_bm25_query"] = document.metadata.get("matched_by_bm25_query")
                    variants = list(existing.metadata.get("bm25_query_variants") or [])
                    for variant in document.metadata.get("bm25_query_variants") or []:
                        if variant not in variants:
                            variants.append(variant)
                    existing.metadata["bm25_query_variants"] = variants
        return unique_candidates

    def _reranking(
        self,
        unique_candidates: List[Document],
        user_question: str,
        *,
        use_reranker: bool = True,
    ) -> List[Document]:
        candidates = [doc for doc in unique_candidates if self._is_valid_document(doc)]
        if not candidates:
            return []

        canonical_texts = []
        valid_candidates = []
        for doc in candidates:
            canonical_text = build_embedding_text(doc.metadata.get("title", ""), doc.page_content)
            if not has_effective_content(canonical_text):
                continue
            canonical_texts.append(canonical_text)
            doc.page_content = canonical_text
            valid_candidates.append(doc)

        if not valid_candidates:
            return []

        query_embedding = self.chroma_vector.embedd_document(user_question)
        candidate_embeddings = self.chroma_vector.embedd_documents(canonical_texts)
        similarities = cosine_similarity([query_embedding], candidate_embeddings).flatten()

        scored = []
        for index, doc in enumerate(valid_candidates):
            score = max(float(similarities[index]), 0.0)
            doc.metadata = dict(doc.metadata or {})
            doc.metadata["embedding_rerank_score"] = score
            doc.metadata["ranking_base_score"] = score
            doc.metadata["final_rerank_score"] = score
            doc.metadata["canonical_embedding_text_hash"] = build_content_hash(canonical_texts[index])
            scored.append((doc, score, candidate_embeddings[index]))

        if use_reranker and self.reranker_mode == "experimental":
            scored = self._apply_experimental_reranker(user_question, scored)

        if self.is_anchor_evidence_enabled():
            apply_anchor_adjustment(
                user_question,
                [doc for doc, _, _ in scored],
                match_boost=getattr(self, "anchor_match_boost", settings.RAG_ANCHOR_MATCH_BOOST),
                missing_penalty=getattr(self, "anchor_missing_penalty", settings.RAG_ANCHOR_MISSING_PENALTY),
                hard_match_boost=settings.RAG_HARD_ANCHOR_MATCH_BOOST,
                hard_missing_penalty=settings.RAG_HARD_ANCHOR_MISSING_PENALTY,
                soft_match_boost=settings.RAG_SOFT_ANCHOR_MATCH_BOOST
                if self.anchor_evidence_mode == "hard-soft-negative"
                else getattr(self, "anchor_match_boost", settings.RAG_ANCHOR_MATCH_BOOST),
                soft_missing_penalty=settings.RAG_SOFT_ANCHOR_MISSING_PENALTY
                if self.anchor_evidence_mode == "hard-soft-negative"
                else getattr(self, "anchor_missing_penalty", settings.RAG_ANCHOR_MISSING_PENALTY),
                negative_match_penalty=settings.RAG_NEGATIVE_ANCHOR_MATCH_PENALTY,
            )
            scored = [
                (doc, float(doc.metadata.get("evidence_adjusted_score", score)), embedding)
                for doc, score, embedding in scored
            ]

        scored.sort(key=lambda item: item[1], reverse=True)
        window_size = max(int(getattr(self, "anchor_evidence_window_size", settings.RAG_ANCHOR_EVIDENCE_WINDOW_SIZE)), settings.RAG_FINAL_TOP_K)
        self._last_anchor_window_documents = [doc for doc, _, _ in scored[:window_size]]
        for rank, doc in enumerate(self._last_anchor_window_documents, start=1):
            doc.metadata = dict(doc.metadata or {})
            doc.metadata["anchor_candidate_window_rank"] = rank
        selected = self._select_mmr(scored, settings.RAG_FINAL_TOP_K)
        for rank, (doc, mmr_score) in enumerate(selected, start=1):
            doc.metadata["mmr_score"] = float(mmr_score)
            doc.metadata["final_rank"] = rank
        return [doc for doc, _ in selected]

    def _apply_experimental_reranker(
        self,
        user_question: str,
        scored: list[tuple[Document, float, list[float]]],
    ) -> list[tuple[Document, float, list[float]]]:
        if not scored:
            return scored
        if self.reranker_repository is None:
            raise RuntimeError("Reranker experimental mode requires a reranker repository")
        documents = [
            self._build_reranker_document_text(doc)
            for doc, _, _ in scored
        ]
        try:
            results = self.reranker_repository.rerank(
                user_question,
                documents,
                top_n=len(documents),
            )
        except Exception:
            self.reranker_failure_count += 1
            raise
        if len(results) != len(scored):
            self.reranker_invalid_result_count += 1
            raise RuntimeError(
                f"Reranker returned {len(results)} results for {len(scored)} candidates"
            )
        result_by_index = {result.candidate_index: result for result in results}
        if len(result_by_index) != len(results):
            self.reranker_invalid_result_count += 1
            raise RuntimeError("Reranker returned duplicate candidate indexes")

        reranked = []
        for index, (doc, _, embedding) in enumerate(scored):
            result = result_by_index.get(index)
            if result is None:
                self.reranker_invalid_result_count += 1
                raise RuntimeError(f"Reranker missing candidate index {index}")
            doc.metadata = dict(doc.metadata or {})
            doc.metadata["reranker_provider"] = getattr(self.reranker_repository, "provider", "unknown")
            doc.metadata["reranker_model"] = getattr(self.reranker_repository, "model", settings.RAG_RERANKER_MODEL)
            doc.metadata["reranker_score"] = float(result.reranker_score)
            doc.metadata["reranker_rank"] = int(result.rank)
            doc.metadata["ranking_base_score"] = float(result.reranker_score)
            doc.metadata["final_rerank_score"] = float(result.reranker_score)
            reranked.append((doc, float(result.reranker_score), embedding))

        call_stats = getattr(self.reranker_repository, "last_call_stats", None)
        if call_stats is not None:
            self.reranker_latency_ms.append(int(call_stats.duration_ms))
        self.reranker_success_count += 1
        return reranked

    def _build_reranker_document_text(self, document: Document) -> str:
        metadata = document.metadata or {}
        title = str(metadata.get("title") or "").strip()
        keywords = metadata.get("keywords") or metadata.get("keyword") or metadata.get("tags") or []
        if isinstance(keywords, str):
            keyword_text = keywords.strip()
        elif isinstance(keywords, (list, tuple, set)):
            keyword_text = " ".join(str(item).strip() for item in keywords if str(item).strip())
        else:
            keyword_text = ""
        content = strip_existing_source_prefixes(document.page_content or "")
        max_chars = max(int(settings.RAG_RERANKER_MAX_DOCUMENT_CHARS), 200)
        if len(content) > max_chars:
            content = content[:max_chars]
        parts = []
        if title:
            parts.append(f"标题:\n{title}")
        if keyword_text:
            parts.append(f"关键词:\n{keyword_text}")
        parts.append(f"正文:\n{content}")
        return "\n\n".join(parts).strip()

    def _select_mmr(self, scored: list[tuple[Document, float, list[float]]], top_k: int) -> list[tuple[Document, float]]:
        if not scored or top_k <= 0:
            return []

        selected: list[tuple[Document, float, list[float], float]] = []
        remaining = list(scored)
        first = remaining.pop(0)
        selected.append((first[0], first[1], first[2], first[1]))

        while remaining and len(selected) < top_k:
            best_index = None
            best_score = None
            for idx, (doc, relevance, embedding) in enumerate(remaining):
                if not self._can_select_document(doc, selected):
                    continue
                max_similarity = max(
                    float(cosine_similarity([embedding], [selected_doc[2]]).flatten()[0])
                    for selected_doc in selected
                )
                mmr_score = settings.RAG_MMR_LAMBDA * relevance - (1 - settings.RAG_MMR_LAMBDA) * max_similarity
                if best_score is None or mmr_score > best_score:
                    best_score = mmr_score
                    best_index = idx

            if best_index is None:
                best_index = 0
                doc, relevance, embedding = remaining[best_index]
                best_score = relevance
            doc, relevance, embedding = remaining.pop(best_index)
            selected.append((doc, relevance, embedding, float(best_score)))

        return [(doc, mmr_score) for doc, _, _, mmr_score in selected]

    def _can_select_document(self, doc: Document, selected: list[tuple[Document, float, list[float], float]]) -> bool:
        max_chunks = settings.RAG_MAX_CHUNKS_PER_DOCUMENT
        if max_chunks <= 0:
            return True
        document_id = doc.metadata.get("document_id")
        if not document_id:
            return True
        count = sum(1 for selected_doc, *_ in selected if selected_doc.metadata.get("document_id") == document_id)
        return count < max_chunks

    def _deal_long_title_content(self, content: str, fine_md_metadata: Dict[str, Any], user_query: str) -> List[Document]:
        chunks = self.spliter.document_spliter.split_text(strip_existing_source_prefixes(content))
        valid_chunks = [chunk.strip() for chunk in chunks if self._is_effective_chunk(chunk)]
        if not valid_chunks:
            return []

        title = fine_md_metadata.get("title", "")
        canonical_chunks = [build_embedding_text(title, chunk) for chunk in valid_chunks]
        query_embedding = self.chroma_vector.embedd_document(user_query)
        chunk_embeddings = self.chroma_vector.embedd_documents(canonical_chunks)
        similarities = cosine_similarity([query_embedding], chunk_embeddings).flatten()
        top_indices = similarities.argsort()[-3:][::-1]

        docs = []
        for rank, chunk_idx in enumerate(top_indices):
            doc = self._build_title_document(canonical_chunks[int(chunk_idx)], fine_md_metadata, chunk_index=int(chunk_idx))
            doc.metadata["rank"] = int(rank + 1)
            doc.metadata["similarity"] = float(similarities[chunk_idx])
            if self._is_valid_document(doc):
                docs.append(doc)
        return docs

    def _clean_content_for_compare(self, content: str) -> str:
        clean_content = strip_existing_source_prefixes(content or "")
        clean_content = re.sub(r"<!--.*?-->", "", clean_content, flags=re.DOTALL).strip()
        clean_content = re.sub(r"^\*\*.*?$", "", clean_content, flags=re.MULTILINE).strip()
        return clean_content

    def _is_effective_chunk(self, chunk: str) -> bool:
        clean = self._clean_content_for_compare(chunk)
        lines = [line.strip() for line in clean.splitlines() if line.strip()]
        if not lines:
            return False
        if len(lines) == 1 and lines[0].startswith("#"):
            return False
        return len("\n".join(lines)) >= 50

    def _is_valid_document(self, document: Document) -> bool:
        if not document or not document.page_content:
            return False
        clean_content = self._clean_content_for_compare(document.page_content)
        if not clean_content:
            return False
        lines = [line.strip() for line in clean_content.splitlines() if line.strip()]
        if not lines:
            return False
        if len(lines) == 1 and lines[0].startswith("#"):
            return False
        plain_text = "\n".join(lines)
        plain_text_no_link = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", plain_text)
        return len(plain_text_no_link) >= 50

    def _source_id_from_path(self, file_path: str) -> str:
        try:
            return os.path.normpath(os.path.relpath(file_path, settings.CRAWL_OUTPUT_DIR)).replace("\\", "/")
        except Exception:
            return os.path.basename(file_path)


if __name__ == "__main__":
    retrieval_service = RetrievalService()
    result = retrieval_service.retrieval("开机屏幕黑屏或蓝屏报错,无法正常进入系统怎么办")
    for doc in result:
        print("标题:", doc.metadata.get("title"))
        print("来源:", doc.metadata.get("source") or doc.metadata.get("path"))
        print("分数:", doc.metadata.get("final_rerank_score"))
        print(doc.page_content[:1000])
        print("=" * 80)

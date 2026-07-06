from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any, Sequence

import requests

from config.settings import settings


logger = logging.getLogger(__name__)


RERANK_INSTRUCTION = (
    "请根据用户问题，对候选知识库资料按直接解决问题的相关性排序。"
    "优先选择具体、可执行、与问题对象和故障现象一致的资料。"
)


class RerankerError(RuntimeError):
    pass


@dataclass(frozen=True)
class RerankCandidateResult:
    candidate_index: int
    document_id: str
    chunk_id: str
    reranker_score: float
    rank: int


@dataclass(frozen=True)
class RerankerCallStats:
    provider: str
    model: str
    candidate_count: int
    duration_ms: int
    http_status: int | None
    result_count: int
    trace_id: str | None = None


class SiliconFlowRerankerRepository:
    provider = "siliconflow"

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        timeout_seconds: int | None = None,
        session: Any | None = None,
    ) -> None:
        self.api_key = api_key or settings.SILICONFLOW_API_KEY
        self.base_url = (base_url or settings.RAG_RERANKER_BASE_URL).rstrip("/")
        self.model = model or settings.RAG_RERANKER_MODEL
        self.timeout_seconds = timeout_seconds or settings.RAG_RERANKER_TIMEOUT_SECONDS
        self.session = session or requests
        self.last_call_stats: RerankerCallStats | None = None

    @property
    def endpoint(self) -> str:
        return f"{self.base_url}/rerank"

    def rerank(self, query: str, documents: Sequence[str], *, top_n: int | None = None) -> list[RerankCandidateResult]:
        if not self.api_key:
            raise RerankerError("SILICONFLOW_API_KEY is not configured")
        if not self.model:
            raise RerankerError("RAG_RERANKER_MODEL is not configured")
        if not query or not query.strip():
            raise RerankerError("reranker query is empty")
        if not documents:
            return []

        safe_documents = [str(document or "") for document in documents]
        payload = {
            "model": self.model,
            "query": query.strip(),
            "documents": safe_documents,
            "instruction": RERANK_INSTRUCTION,
            "top_n": int(top_n or len(safe_documents)),
            "return_documents": False,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        started = time.perf_counter()
        http_status = None
        trace_id = None
        try:
            response = self.session.post(
                self.endpoint,
                headers=headers,
                json=payload,
                timeout=self.timeout_seconds,
            )
            http_status = getattr(response, "status_code", None)
            trace_id = self._extract_trace_id(response)
            if http_status != 200:
                raise RerankerError(f"SiliconFlow reranker HTTP {http_status}: {self._safe_error_text(response)}")
            try:
                response_json = response.json()
            except ValueError as exc:
                raise RerankerError("SiliconFlow reranker response is not valid JSON") from exc
            results = self._parse_results(response_json, document_count=len(safe_documents))
            self.last_call_stats = RerankerCallStats(
                provider=self.provider,
                model=self.model,
                candidate_count=len(safe_documents),
                duration_ms=int((time.perf_counter() - started) * 1000),
                http_status=http_status,
                result_count=len(results),
                trace_id=trace_id,
            )
            logger.info(
                "reranker_call provider=%s model=%s candidates=%s status=%s results=%s duration_ms=%s trace_id=%s",
                self.provider,
                self.model,
                len(safe_documents),
                http_status,
                len(results),
                self.last_call_stats.duration_ms,
                trace_id,
            )
            return results
        except requests.Timeout as exc:
            raise RerankerError("SiliconFlow reranker timeout") from exc
        except requests.RequestException as exc:
            raise RerankerError(f"SiliconFlow reranker network error: {exc.__class__.__name__}") from exc

    def _parse_results(self, response_json: Any, *, document_count: int) -> list[RerankCandidateResult]:
        if not isinstance(response_json, dict):
            raise RerankerError("SiliconFlow reranker response schema invalid: root is not object")
        raw_results = response_json.get("results")
        if not isinstance(raw_results, list):
            raise RerankerError("SiliconFlow reranker response schema invalid: results is not list")

        seen_indexes: set[int] = set()
        parsed: list[tuple[int, float]] = []
        for raw in raw_results:
            if not isinstance(raw, dict):
                raise RerankerError("SiliconFlow reranker response schema invalid: result item is not object")
            if "index" not in raw:
                raise RerankerError("SiliconFlow reranker response schema invalid: missing index")
            if "relevance_score" not in raw:
                raise RerankerError("SiliconFlow reranker response schema invalid: missing relevance_score")
            index = raw["index"]
            if not isinstance(index, int):
                raise RerankerError("SiliconFlow reranker response schema invalid: index is not int")
            if index < 0 or index >= document_count:
                raise RerankerError("SiliconFlow reranker response schema invalid: index out of range")
            if index in seen_indexes:
                raise RerankerError("SiliconFlow reranker response schema invalid: duplicate index")
            seen_indexes.add(index)
            try:
                score = float(raw["relevance_score"])
            except (TypeError, ValueError) as exc:
                raise RerankerError("SiliconFlow reranker response schema invalid: relevance_score is not numeric") from exc
            parsed.append((index, score))

        parsed.sort(key=lambda item: item[1], reverse=True)
        return [
            RerankCandidateResult(
                candidate_index=index,
                document_id="",
                chunk_id="",
                reranker_score=score,
                rank=rank,
            )
            for rank, (index, score) in enumerate(parsed, start=1)
        ]

    def _extract_trace_id(self, response: Any) -> str | None:
        headers = getattr(response, "headers", None) or {}
        for key in ("x-request-id", "x-trace-id", "x-sf-request-id"):
            value = headers.get(key) if hasattr(headers, "get") else None
            if value:
                return str(value)
        return None

    def _safe_error_text(self, response: Any) -> str:
        text = getattr(response, "text", "") or ""
        text = " ".join(str(text).split())
        if len(text) > 240:
            text = text[:240] + "..."
        return text

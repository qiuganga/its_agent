from __future__ import annotations

import json
import math
import os
import re
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import jieba
from langchain_core.documents import Document

from config.settings import settings


TOKENIZER_NAME = "jieba_with_exact_anchor_tokens"
TOKENIZER_VERSION = "v1"


EXACT_TOKEN_PATTERN = re.compile(
    r"0x[0-9A-Fa-f]+"
    r"|[A-Za-z]+(?:\s+[A-Za-z0-9]+){0,3}"
    r"|[A-Za-z]+[0-9]+[A-Za-z0-9]*"
    r"|[0-9]+[A-Za-z]+[A-Za-z0-9]*"
    r"|[\u4e00-\u9fffA-Za-z0-9]+(?:\s+[\u4e00-\u9fffA-Za-z0-9]+){1,5}"
)


@dataclass(frozen=True)
class Bm25IndexMetadata:
    index_name: str
    index_path: str
    chunk_count: int
    source_document_count: int
    chunk_size: int
    chunk_overlap: int


def default_index_dir(index_name: str = "clean-v1") -> Path:
    root = Path(__file__).resolve().parents[1]
    return root / "bm25_kb" / index_name


def bm25_root_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "bm25_kb"


def normalize_token(token: str) -> str:
    return re.sub(r"\s+", " ", (token or "").strip()).lower()


def strip_non_content_noise(text: str) -> str:
    text = text or ""
    text = re.sub(r"https?://[^\s)>\]]+", " ", text)
    text = re.sub(r"!\[[^\]]*]\([^)]+\)", " ", text)
    text = re.sub(r"(?<!!)\[([^\]]+)]\((https?://[^)]+)\)", r"\1", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.DOTALL)
    text = re.sub(r"[A-Za-z]:\\[^\s]+", " ", text)
    text = re.sub(r"source_id\s*[:=]\s*\S+", " ", text, flags=re.I)
    text = re.sub(r"collection[_-]?\w*\s*[:=]\s*\S+", " ", text, flags=re.I)
    text = re.sub(r"\b[a-f0-9]{32,64}\b", " ", text, flags=re.I)
    return text


def tokenize_for_bm25(text: str, *, title: str | None = None) -> list[str]:
    combined = strip_non_content_noise(text)
    tokens: list[str] = []

    for exact in EXACT_TOKEN_PATTERN.findall(combined):
        normalized = normalize_token(exact)
        if len(normalized) >= 2:
            tokens.append(normalized)

    for item in jieba.lcut(combined):
        normalized = normalize_token(item)
        if len(normalized) >= 2 and re.search(r"[\u4e00-\u9fffA-Za-z0-9]", normalized):
            tokens.append(normalized)

    if title:
        clean_title = strip_non_content_noise(title)
        for item in EXACT_TOKEN_PATTERN.findall(clean_title):
            normalized = normalize_token(item)
            if len(normalized) >= 2:
                tokens.append(normalized)
        for item in jieba.lcut(clean_title):
            normalized = normalize_token(item)
            if len(normalized) >= 2 and re.search(r"[\u4e00-\u9fffA-Za-z0-9]", normalized):
                tokens.append(normalized)

    return tokens


class Bm25Repository:
    def __init__(self, index_dir: str | Path | None = None):
        self.index_dir = Path(index_dir) if index_dir else default_index_dir()
        self.index_file = self.index_dir / "index.json"
        self.manifest_file = self.index_dir / "manifest.json"
        self.documents: list[dict[str, Any]] = []
        self.doc_freq: dict[str, int] = {}
        self.avg_doc_len = 0.0
        self.metadata: Bm25IndexMetadata | None = None

    def build_index(
        self,
        documents: list[Document],
        *,
        index_name: str,
        chunk_size: int,
        chunk_overlap: int,
        collection_reference: str,
        collection_chunk_count: int | None,
        rebuild: bool = False,
    ) -> dict[str, Any]:
        if self.index_dir.exists() and any(self.index_dir.iterdir()) and not rebuild:
            raise FileExistsError(f"BM25 index already exists: {self.index_dir}. Pass --rebuild to overwrite it.")
        resolved = self.index_dir.resolve()
        allowed_root = bm25_root_dir().resolve()
        if resolved != allowed_root and allowed_root not in resolved.parents:
            raise ValueError(f"Refuse to write outside BM25 experiment root: {resolved}")

        self.index_dir.mkdir(parents=True, exist_ok=True)
        if rebuild:
            for child in self.index_dir.glob("*"):
                if child.is_file():
                    child.unlink()

        indexed_docs = []
        missing_source = 0
        doc_freq: Counter[str] = Counter()
        source_ids = set()
        for doc in documents:
            metadata = dict(doc.metadata or {})
            source_id = metadata.get("source_id")
            if not source_id:
                missing_source += 1
                continue
            source_ids.add(source_id)
            title = metadata.get("title") or ""
            tokens = tokenize_for_bm25(doc.page_content, title=title)
            token_counts = Counter(tokens)
            doc_freq.update(token_counts.keys())
            indexed_docs.append({
                "source_id": source_id,
                "document_id": metadata.get("document_id"),
                "chunk_id": metadata.get("chunk_id"),
                "chunk_index": metadata.get("chunk_index"),
                "title": title,
                "page_content": doc.page_content,
                "metadata": metadata,
                "tokens": tokens,
                "token_counts": dict(token_counts),
                "doc_len": len(tokens),
            })

        if any(item.get("source_id") is None for item in indexed_docs):
            raise ValueError("BM25 index contains source_id=None")
        if not indexed_docs:
            raise ValueError("BM25 index has no documents")

        avg_doc_len = sum(item["doc_len"] for item in indexed_docs) / len(indexed_docs)
        payload = {
            "schema_version": "bm25-clean-v1",
            "tokenizer_name": TOKENIZER_NAME,
            "tokenizer_version": TOKENIZER_VERSION,
            "index_name": index_name,
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap,
            "collection_reference": collection_reference,
            "collection_chunk_count": collection_chunk_count,
            "documents": indexed_docs,
            "doc_freq": dict(doc_freq),
            "avg_doc_len": avg_doc_len,
        }
        self.index_file.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        manifest = self._build_manifest(
            payload,
            source_document_count=len(source_ids),
            source_id_missing_count=missing_source,
        )
        self.manifest_file.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        self.documents = indexed_docs
        self.doc_freq = dict(doc_freq)
        self.avg_doc_len = avg_doc_len
        return manifest

    def load_index(self) -> None:
        if not self.index_file.exists():
            raise FileNotFoundError(f"BM25 index not found: {self.index_file}")
        payload = json.loads(self.index_file.read_text(encoding="utf-8"))
        self.documents = payload.get("documents") or []
        self.doc_freq = payload.get("doc_freq") or {}
        self.avg_doc_len = float(payload.get("avg_doc_len") or 0.0)
        self.metadata = Bm25IndexMetadata(
            index_name=payload.get("index_name") or self.index_dir.name,
            index_path=str(self.index_dir),
            chunk_count=len(self.documents),
            source_document_count=len({doc.get("source_id") for doc in self.documents if doc.get("source_id")}),
            chunk_size=int(payload.get("chunk_size") or 0),
            chunk_overlap=int(payload.get("chunk_overlap") or 0),
        )
        self.validate_manifest()

    def validate_manifest(self) -> dict[str, Any]:
        if not self.manifest_file.exists():
            raise FileNotFoundError(f"BM25 manifest not found: {self.manifest_file}")
        manifest = json.loads(self.manifest_file.read_text(encoding="utf-8"))
        if manifest.get("source_id_missing_count"):
            raise ValueError(f"BM25 manifest has missing source_id: {manifest['source_id_missing_count']}")
        if manifest.get("chunk_count") != len(self.documents):
            raise ValueError("BM25 manifest chunk_count does not match loaded index")
        if manifest.get("chunk_count_match") is False:
            raise ValueError(f"BM25 chunk count mismatch: {manifest.get('mismatch_reason')}")
        return manifest

    def metadata_report(self) -> dict[str, Any]:
        if not self.documents:
            self.load_index()
        manifest = json.loads(self.manifest_file.read_text(encoding="utf-8"))
        return dict(manifest)

    def search(self, query: str, *, top_k: int = 10, query_variant: str | None = None) -> list[Document]:
        if not self.documents:
            self.load_index()
        query_tokens = tokenize_for_bm25(query)
        if not query_tokens:
            return []
        scores = []
        n_docs = len(self.documents)
        avg_len = self.avg_doc_len or 1.0
        k1 = 1.5
        b = 0.75
        for item in self.documents:
            counts = item.get("token_counts") or {}
            doc_len = float(item.get("doc_len") or 0.0) or 1.0
            score = 0.0
            for token in query_tokens:
                tf = float(counts.get(token) or 0.0)
                if tf <= 0:
                    continue
                df = float(self.doc_freq.get(token) or 0.0)
                idf = math.log(1 + (n_docs - df + 0.5) / (df + 0.5))
                score += idf * (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * doc_len / avg_len))
            if score > 0:
                metadata = dict(item.get("metadata") or {})
                metadata.update({
                    "retrieval_route": "bm25",
                    "bm25_score": float(score),
                    "matched_by_bm25_query": query_variant or query,
                    "bm25_query_variants": [query_variant or query],
                })
                scores.append((score, Document(page_content=item.get("page_content") or "", metadata=metadata)))
        scores.sort(key=lambda pair: pair[0], reverse=True)
        return [doc for _, doc in scores[:top_k]]

    def _build_manifest(
        self,
        payload: dict[str, Any],
        *,
        source_document_count: int,
        source_id_missing_count: int,
    ) -> dict[str, Any]:
        collection_chunk_count = payload.get("collection_chunk_count")
        chunk_count = len(payload.get("documents") or [])
        chunk_count_match = collection_chunk_count is None or int(collection_chunk_count) == chunk_count
        return {
            "index_name": payload["index_name"],
            "index_path": str(self.index_dir),
            "cleaning_version": "clean-v1",
            "chunk_size": payload["chunk_size"],
            "chunk_overlap": payload["chunk_overlap"],
            "source_document_count": source_document_count,
            "chunk_count": chunk_count,
            "tokenizer_name": TOKENIZER_NAME,
            "tokenizer_version": TOKENIZER_VERSION,
            "build_time": datetime.now().isoformat(timespec="seconds"),
            "source_id_missing_count": source_id_missing_count,
            "content_hash_strategy": "utils.embedding_text.build_chunk_id(document_id, chunk_index, canonical_text)",
            "collection_reference": payload.get("collection_reference"),
            "collection_chunk_count": collection_chunk_count,
            "chunk_count_match": chunk_count_match,
            "mismatch_reason": "" if chunk_count_match else f"bm25={chunk_count}, collection={collection_chunk_count}",
            "schema_version": payload["schema_version"],
        }

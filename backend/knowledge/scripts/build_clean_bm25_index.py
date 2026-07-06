from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


SCRIPT_PATH = Path(__file__).resolve()
KNOWLEDGE_ROOT = SCRIPT_PATH.parents[1]
REPO_ROOT = KNOWLEDGE_ROOT.parents[1]
if str(KNOWLEDGE_ROOT) not in sys.path:
    sys.path.insert(0, str(KNOWLEDGE_ROOT))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from config.settings import settings
from repositories.bm25_repository import Bm25Repository, default_index_dir
from services.document_cleaning_service import clean_document_text, is_indexable
from utils.embedding_text import build_chunk_id, build_content_hash, build_document_id, build_embedding_text, normalize_title
from utils.markdown_utils import MarkDownUtils


TESTDATA = KNOWLEDGE_ROOT / "testdata"
PRODUCTION_COLLECTION = "its-knowledge"
EXPERIMENT_PREFIX = "its-knowledge-clean"


def validate_collection_name(collection_name: str) -> None:
    if collection_name == PRODUCTION_COLLECTION:
        raise ValueError("Refuse production collection for BM25 experiment")
    if not collection_name.startswith(EXPERIMENT_PREFIX):
        raise ValueError("BM25 clean experiment must reference an its-knowledge-clean* collection")


def collection_count(collection_name: str) -> int:
    client = chromadb.PersistentClient(path=settings.VECTOR_STORE_PATH)
    collection = client.get_collection(collection_name)
    return int(collection.count())


def markdown_files() -> list[Path]:
    return sorted(Path(settings.CRAWL_OUTPUT_DIR).glob("*.md"))


def stable_source_id(md_path: Path) -> str:
    return os.path.normpath(os.path.relpath(str(md_path), settings.CRAWL_OUTPUT_DIR)).replace("\\", "/")


def build_clean_chunks(
    *,
    collection_name: str,
    chunk_size: int,
    chunk_overlap: int,
    min_effective_chars: int,
) -> tuple[list[Document], dict[str, Any]]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n##", "\n**", "\n\n", "\n", " ", ""],
    )
    documents: list[Document] = []
    records: list[dict[str, Any]] = []
    missing_source_id = 0

    for md_path in markdown_files():
        raw = md_path.read_text(encoding="utf-8", errors="ignore")
        cleaned = clean_document_text(raw)
        title = normalize_title(MarkDownUtils.extract_title(str(md_path)) or md_path.stem)
        source_id = stable_source_id(md_path)
        indexable = is_indexable(cleaned, min_effective_chars=min_effective_chars)
        records.append({
            "source_path": str(md_path),
            "source_id": source_id,
            "title": title,
            "indexable": indexable,
            "effective_content_chars": cleaned.effective_content_chars,
            "cleaned_char_count": cleaned.cleaned_char_count,
        })
        if not indexable:
            continue
        document_id = build_document_id(source_id)
        chunks = (
            splitter.split_text(cleaned.cleaned_text)
            if len(cleaned.cleaned_text) > chunk_size
            else [cleaned.cleaned_text]
        )
        for chunk_index, chunk in enumerate(chunks):
            canonical_text = build_embedding_text(title, chunk)
            if not canonical_text.strip():
                continue
            chunk_id = build_chunk_id(document_id, chunk_index, canonical_text)
            metadata = {
                "source_id": source_id,
                "source_path": str(md_path),
                "document_id": document_id,
                "chunk_id": chunk_id,
                "chunk_index": chunk_index,
                "title": title,
                "keywords": "",
                "source_type": "markdown_clean",
                "cleaning_version": "clean-v1",
                "collection_experiment": collection_name,
                "original_char_count": cleaned.original_char_count,
                "cleaned_char_count": cleaned.cleaned_char_count,
                "effective_content_chars": cleaned.effective_content_chars,
                "content_hash": build_content_hash(canonical_text),
            }
            if not source_id:
                missing_source_id += 1
            documents.append(Document(page_content=canonical_text, metadata=metadata))

    manifest = {
        "source_document_count": len(records),
        "indexable_document_count": sum(1 for item in records if item["indexable"]),
        "chunk_count": len(documents),
        "source_id_missing_count": missing_source_id,
        "records": records,
    }
    return documents, manifest


def write_manifest_reports(manifest: dict[str, Any], *, index_name: str) -> None:
    json_path = TESTDATA / f"rag_bm25_{index_name.replace('-', '_')}_manifest.json"
    md_path = TESTDATA / f"rag_bm25_{index_name.replace('-', '_')}_manifest.md"
    json_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        "# RAG BM25 Clean Manifest",
        "",
        f"- index_name: `{manifest.get('index_name')}`",
        f"- index_path: `{manifest.get('index_path')}`",
        f"- cleaning_version: `{manifest.get('cleaning_version')}`",
        f"- chunk_size / chunk_overlap: {manifest.get('chunk_size')} / {manifest.get('chunk_overlap')}",
        f"- source_document_count: {manifest.get('source_document_count')}",
        f"- chunk_count: {manifest.get('chunk_count')}",
        f"- collection_reference: `{manifest.get('collection_reference')}`",
        f"- collection_chunk_count: {manifest.get('collection_chunk_count')}",
        f"- chunk_count_match: {manifest.get('chunk_count_match')}",
        f"- mismatch_reason: {manifest.get('mismatch_reason')}",
        f"- tokenizer: {manifest.get('tokenizer_name')} {manifest.get('tokenizer_version')}",
        f"- source_id_missing_count: {manifest.get('source_id_missing_count')}",
    ]
    md_path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build experimental BM25 index for clean RAG collection.")
    parser.add_argument("--index-name", default="clean-v1")
    parser.add_argument("--collection-name", required=True)
    parser.add_argument("--chunk-size", type=int, default=1500)
    parser.add_argument("--chunk-overlap", type=int, default=200)
    parser.add_argument("--min-effective-chars", type=int, default=80)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--rebuild", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    validate_collection_name(args.collection_name)
    collection_chunks = collection_count(args.collection_name)
    documents, build_manifest = build_clean_chunks(
        collection_name=args.collection_name,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        min_effective_chars=args.min_effective_chars,
    )
    chunk_count_match = len(documents) == collection_chunks
    preliminary = {
        "index_name": args.index_name,
        "index_path": str(default_index_dir(args.index_name)),
        "cleaning_version": "clean-v1",
        "chunk_size": args.chunk_size,
        "chunk_overlap": args.chunk_overlap,
        "source_document_count": build_manifest["source_document_count"],
        "chunk_count": len(documents),
        "tokenizer_name": "jieba_with_exact_anchor_tokens",
        "tokenizer_version": "v1",
        "build_time": None,
        "source_id_missing_count": build_manifest["source_id_missing_count"],
        "content_hash_strategy": "utils.embedding_text.build_chunk_id(document_id, chunk_index, canonical_text)",
        "collection_reference": args.collection_name,
        "collection_chunk_count": collection_chunks,
        "chunk_count_match": chunk_count_match,
        "mismatch_reason": "" if chunk_count_match else f"bm25={len(documents)}, collection={collection_chunks}",
        "dry_run": args.dry_run,
    }
    if args.dry_run:
        write_manifest_reports(preliminary, index_name=args.index_name)
        print("BM25 dry run completed")
        print(json.dumps(preliminary, ensure_ascii=False, indent=2))
        return 0 if chunk_count_match else 2

    if not chunk_count_match:
        write_manifest_reports(preliminary, index_name=args.index_name)
        raise SystemExit(f"BM25 chunk count mismatch: {preliminary['mismatch_reason']}")

    repo = Bm25Repository(default_index_dir(args.index_name))
    manifest = repo.build_index(
        documents,
        index_name=args.index_name,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        collection_reference=args.collection_name,
        collection_chunk_count=collection_chunks,
        rebuild=args.rebuild,
    )
    write_manifest_reports(manifest, index_name=args.index_name)
    print("BM25 index build completed")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

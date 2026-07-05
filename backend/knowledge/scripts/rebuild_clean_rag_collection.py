from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import chromadb
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


SCRIPT_PATH = Path(__file__).resolve()
KNOWLEDGE_ROOT = SCRIPT_PATH.parents[1]
REPO_ROOT = KNOWLEDGE_ROOT.parents[1]
if str(KNOWLEDGE_ROOT) not in sys.path:
    sys.path.insert(0, str(KNOWLEDGE_ROOT))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from config.settings import settings
from repositories.vector_store_repository import VectorStoreRepository
from services.document_cleaning_service import clean_document_text, is_indexable
from utils.embedding_text import build_chunk_id, build_content_hash, build_document_id, build_embedding_text, normalize_title
from utils.markdown_utils import MarkDownUtils


PRODUCTION_COLLECTION = "its-knowledge"
EXPERIMENT_PREFIX = "its-knowledge-clean"
MANIFEST_JSON = KNOWLEDGE_ROOT / "testdata" / "rag_cleaning_manifest.json"
MANIFEST_MD = KNOWLEDGE_ROOT / "testdata" / "rag_cleaning_manifest.md"
REBUILD_REPORT_JSON = KNOWLEDGE_ROOT / "testdata" / "rag_clean_collection_rebuild_report.json"
REBUILD_REPORT_MD = KNOWLEDGE_ROOT / "testdata" / "rag_clean_collection_rebuild_report.md"
REQUIRED_METADATA_FIELDS = {
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


def validate_collection_name(collection_name: str) -> None:
    if collection_name == PRODUCTION_COLLECTION:
        raise ValueError("Refuse to rebuild or delete production collection: its-knowledge")
    if not collection_name.startswith(EXPERIMENT_PREFIX):
        raise ValueError("Refuse collection name that does not start with its-knowledge-clean")


def collection_exists(collection_name: str) -> bool:
    client = chromadb.PersistentClient(path=settings.VECTOR_STORE_PATH)
    names = []
    for collection in client.list_collections():
        names.append(collection.name if hasattr(collection, "name") else str(collection))
    return collection_name in names


def delete_experiment_collection(collection_name: str) -> None:
    validate_collection_name(collection_name)
    client = chromadb.PersistentClient(path=settings.VECTOR_STORE_PATH)
    try:
        client.delete_collection(collection_name)
    except Exception:
        pass


def load_markdown_files() -> list[Path]:
    root = Path(settings.CRAWL_OUTPUT_DIR)
    return sorted(root.glob("*.md"))


def stable_source_id(md_path: Path) -> str:
    return os.path.normpath(os.path.relpath(str(md_path), settings.CRAWL_OUTPUT_DIR)).replace("\\", "/")


def build_manifest(min_effective_chars: int) -> dict[str, Any]:
    records = []
    for md_path in load_markdown_files():
        raw = md_path.read_text(encoding="utf-8", errors="ignore")
        title = normalize_title(MarkDownUtils.extract_title(str(md_path)) or md_path.stem)
        source_id = stable_source_id(md_path)
        cleaned = clean_document_text(raw)
        indexable = is_indexable(cleaned, min_effective_chars=min_effective_chars)
        skip_reason = "" if indexable else f"effective_content_chars<{min_effective_chars}"
        records.append({
            "source_path": str(md_path),
            "source_id": source_id,
            "title": title,
            "original_char_count": cleaned.original_char_count,
            "cleaned_char_count": cleaned.cleaned_char_count,
            "effective_content_chars": cleaned.effective_content_chars,
            "image_markdown_count": cleaned.image_markdown_count,
            "url_count": cleaned.url_count,
            "html_tag_count": cleaned.html_tag_count,
            "removed_metadata_blocks": cleaned.removed_metadata_blocks,
            "indexable": indexable,
            "skip_reason": skip_reason,
            "mineru_candidate": cleaned.mineru_candidate,
            "content_hash": cleaned.content_hash,
        })
    summary = summarize_manifest(records)
    manifest = {
        "status": "success",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "min_effective_chars": min_effective_chars,
        "crawl_output_dir": settings.CRAWL_OUTPUT_DIR,
        "summary": summary,
        "records": records,
    }
    write_manifest(manifest)
    return manifest


def summarize_manifest(records: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(records)
    indexable = sum(1 for item in records if item["indexable"])
    skipped = total - indexable
    mineru = sum(1 for item in records if item["mineru_candidate"])
    original_avg = sum(item["original_char_count"] for item in records) / total if total else 0
    cleaned_avg = sum(item["cleaned_char_count"] for item in records) / total if total else 0
    return {
        "total_markdown": total,
        "indexable_documents": indexable,
        "skipped_documents": skipped,
        "mineru_candidate_documents": mineru,
        "average_original_char_count": round(original_avg, 2),
        "average_cleaned_char_count": round(cleaned_avg, 2),
        "removed_image_markdown_count": sum(item["image_markdown_count"] for item in records),
        "removed_url_count": sum(item["url_count"] for item in records),
        "removed_html_tag_count": sum(item["html_tag_count"] for item in records),
    }


def write_manifest(manifest: dict[str, Any]) -> None:
    MANIFEST_JSON.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_JSON.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    MANIFEST_MD.write_text(render_manifest_md(manifest), encoding="utf-8")


def render_manifest_md(manifest: dict[str, Any]) -> str:
    summary = manifest["summary"]
    lines = [
        "# RAG Cleaning Manifest",
        "",
        f"- Generated at: `{manifest['generated_at']}`",
        f"- Markdown dir: `{manifest['crawl_output_dir']}`",
        f"- Min effective chars: {manifest['min_effective_chars']}",
        "",
        "## Summary",
        "",
    ]
    for key, value in summary.items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Top Skipped Documents", ""])
    skipped = [item for item in manifest["records"] if not item["indexable"]]
    skipped.sort(key=lambda item: item["effective_content_chars"])
    for item in skipped[:20]:
        lines.append(
            f"- `{item['source_id']}` | effective={item['effective_content_chars']} | "
            f"images={item['image_markdown_count']} | urls={item['url_count']} | reason={item['skip_reason']}"
        )
    lines.extend(["", "## Top MinerU Candidates", ""])
    mineru = [item for item in manifest["records"] if item["mineru_candidate"]]
    mineru.sort(key=lambda item: (item["effective_content_chars"], -item["image_markdown_count"]))
    for item in mineru[:20]:
        lines.append(
            f"- `{item['source_id']}` | effective={item['effective_content_chars']} | "
            f"images={item['image_markdown_count']} | cleaned={item['cleaned_char_count']}"
        )
    return "\n".join(lines)


def build_documents(
    manifest: dict[str, Any],
    *,
    collection_name: str,
    chunk_size: int,
    chunk_overlap: int,
) -> tuple[list[Document], list[str], list[dict[str, Any]]]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n##", "\n**", "\n\n", "\n", " ", ""],
    )
    documents: list[Document] = []
    ids: list[str] = []
    metadata_errors: list[dict[str, Any]] = []

    for record in manifest["records"]:
        if not record["indexable"]:
            continue
        md_path = Path(record["source_path"])
        raw = md_path.read_text(encoding="utf-8", errors="ignore")
        cleaned = clean_document_text(raw)
        source_id = record["source_id"]
        title = record["title"]
        document_id = build_document_id(source_id)
        chunks = splitter.split_text(cleaned.cleaned_text) if len(cleaned.cleaned_text) > chunk_size else [cleaned.cleaned_text]

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
            missing = sorted(field for field in REQUIRED_METADATA_FIELDS if metadata.get(field) is None)
            if missing:
                metadata_errors.append({"source_id": source_id, "chunk_index": chunk_index, "missing": missing})
            documents.append(Document(page_content=canonical_text, metadata=metadata))
            ids.append(chunk_id)

    return documents, ids, metadata_errors


def rebuild_collection(args: argparse.Namespace, manifest: dict[str, Any]) -> dict[str, Any]:
    validate_collection_name(args.collection_name)
    exists = collection_exists(args.collection_name)
    if exists and not args.recreate_experiment:
        raise ValueError(
            f"Experiment collection already exists: {args.collection_name}. "
            "Pass --recreate-experiment to delete and rebuild it."
        )
    if exists and args.recreate_experiment:
        delete_experiment_collection(args.collection_name)

    documents, ids, metadata_errors = build_documents(
        manifest,
        collection_name=args.collection_name,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
    )
    vector_store = VectorStoreRepository(collection_name=args.collection_name)
    added = vector_store.add_documents(documents, batch_size=args.batch_size, ids=ids) if documents else 0
    collection = vector_store._collection()
    collection_count = int(collection.count()) if collection is not None else None
    sample_errors = sample_metadata_integrity(vector_store, sample_size=20)

    report = {
        "status": "success",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "collection_name": args.collection_name,
        "chunk_size": args.chunk_size,
        "chunk_overlap": args.chunk_overlap,
        "min_effective_chars": args.min_effective_chars,
        "documents_added": added,
        "chunk_count": len(documents),
        "collection_count": collection_count,
        "metadata_errors": metadata_errors,
        "sample_metadata_errors": sample_errors,
        "manifest_summary": manifest["summary"],
        "embedding_model": settings.EMBEDDING_MODEL,
        "distance_space": settings.VECTOR_DISTANCE_SPACE,
    }
    write_rebuild_report(report)
    return report


def sample_metadata_integrity(vector_store: VectorStoreRepository, sample_size: int) -> list[dict[str, Any]]:
    collection = vector_store._collection()
    if collection is None:
        return [{"error": "collection handle unavailable"}]
    try:
        found = collection.get(limit=sample_size, include=["metadatas"])
    except Exception as exc:
        return [{"error": str(exc)}]
    errors = []
    metadatas = found.get("metadatas", []) if isinstance(found, dict) else []
    for index, metadata in enumerate(metadatas):
        missing = sorted(field for field in REQUIRED_METADATA_FIELDS if not metadata or metadata.get(field) is None)
        if missing:
            errors.append({"sample_index": index, "missing": missing})
    return errors


def write_rebuild_report(report: dict[str, Any]) -> None:
    REBUILD_REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        "# RAG Clean Collection Rebuild Report",
        "",
        f"- Status: `{report['status']}`",
        f"- Generated at: `{report['generated_at']}`",
        f"- Collection: `{report['collection_name']}`",
        f"- Chunk size/overlap: {report['chunk_size']} / {report['chunk_overlap']}",
        f"- Documents added: {report['documents_added']}",
        f"- Chunk count: {report['chunk_count']}",
        f"- Collection count: {report['collection_count']}",
        f"- Metadata errors: {len(report['metadata_errors'])}",
        f"- Sample metadata errors: {len(report['sample_metadata_errors'])}",
    ]
    REBUILD_REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build cleaned experimental RAG Chroma collections.")
    parser.add_argument("--dry-run", action="store_true", help="Only generate cleaning manifest.")
    parser.add_argument("--collection-name", help="Experimental collection name.")
    parser.add_argument("--chunk-size", type=int, default=1500)
    parser.add_argument("--chunk-overlap", type=int, default=200)
    parser.add_argument("--min-effective-chars", type=int, default=80)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--recreate-experiment", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest = build_manifest(args.min_effective_chars)
    if args.dry_run:
        print("Dry run completed")
        print(f"manifest_json={MANIFEST_JSON}")
        print(f"manifest_md={MANIFEST_MD}")
        print(f"summary={manifest['summary']}")
        return 0
    if not args.collection_name:
        raise SystemExit("--collection-name is required unless --dry-run is used")
    report = rebuild_collection(args, manifest)
    print("Clean collection rebuild completed")
    print(f"collection={report['collection_name']}")
    print(f"documents_added={report['documents_added']} chunk_count={report['chunk_count']}")
    print(f"collection_count={report['collection_count']}")
    print(f"rebuild_report_json={REBUILD_REPORT_JSON}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

import argparse
import os
import sys
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from config.settings import settings
from repositories.vector_store_repository import VectorStoreRepository
from services.ingestion.ingestion_processor import IngestionProcessor


def iter_markdown_files(source_dir: str):
    root = Path(source_dir).resolve()
    for path in sorted(root.rglob("*.md")):
        if path.is_file():
            yield root, path


def main() -> None:
    parser = argparse.ArgumentParser(description="Rebuild markdown files into a new Chroma collection without deleting old collections.")
    parser.add_argument("--source-dir", required=True)
    parser.add_argument("--collection-name", required=True)
    parser.add_argument("--space", default="cosine")
    args = parser.parse_args()

    vector_store = VectorStoreRepository(
        collection_name=args.collection_name,
        distance_space=args.space,
        persist_directory=settings.VECTOR_STORE_PATH,
    )
    processor = IngestionProcessor(vector_store=vector_store)

    document_count = 0
    chunk_count = 0
    for root, path in iter_markdown_files(args.source_dir):
        source_id = os.path.normpath(os.path.relpath(path, root)).replace("\\", "/")
        added = processor.ingest_file(
            str(path),
            source_id=source_id,
            display_title=path.name,
        )
        document_count += 1
        chunk_count += added

    print("Vector store rebuild finished")
    print(f"old_collection={settings.VECTOR_COLLECTION_NAME}")
    print(f"new_collection={args.collection_name}")
    print(f"documents={document_count}")
    print(f"chunks={chunk_count}")
    print(f"distance_space={args.space}")
    print("Old collection was not deleted. Switch VECTOR_COLLECTION_NAME explicitly after validation.")


if __name__ == "__main__":
    main()

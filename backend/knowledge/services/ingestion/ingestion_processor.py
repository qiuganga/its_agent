import logging
import os

from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores.utils import filter_complex_metadata
from langchain_text_splitters import RecursiveCharacterTextSplitter

from repositories.vector_store_repository import VectorStoreRepository
from utils.embedding_text import (
    build_chunk_id,
    build_content_hash,
    build_document_id,
    build_embedding_text,
    has_effective_content,
    normalize_title,
    strip_existing_source_prefixes,
)
from utils.markdown_utils import MarkDownUtils


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IngestionProcessor:
    def __init__(self, vector_store: VectorStoreRepository | None = None):
        self.vector_store = vector_store or VectorStoreRepository()
        self.document_spliter = RecursiveCharacterTextSplitter(
            chunk_size=1500,
            chunk_overlap=200,
            separators=["\n##", "\n**", "\n\n", "\n", " ", ""],
        )

    def ingest_file(
        self,
        md_path: str,
        *,
        source_id: str | None = None,
        display_title: str | None = None,
    ) -> int:
        stable_source_id = source_id or self._stable_source_id(md_path)
        title = normalize_title(display_title or MarkDownUtils.extract_title(md_path) or stable_source_id)
        document_id = build_document_id(stable_source_id)

        try:
            text_loader = TextLoader(file_path=md_path, encoding="utf-8")
            documents = text_loader.load()
        except Exception as e:
            logger.error("Failed to load markdown file %s: %s", md_path, str(e))
            raise

        final_document_chunks = []
        for doc in documents:
            raw_content = strip_existing_source_prefixes(doc.page_content)
            doc.metadata["title"] = title
            doc.metadata["source_id"] = stable_source_id
            doc.metadata["source_path"] = md_path
            doc.metadata["document_id"] = document_id

            if len(raw_content) < 1500:
                doc.page_content = raw_content
                final_document_chunks.append(doc)
            else:
                doc.page_content = raw_content
                final_document_chunks.extend(self.document_spliter.split_documents([doc]))

        clean_documents_chunks = filter_complex_metadata(final_document_chunks)
        valid_documents_chunks = []
        ids = []

        for chunk_index, document in enumerate(clean_documents_chunks):
            canonical_text = build_embedding_text(title, document.page_content)
            if not has_effective_content(canonical_text):
                continue

            chunk_id = build_chunk_id(document_id, chunk_index, canonical_text)
            document.page_content = canonical_text
            document.metadata.update({
                "source_id": stable_source_id,
                "source_path": md_path,
                "document_id": document_id,
                "chunk_id": chunk_id,
                "chunk_index": chunk_index,
                "title": title,
                "content_hash": build_content_hash(canonical_text),
            })
            valid_documents_chunks.append(document)
            ids.append(chunk_id)

        if not valid_documents_chunks:
            logger.error("No valid chunks after splitting markdown file: %s", md_path)
            return 0

        self.vector_store.delete_by_source_id(stable_source_id)
        return self.vector_store.add_documents(valid_documents_chunks, ids=ids)

    def _stable_source_id(self, md_path: str) -> str:
        try:
            return os.path.normpath(os.path.relpath(md_path)).replace("\\", "/")
        except Exception:
            return os.path.basename(md_path)


if __name__ == "__main__":
    ingest_processor = IngestionProcessor()
    count = ingest_processor.ingest_file(
        "D:\\sgg-agent\\code\\its_multi_agent\\backend\\knowledge\\data\\crawl\\0430-联想手机K900常见问题汇总.md"
    )
    print(f"成功入库文档块数量: {count}")

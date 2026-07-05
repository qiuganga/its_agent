import logging
from typing import List

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai.embeddings import OpenAIEmbeddings

from config.settings import settings


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorStoreRepository:
    def __init__(
        self,
        *,
        collection_name: str | None = None,
        distance_space: str | None = None,
        persist_directory: str | None = None,
        embedding=None,
    ):
        self.collection_name = collection_name or settings.VECTOR_COLLECTION_NAME
        self.distance_space = distance_space or settings.VECTOR_DISTANCE_SPACE
        self.persist_directory = persist_directory or settings.VECTOR_STORE_PATH
        self.embedding = embedding or OpenAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            openai_api_key=settings.API_KEY,
            openai_api_base=settings.BASE_URL,
        )

        self.vector_database = self._build_chroma()
        self._log_collection_configuration()

    def _build_chroma(self) -> Chroma:
        kwargs = {
            "persist_directory": self.persist_directory,
            "collection_name": self.collection_name,
            "embedding_function": self.embedding,
        }
        try:
            kwargs["collection_metadata"] = {"hnsw:space": self.distance_space}
            return Chroma(**kwargs)
        except TypeError:
            kwargs.pop("collection_metadata", None)
            logger.warning("Current langchain-chroma does not support collection_metadata; using default collection config")
            return Chroma(**kwargs)

    def _collection(self):
        return getattr(self.vector_database, "_collection", None)

    def _log_collection_configuration(self) -> None:
        collection = self._collection()
        metadata = getattr(collection, "metadata", None) if collection is not None else None
        logger.info(
            "Chroma collection loaded: name=%s expected_space=%s actual_metadata=%s",
            self.collection_name,
            self.distance_space,
            metadata,
        )
        actual_space = None
        if isinstance(metadata, dict):
            actual_space = metadata.get("hnsw:space")
        if actual_space and actual_space != self.distance_space:
            logger.warning(
                "Chroma collection distance space mismatch: expected=%s actual=%s. "
                "Do not rewrite existing data automatically; run rebuild CLI and switch config explicitly.",
                self.distance_space,
                actual_space,
            )

    def add_documents(self, documents: list[Document], batch_size: int = 16, ids: list[str] | None = None) -> int:
        total_documents_chunks = len(documents)
        documents_chunks_added = 0

        try:
            for i in range(0, total_documents_chunks, batch_size):
                batch = documents[i:i + batch_size]
                batch_ids = ids[i:i + batch_size] if ids else None
                if batch_ids:
                    self.vector_database.add_documents(batch, ids=batch_ids)
                else:
                    self.vector_database.add_documents(batch)

                documents_chunks_added += len(batch)
                logger.info("Added chunks to vector store: %s/%s", documents_chunks_added, total_documents_chunks)

            return documents_chunks_added
        except Exception as e:
            logger.error("Failed to add document chunks to vector store: %s", str(e))
            raise

    def delete_by_source_id(self, source_id: str) -> int:
        if not source_id:
            return 0

        collection = self._collection()
        if collection is None:
            logger.warning("Chroma collection handle unavailable; skip delete_by_source_id")
            return 0

        try:
            found = collection.get(where={"source_id": source_id})
            ids = found.get("ids", []) if isinstance(found, dict) else []
            if not ids:
                return 0
            collection.delete(ids=ids)
            logger.info("Deleted %s old chunks for source_id=%s", len(ids), source_id)
            return len(ids)
        except Exception as e:
            logger.error("Failed to delete chunks by source_id=%s: %s", source_id, str(e))
            raise

    def embedd_document(self, text: str) -> List[float]:
        return self.embedding.embed_query(text)

    def embedd_documents(self, texts: List[str]) -> List[List[float]]:
        return self.embedding.embed_documents(texts)

    def search_similarity_with_score(
        self,
        user_question: str,
        top_k: int | None = None,
    ) -> List[tuple[Document, float]]:
        if top_k is None:
            top_k = settings.RAG_VECTOR_CANDIDATE_TOP_K
        return self.vector_database.similarity_search_with_score(user_question, top_k)

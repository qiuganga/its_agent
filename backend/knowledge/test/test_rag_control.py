import os
import sys
import tempfile
import types
import unittest
from dataclasses import dataclass, field


KNOWLEDGE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if KNOWLEDGE_ROOT not in sys.path:
    sys.path.insert(0, KNOWLEDGE_ROOT)


@dataclass
class FakeDocument:
    page_content: str
    metadata: dict = field(default_factory=dict)


class FakeArray(list):
    def flatten(self):
        return self

    def argsort(self):
        return sorted(range(len(self)), key=lambda i: self[i])


def _cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(x * x for x in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def fake_cosine_similarity(left, right):
    return FakeArray([_cosine(left[0], item) for item in right])


def install_fake_dependencies():
    langchain_core = types.ModuleType("langchain_core")
    documents = types.ModuleType("langchain_core.documents")
    documents.Document = FakeDocument
    sys.modules["langchain_core"] = langchain_core
    sys.modules["langchain_core.documents"] = documents

    splitters = types.ModuleType("langchain_text_splitters")

    class FakeSplitter:
        def __init__(self, *args, **kwargs):
            pass

        def split_documents(self, docs):
            chunks = []
            for doc in docs:
                text = doc.page_content
                for idx in range(0, len(text), 120):
                    chunks.append(FakeDocument(text[idx:idx + 160], dict(doc.metadata)))
            return chunks

        def split_text(self, text):
            return [text[idx:idx + 160] for idx in range(0, len(text), 120)]

    splitters.RecursiveCharacterTextSplitter = FakeSplitter
    sys.modules["langchain_text_splitters"] = splitters

    loaders = types.ModuleType("langchain_community.document_loaders")

    class FakeTextLoader:
        def __init__(self, file_path, encoding="utf-8"):
            self.file_path = file_path
            self.encoding = encoding

        def load(self):
            with open(self.file_path, "r", encoding=self.encoding) as handle:
                return [FakeDocument(handle.read(), {"source": self.file_path})]

    loaders.TextLoader = FakeTextLoader
    community = types.ModuleType("langchain_community")
    vector_utils = types.ModuleType("langchain_community.vectorstores.utils")
    vector_utils.filter_complex_metadata = lambda docs: docs
    sys.modules["langchain_community"] = community
    sys.modules["langchain_community.document_loaders"] = loaders
    sys.modules["langchain_community.vectorstores"] = types.ModuleType("langchain_community.vectorstores")
    sys.modules["langchain_community.vectorstores.utils"] = vector_utils

    chroma = types.ModuleType("langchain_chroma")
    chroma.Chroma = object
    sys.modules["langchain_chroma"] = chroma

    openai_embeddings = types.ModuleType("langchain_openai.embeddings")
    openai_embeddings.OpenAIEmbeddings = object
    langchain_openai = types.ModuleType("langchain_openai")
    sys.modules["langchain_openai"] = langchain_openai
    sys.modules["langchain_openai.embeddings"] = openai_embeddings

    sklearn = types.ModuleType("sklearn")
    metrics = types.ModuleType("sklearn.metrics")
    pairwise = types.ModuleType("sklearn.metrics.pairwise")
    pairwise.cosine_similarity = fake_cosine_similarity
    sys.modules["sklearn"] = sklearn
    sys.modules["sklearn.metrics"] = metrics
    sys.modules["sklearn.metrics.pairwise"] = pairwise

    jieba = types.ModuleType("jieba")
    jieba.lcut = lambda text: list(text)
    sys.modules["jieba"] = jieba


install_fake_dependencies()

from services.ingestion.ingestion_processor import IngestionProcessor
from services.retrieval_service import RetrievalService
from utils.embedding_text import build_embedding_text


class FakeVectorStore:
    def __init__(self):
        self.docs = []
        self.ids = []
        self.deleted = []
        self.embedded_texts = []

    def delete_by_source_id(self, source_id):
        self.deleted.append(source_id)
        kept = [(doc, id_) for doc, id_ in zip(self.docs, self.ids) if doc.metadata.get("source_id") != source_id]
        self.docs = [item[0] for item in kept]
        self.ids = [item[1] for item in kept]
        return 1

    def add_documents(self, documents, batch_size=16, ids=None):
        self.docs.extend(documents)
        self.ids.extend(ids or [None] * len(documents))
        return len(documents)

    def search_similarity_with_score(self, user_question, top_k=5):
        return [(FakeDocument("文档来源:旧标题\n有效内容" * 20, {"title": "旧标题"}), 0.42)]

    def embedd_document(self, text):
        return [1.0, 0.0]

    def embedd_documents(self, texts):
        self.embedded_texts.extend(texts)
        vectors = []
        for text in texts:
            if "doc-b" in text:
                vectors.append([0.0, 1.0])
            elif "doc-a-2" in text:
                vectors.append([1.0, 0.0])
            else:
                vectors.append([1.0, 0.0])
        return vectors


class RagControlTests(unittest.TestCase):
    def test_build_embedding_text_is_idempotent(self):
        first = build_embedding_text("标题", "文档来源:旧标题\n文档来源:重复\n正文内容")
        second = build_embedding_text("标题", first)
        self.assertEqual(first, second)
        self.assertEqual(first.count("文档来源:"), 1)

    def test_repeated_ingest_replaces_same_source_chunks_and_metadata(self):
        store = FakeVectorStore()
        processor = IngestionProcessor(vector_store=store)
        with tempfile.TemporaryDirectory() as temp_dir:
            path = os.path.join(temp_dir, "doc.md")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write("第一版正文内容" * 20)
            processor.ingest_file(path, source_id="stable/doc.md", display_title="doc.md")
            first_ids = list(store.ids)

            with open(path, "w", encoding="utf-8") as handle:
                handle.write("第二版正文内容" * 20)
            processor.ingest_file(path, source_id="stable/doc.md", display_title="doc.md")

        self.assertIn("stable/doc.md", store.deleted)
        self.assertTrue(store.docs)
        self.assertNotEqual(first_ids, store.ids)
        for doc in store.docs:
            self.assertEqual(doc.metadata["source_id"], "stable/doc.md")
            self.assertIn("document_id", doc.metadata)
            self.assertIn("chunk_id", doc.metadata)
            self.assertIn("content_hash", doc.metadata)

    def test_vector_route_keeps_chroma_distance(self):
        service = RetrievalService(chroma_vector=FakeVectorStore())
        docs = service._search_based_vector("问题")
        self.assertEqual(docs[0].metadata["retrieval_route"], "vector")
        self.assertEqual(docs[0].metadata["chroma_distance"], 0.42)

    def test_reranking_recomputes_all_candidate_scores(self):
        store = FakeVectorStore()
        service = RetrievalService(chroma_vector=store)
        docs = [
            FakeDocument("doc-a-1 内容" * 20, {"title": "A", "similarity": 0.01}),
            FakeDocument("doc-b 内容" * 20, {"title": "B", "similarity": 0.99}),
        ]
        result = service._reranking(docs, "问题")
        self.assertEqual(len(store.embedded_texts), 2)
        self.assertTrue(all("final_rerank_score" in doc.metadata for doc in result))
        self.assertTrue(all("canonical_embedding_text_hash" in doc.metadata for doc in result))

    def test_mmr_prefers_diversity_but_falls_back_for_single_document(self):
        service = RetrievalService(chroma_vector=FakeVectorStore())
        scored = [
            (FakeDocument("doc-a-1", {"document_id": "a"}), 0.95, [1.0, 0.0]),
            (FakeDocument("doc-a-2", {"document_id": "a"}), 0.94, [1.0, 0.0]),
            (FakeDocument("doc-b", {"document_id": "b"}), 0.80, [0.0, 1.0]),
        ]
        selected = service._select_mmr(scored, 2)
        self.assertEqual([doc.metadata["document_id"] for doc, _ in selected], ["a", "b"])

        single_source = scored[:2]
        selected_single = service._select_mmr(single_source, 2)
        self.assertEqual(len(selected_single), 2)

    def test_rebuild_cli_does_not_delete_old_collection_in_source(self):
        cli_path = os.path.join(KNOWLEDGE_ROOT, "cli", "rebuild_vector_store.py")
        with open(cli_path, "r", encoding="utf-8") as handle:
            source = handle.read()
        self.assertNotIn("delete_collection", source)
        self.assertIn("Old collection was not deleted", source)


if __name__ == "__main__":
    unittest.main()

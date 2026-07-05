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

    class FakeChatOpenAI:
        last_prompt = None

        def __init__(self, *args, **kwargs):
            pass

        def invoke(self, prompt):
            FakeChatOpenAI.last_prompt = prompt
            return types.SimpleNamespace(content="mock answer")

    langchain_openai.ChatOpenAI = FakeChatOpenAI
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
from services.query_normalization_service import QueryNormalizationService
from services.query_service import QueryService
from services.retrieval_service import RetrievalService
from repositories.vector_store_repository import VectorStoreRepository
from config.settings import settings
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


class TrackingRetrievalService(RetrievalService):
    def __init__(self, docs_by_query, reranked_docs=None):
        self.docs_by_query = docs_by_query
        self.reranked_docs = reranked_docs
        self.retrieved_queries = []
        self.rerank_questions = []

    def retrieve_candidates(self, query, *, original_question=None):
        self.retrieved_queries.append(query)
        docs = []
        for doc in self.docs_by_query.get(query, []):
            metadata = dict(doc.metadata)
            metadata["matched_by_normalized_query"] = bool(original_question and query != original_question)
            docs.append(FakeDocument(doc.page_content, metadata))
        return docs

    def rerank_candidates(self, original_question, candidates):
        self.rerank_questions.append(original_question)
        docs = self.reranked_docs if self.reranked_docs is not None else candidates
        return [FakeDocument(doc.page_content, dict(doc.metadata)) for doc in docs]


class RagControlTests(unittest.TestCase):
    def test_query_normalization_rewrites_common_fault_phrases(self):
        service = QueryNormalizationService()
        normalized = service.normalize("  开不了机，   屏幕不亮  ")
        self.assertIn("无法开机", normalized)
        self.assertIn("黑屏", normalized)

    def test_query_normalization_keeps_question_without_rule_changes(self):
        service = QueryNormalizationService()
        question = "键盘输入延迟怎么办"
        self.assertEqual(service.normalize(question), question)

    def test_query_normalization_does_not_invent_brand_model_or_system_version(self):
        service = QueryNormalizationService()
        normalized = service.normalize("屏幕不亮怎么办")
        self.assertIn("黑屏", normalized)
        for unexpected in ["联想", "K900", "Windows", "Windows 11"]:
            self.assertNotIn(unexpected, normalized)

    def test_same_normalized_question_retrieves_candidates_once(self):
        doc = FakeDocument("有效内容" * 20, {"document_id": "a", "final_rerank_score": 0.9})
        service = TrackingRetrievalService({"键盘输入延迟怎么办": [doc]})
        result = service.retrieval(
            original_question="键盘输入延迟怎么办",
            query_variants=["键盘输入延迟怎么办"],
        )
        self.assertEqual(service.retrieved_queries, ["键盘输入延迟怎么办"])
        self.assertEqual(len(result), 1)

    def test_different_normalized_question_retrieves_two_candidate_routes(self):
        original = "开不了机，屏幕不亮"
        normalized = "无法开机，黑屏"
        doc = FakeDocument("有效内容" * 20, {"document_id": "a", "final_rerank_score": 0.9})
        service = TrackingRetrievalService({original: [doc], normalized: [doc]})
        service.retrieval(original_question=original, query_variants=[original, normalized])
        self.assertEqual(service.retrieved_queries, [original, normalized])

    def test_two_route_candidates_are_deduplicated_and_keep_normalized_flag(self):
        original = "开不了机"
        normalized = "无法开机"
        first = FakeDocument("相同有效内容" * 20, {"document_id": "same", "final_rerank_score": 0.9})
        second = FakeDocument("相同有效内容" * 20, {"document_id": "same", "final_rerank_score": 0.8})
        service = TrackingRetrievalService({original: [first], normalized: [second]})
        result = service.retrieval(original_question=original, query_variants=[original, normalized])
        self.assertEqual(len(result), 1)
        self.assertTrue(result[0].metadata["matched_by_normalized_query"])
        self.assertEqual(result[0].metadata["query_variants"], [original, normalized])

    def test_final_rerank_uses_original_question_not_normalized_question(self):
        original = "开不了机"
        normalized = "无法开机"
        doc = FakeDocument("有效内容" * 20, {"document_id": "a", "final_rerank_score": 0.9})
        service = TrackingRetrievalService({original: [doc], normalized: [doc]})
        service.retrieval(original_question=original, query_variants=[original, normalized])
        self.assertEqual(service.rerank_questions, [original])

    def test_vector_repository_default_top_k_uses_candidate_setting(self):
        class FakeChroma:
            def __init__(self):
                self.top_k = None

            def similarity_search_with_score(self, question, top_k):
                self.top_k = top_k
                return []

        fake_chroma = FakeChroma()
        repo = VectorStoreRepository.__new__(VectorStoreRepository)
        repo.vector_database = fake_chroma
        repo.search_similarity_with_score("问题")
        self.assertEqual(fake_chroma.top_k, settings.RAG_VECTOR_CANDIDATE_TOP_K)

    def test_title_candidate_limit_uses_title_candidate_setting(self):
        store = FakeVectorStore()
        service = RetrievalService(chroma_vector=store)
        rough = [
            {"title": f"title-{idx}", "roughing_score": 1.0, "path": f"doc-{idx}.md"}
            for idx in range(settings.RAG_TITLE_CANDIDATE_TOP_K + 5)
        ]
        result = service.fine_ranking("问题", rough)
        self.assertEqual(len(result), settings.RAG_TITLE_CANDIDATE_TOP_K)

    def test_retrieval_returns_empty_when_no_final_candidates(self):
        service = TrackingRetrievalService({"无结果问题": []}, reranked_docs=[])
        self.assertEqual(service.retrieval("无结果问题"), [])

    def test_retrieval_rejects_when_top_rerank_score_is_below_threshold(self):
        doc = FakeDocument("有效内容" * 20, {"document_id": "a", "final_rerank_score": settings.RAG_MIN_RERANK_SCORE - 0.01})
        service = TrackingRetrievalService({"低相关问题": [doc]}, reranked_docs=[doc])
        self.assertEqual(service.retrieval("低相关问题"), [])

    def test_low_confidence_rejection_uses_final_rerank_score_not_chroma_distance(self):
        doc = FakeDocument(
            "有效内容" * 20,
            {
                "document_id": "a",
                "chroma_distance": 0.0,
                "final_rerank_score": settings.RAG_MIN_RERANK_SCORE - 0.01,
            },
        )
        service = TrackingRetrievalService({"低相关问题": [doc]}, reranked_docs=[doc])
        self.assertEqual(service.retrieval("低相关问题"), [])

    def test_retrieval_accepts_when_top_rerank_score_reaches_threshold(self):
        doc = FakeDocument("有效内容" * 20, {"document_id": "a", "final_rerank_score": settings.RAG_MIN_RERANK_SCORE})
        service = TrackingRetrievalService({"相关问题": [doc]}, reranked_docs=[doc])
        result = service.retrieval("相关问题")
        self.assertEqual(len(result), 1)

    def test_query_service_formats_context_without_document_repr(self):
        service = QueryService()
        doc = FakeDocument(
            "这是正文内容",
            {
                "title": "黑屏处理",
                "source_id": "faq/black-screen.md",
                "final_rerank_score": 0.88,
            },
        )
        context_text = service._format_retrieval_context([doc])
        self.assertIn("资料1", context_text)
        self.assertIn("标题：黑屏处理", context_text)
        self.assertIn("正文：\n这是正文内容", context_text)
        self.assertNotIn("Document(", context_text)

    def test_query_service_prompt_uses_original_question(self):
        import sys

        fake_chat = sys.modules["langchain_openai"].ChatOpenAI
        service = QueryService()
        doc = FakeDocument("这是正文内容" * 10, {"title": "黑屏处理", "source_id": "faq.md", "final_rerank_score": 0.9})
        service.generate_answer("开不了机，屏幕不亮", [doc])
        self.assertIn("开不了机，屏幕不亮", fake_chat.last_prompt)
        self.assertNotIn("无法开机，黑屏", fake_chat.last_prompt)

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

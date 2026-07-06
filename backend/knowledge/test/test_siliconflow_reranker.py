import os
import sys
import unittest
from unittest.mock import patch


KNOWLEDGE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if KNOWLEDGE_ROOT not in sys.path:
    sys.path.insert(0, KNOWLEDGE_ROOT)


try:
    from langchain_core.documents import Document
except Exception:  # pragma: no cover
    from test_rag_control import install_fake_dependencies

    install_fake_dependencies()
    from langchain_core.documents import Document


from repositories.reranker_repository import RerankerError, SiliconFlowRerankerRepository
from services.retrieval_service import RetrievalService


class FakeVectorStore:
    def __init__(self):
        self.embedded_texts = []

    def embedd_document(self, text):
        return [1.0, 0.0]

    def embedd_documents(self, texts):
        self.embedded_texts.extend(texts)
        vectors = []
        for text in texts:
            if "doc-a" in text:
                vectors.append([1.0, 0.0])
            else:
                vectors.append([0.9, 0.1])
        return vectors


class FakeReranker:
    provider = "siliconflow"
    model = "Qwen/Qwen3-Reranker-8B"

    def __init__(self, scores):
        self.scores = scores
        self.calls = []
        self.last_call_stats = type("Stats", (), {"duration_ms": 12})()

    def rerank(self, query, documents, *, top_n=None):
        self.calls.append({"query": query, "documents": documents, "top_n": top_n})
        from repositories.reranker_repository import RerankCandidateResult

        ordered = sorted(enumerate(self.scores), key=lambda item: item[1], reverse=True)
        return [
            RerankCandidateResult(
                candidate_index=index,
                document_id="",
                chunk_id="",
                reranker_score=score,
                rank=rank,
            )
            for rank, (index, score) in enumerate(ordered, start=1)
        ]


def make_doc(text, title, *, source_id="secret/url.md"):
    return Document(
        page_content=text,
        metadata={
            "title": title,
            "source_id": source_id,
            "case_id": "case_999",
            "expected_answerability": "answerable",
            "expected_title_contains": ["should-not-leak"],
            "url": "https://example.com/private",
            "path": "D:/private/file.md",
            "document_id": title,
            "chunk_id": title,
        },
    )


class FakeResponse:
    def __init__(self, status_code=200, payload=None, text="", headers=None):
        self.status_code = status_code
        self._payload = payload
        self.text = text
        self.headers = headers or {}

    def json(self):
        if isinstance(self._payload, Exception):
            raise self._payload
        return self._payload


class FakeSession:
    def __init__(self, response):
        self.response = response
        self.payload = None
        self.headers = None

    def post(self, url, *, headers, json, timeout):
        self.payload = json
        self.headers = headers
        return self.response


class SiliconFlowRerankerTests(unittest.TestCase):
    def test_default_reranker_mode_off_does_not_instantiate_client(self):
        with patch("services.retrieval_service.SiliconFlowRerankerRepository") as factory:
            service = RetrievalService(chroma_vector=FakeVectorStore(), reranker_mode="off")

        self.assertEqual(service.reranker_mode, "off")
        factory.assert_not_called()

    def test_experimental_reranker_reorders_candidates_and_preserves_embedding_score(self):
        reranker = FakeReranker([0.2, 0.95])
        service = RetrievalService(
            chroma_vector=FakeVectorStore(),
            reranker_mode="experimental",
            reranker_repository=reranker,
        )
        docs = [
            make_doc("doc-a 有效资料" * 20, "A"),
            make_doc("doc-b 更相关资料" * 20, "B"),
        ]

        result = service.rerank_candidates("原始问题", docs)

        self.assertEqual(result[0].metadata["title"], "B")
        self.assertIn("embedding_rerank_score", result[0].metadata)
        self.assertEqual(result[0].metadata["ranking_base_score"], result[0].metadata["reranker_score"])
        self.assertEqual(result[0].metadata["final_rerank_score"], result[0].metadata["reranker_score"])
        self.assertEqual(service.reranker_success_count, 1)

    def test_off_mode_uses_embedding_score_as_ranking_base_score(self):
        service = RetrievalService(chroma_vector=FakeVectorStore(), reranker_mode="off")
        docs = [make_doc("doc-a 有效资料" * 20, "A")]

        result = service.rerank_candidates("原始问题", docs)

        self.assertEqual(result[0].metadata["ranking_base_score"], result[0].metadata["embedding_rerank_score"])
        self.assertNotIn("reranker_score", result[0].metadata)

    def test_anchor_adjustment_runs_after_reranker(self):
        reranker = FakeReranker([0.4])
        service = RetrievalService(
            chroma_vector=FakeVectorStore(),
            reranker_mode="experimental",
            reranker_repository=reranker,
            anchor_evidence_mode="experimental",
        )
        docs = [make_doc("0x0000007B 蓝屏 排查方法" * 20, "蓝屏")]

        result = service.rerank_candidates("蓝屏 0x0000007B 怎么处理", docs)

        self.assertIn("evidence_adjusted_score", result[0].metadata)
        self.assertGreaterEqual(result[0].metadata["evidence_adjusted_score"], result[0].metadata["ranking_base_score"])

    def test_reranker_payload_excludes_eval_and_source_fields(self):
        reranker = FakeReranker([0.8])
        service = RetrievalService(
            chroma_vector=FakeVectorStore(),
            reranker_mode="experimental",
            reranker_repository=reranker,
        )
        docs = [make_doc("正文内容" * 40, "安全标题")]

        service.rerank_candidates("原始问题", docs)

        payload_text = reranker.calls[0]["documents"][0]
        for forbidden in ["case_999", "expected_answerability", "expected_title_contains", "source_id", "https://", "D:/private"]:
            self.assertNotIn(forbidden, payload_text)
        self.assertIn("标题:", payload_text)
        self.assertIn("正文:", payload_text)

    def test_repository_parses_valid_response_and_sends_contract_payload(self):
        session = FakeSession(FakeResponse(payload={"results": [{"index": 1, "relevance_score": 0.9}, {"index": 0, "relevance_score": 0.2}]}))
        repo = SiliconFlowRerankerRepository(api_key="test-key", session=session)

        results = repo.rerank("问题", ["doc0", "doc1"], top_n=2)

        self.assertEqual([item.candidate_index for item in results], [1, 0])
        self.assertEqual(session.payload["model"], "Qwen/Qwen3-Reranker-8B")
        self.assertEqual(session.payload["query"], "问题")
        self.assertEqual(session.payload["documents"], ["doc0", "doc1"])
        self.assertFalse(session.payload["return_documents"])
        self.assertIn("Authorization", session.headers)

    def test_repository_fails_on_missing_results(self):
        repo = SiliconFlowRerankerRepository(api_key="test-key", session=FakeSession(FakeResponse(payload={})))

        with self.assertRaises(RerankerError):
            repo.rerank("问题", ["doc0"])

    def test_repository_fails_on_duplicate_index(self):
        payload = {"results": [{"index": 0, "relevance_score": 0.9}, {"index": 0, "relevance_score": 0.8}]}
        repo = SiliconFlowRerankerRepository(api_key="test-key", session=FakeSession(FakeResponse(payload=payload)))

        with self.assertRaises(RerankerError):
            repo.rerank("问题", ["doc0", "doc1"])

    def test_repository_fails_on_invalid_index(self):
        payload = {"results": [{"index": 2, "relevance_score": 0.9}]}
        repo = SiliconFlowRerankerRepository(api_key="test-key", session=FakeSession(FakeResponse(payload=payload)))

        with self.assertRaises(RerankerError):
            repo.rerank("问题", ["doc0"])

    def test_repository_fails_on_missing_or_non_numeric_score(self):
        for payload in (
            {"results": [{"index": 0}]},
            {"results": [{"index": 0, "relevance_score": "bad"}]},
        ):
            repo = SiliconFlowRerankerRepository(api_key="test-key", session=FakeSession(FakeResponse(payload=payload)))
            with self.assertRaises(RerankerError):
                repo.rerank("问题", ["doc0"])

    def test_repository_http_error_does_not_fallback(self):
        repo = SiliconFlowRerankerRepository(
            api_key="test-key",
            session=FakeSession(FakeResponse(status_code=401, payload={}, text='{"error":"auth"}')),
        )

        with self.assertRaises(RerankerError):
            repo.rerank("问题", ["doc0"])


if __name__ == "__main__":
    unittest.main()

import os
import sys
import unittest
from dataclasses import dataclass, field


KNOWLEDGE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if KNOWLEDGE_ROOT not in sys.path:
    sys.path.insert(0, KNOWLEDGE_ROOT)

from services.retrieval_service import RetrievalService


@dataclass
class FakeDocument:
    page_content: str
    metadata: dict = field(default_factory=dict)


class FakeVectorStore:
    def embedd_document(self, text):
        return [1.0, 0.0]

    def embedd_documents(self, texts):
        vectors = []
        for text in texts:
            if "high semantic unrelated" in text:
                vectors.append([1.0, 0.0])
            else:
                vectors.append([0.94, 0.34])
        return vectors

    def search_similarity_with_score(self, user_question, top_k=None):
        return []


class AnchorEvidenceRetrievalTests(unittest.TestCase):
    def test_default_anchor_disabled_preserves_existing_rerank_order_and_metadata(self):
        service = RetrievalService(chroma_vector=FakeVectorStore(), anchor_evidence_enabled=False)
        docs = [
            FakeDocument("high semantic unrelated " * 20, {"title": "普通网络说明", "document_id": "a"}),
            FakeDocument("蓝屏报错代码 0x0000007B " * 20, {"title": "台式和一体机蓝屏报错代码：0x0000007B", "document_id": "b"}),
        ]

        result = service._reranking(docs, "电脑蓝屏报错 0x0000007B 怎么办")

        self.assertEqual(result[0].metadata["document_id"], "a")
        self.assertNotIn("evidence_adjusted_score", result[0].metadata)
        self.assertNotIn("anchor_adjustment", result[0].metadata)

    def test_experimental_anchor_mode_reorders_before_mmr_without_overwriting_original_score(self):
        service = RetrievalService(
            chroma_vector=FakeVectorStore(),
            anchor_evidence_enabled=True,
            anchor_match_boost=0.08,
            anchor_missing_penalty=0.12,
        )
        docs = [
            FakeDocument("high semantic unrelated " * 20, {"title": "普通网络说明", "document_id": "a"}),
            FakeDocument("蓝屏报错代码 0x0000007B " * 20, {"title": "台式和一体机蓝屏报错代码：0x0000007B", "document_id": "b"}),
        ]

        result = service._reranking(docs, "电脑蓝屏报错 0x0000007B 怎么办")

        self.assertEqual(result[0].metadata["document_id"], "b")
        self.assertIn("final_rerank_score", result[0].metadata)
        self.assertIn("evidence_adjusted_score", result[0].metadata)
        self.assertGreater(result[0].metadata["evidence_adjusted_score"], result[0].metadata["final_rerank_score"])

    def test_anchor_gate_blocks_when_final_topk_has_no_evidence(self):
        service = RetrievalService(chroma_vector=FakeVectorStore(), anchor_evidence_enabled=True)
        docs = [
            FakeDocument("普通内容 " * 20, {"title": "普通标题", "document_id": "a"}),
            FakeDocument("其他内容 " * 20, {"title": "其他标题", "document_id": "b"}),
        ]

        decision = service.evaluate_anchor_gate("火星基地打印机怎么连接量子网络", docs)

        self.assertFalse(decision["ok"])
        self.assertEqual(decision["reason_code"], "ANCHOR_EVIDENCE_MISSING")

    def test_anchor_gate_allows_when_any_final_doc_has_evidence(self):
        service = RetrievalService(chroma_vector=FakeVectorStore(), anchor_evidence_enabled=True)
        docs = [
            FakeDocument("普通内容 " * 20, {"title": "普通标题", "document_id": "a"}),
            FakeDocument("Excel 文件菜单灰色不可用 " * 20, {"title": "Excel文件菜单及相关功能灰色不可用怎么办？", "document_id": "b"}),
        ]

        decision = service.evaluate_anchor_gate("Excel 文件菜单和相关功能灰色不可用怎么办", docs)

        self.assertTrue(decision["ok"])

    def test_experimental_instance_does_not_pollute_default_instance(self):
        experimental = RetrievalService(chroma_vector=FakeVectorStore(), anchor_evidence_enabled=True)
        default = RetrievalService(chroma_vector=FakeVectorStore())

        self.assertTrue(experimental.is_anchor_evidence_enabled())
        self.assertFalse(default.is_anchor_evidence_enabled())


if __name__ == "__main__":
    unittest.main()

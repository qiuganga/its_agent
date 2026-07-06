import os
import shutil
import sys
import tempfile
import types
import unittest
from pathlib import Path
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


from repositories.bm25_repository import Bm25Repository, bm25_root_dir, tokenize_for_bm25
from scripts import build_clean_bm25_index
from scripts.compare_anchor_evidence_reports import validate_comparable_reports
from services.retrieval_service import RetrievalService


class FakeVectorStore:
    def __init__(self, vector_docs=None):
        self.vector_docs = vector_docs or []
        self.search_calls = 0

    def search_similarity_with_score(self, query):
        self.search_calls += 1
        return [(doc, 0.1) for doc in self.vector_docs]

    def embedd_document(self, text):
        return [1.0, 0.0, 0.0]

    def embedd_documents(self, texts):
        embeddings = []
        for text in texts:
            if "black screen" in text.lower() or "黑屏" in text:
                embeddings.append([1.0, 0.0, 0.0])
            elif "network" in text.lower() or "无线" in text:
                embeddings.append([0.8, 0.2, 0.0])
            else:
                embeddings.append([0.2, 0.8, 0.0])
        return embeddings


class FakeSplitter:
    document_spliter = None

    def __init__(self):
        self.document_spliter = self

    def split_text(self, text):
        return [text]


class FakeBm25Repository:
    def __init__(self, docs=None, load_error=None):
        self.docs = docs or []
        self.load_error = load_error
        self.search_calls = 0

    def load_index(self):
        if self.load_error:
            raise self.load_error

    def search(self, query, *, top_k=10, query_variant=None):
        self.search_calls += 1
        return list(self.docs)[:top_k]


def make_doc(text, *, route="vector", chunk_id="chunk-1", title="黑屏处理", source_id="doc.md", score=None):
    metadata = {
        "retrieval_route": route,
        "chunk_id": chunk_id,
        "document_id": "doc-1",
        "source_id": source_id,
        "chunk_index": 0,
        "title": title,
    }
    if score is not None:
        metadata["bm25_score"] = score
        metadata["matched_by_bm25_query"] = "屏幕不亮"
        metadata["bm25_query_variants"] = ["屏幕不亮"]
    return Document(page_content=text, metadata=metadata)


class Bm25RetrievalTest(unittest.TestCase):
    def service(self, *, vector_docs=None, bm25_mode="off", bm25_repo=None):
        return RetrievalService(
            chroma_vector=FakeVectorStore(vector_docs=vector_docs),
            spliter=FakeSplitter(),
            bm25_mode=bm25_mode,
            bm25_repository=bm25_repo,
        )

    def test_default_bm25_mode_is_off_and_does_not_call_repository(self):
        repo = FakeBm25Repository(docs=[make_doc("黑屏资料" * 20, route="bm25", chunk_id="bm25-1")])
        service = self.service(bm25_repo=repo)

        service.retrieve_candidates("黑屏")

        self.assertEqual(service.bm25_mode, "off")
        self.assertEqual(repo.search_calls, 0)

    def test_experimental_missing_bm25_index_fails_clearly(self):
        repo = FakeBm25Repository(load_error=FileNotFoundError("missing bm25 index"))

        with self.assertRaises(FileNotFoundError):
            self.service(bm25_mode="experimental", bm25_repo=repo)

    def test_experimental_bm25_adds_candidates_without_replacing_vector(self):
        vector_doc = make_doc("黑屏 vector 内容" * 20, route="vector", chunk_id="vector-1")
        bm25_doc = make_doc("黑屏 bm25 内容" * 20, route="bm25", chunk_id="bm25-1", score=8.5)
        repo = FakeBm25Repository(docs=[bm25_doc])
        service = self.service(vector_docs=[vector_doc], bm25_mode="experimental", bm25_repo=repo)

        candidates = service.retrieve_candidates("屏幕不亮")

        routes = [doc.metadata["retrieval_route"] for doc in candidates]
        self.assertIn("vector", routes)
        self.assertIn("bm25", routes)
        self.assertEqual(repo.search_calls, 1)

    def test_deduplicate_preserves_routes_and_bm25_metadata(self):
        vector_doc = make_doc("黑屏重复内容" * 20, route="vector", chunk_id="same")
        bm25_doc = make_doc("黑屏重复内容" * 20, route="bm25", chunk_id="same", score=7.2)
        service = self.service()

        unique = service._deduplicate([vector_doc, bm25_doc])

        self.assertEqual(len(unique), 1)
        self.assertEqual(unique[0].metadata["retrieval_routes"], ["vector", "bm25"])
        self.assertEqual(unique[0].metadata["bm25_score"], 7.2)
        self.assertEqual(unique[0].metadata["bm25_query_variants"], ["屏幕不亮"])

    def test_bm25_score_does_not_replace_final_rerank_score(self):
        bm25_doc = make_doc("black screen 黑屏 电脑无法显示" * 20, route="bm25", chunk_id="bm25-1", score=99.0)
        service = self.service(bm25_mode="experimental", bm25_repo=FakeBm25Repository(docs=[bm25_doc]))

        docs = service.rerank_candidates("黑屏", [bm25_doc])

        self.assertTrue(docs)
        self.assertEqual(docs[0].metadata["bm25_score"], 99.0)
        self.assertNotEqual(docs[0].metadata["final_rerank_score"], 99.0)

    def test_tokenizer_preserves_exact_error_code_and_model_tokens(self):
        tokens = tokenize_for_bm25("电脑蓝屏 0x0000007B Lenovo G485 ThinkPad X1 无法启动")

        self.assertIn("0x0000007b", tokens)
        self.assertIn("lenovo", tokens)
        self.assertIn("g485", tokens)
        self.assertIn("thinkpad", tokens)
        self.assertIn("x1", tokens)

    def test_tokenizer_strips_url_html_source_and_hash_noise(self):
        tokens = tokenize_for_bm25(
            "source_id=abc.md <div>黑屏</div> https://example.com/a "
            "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        )

        joined = " ".join(tokens)
        self.assertIn("黑屏", joined)
        self.assertNotIn("source_id", joined)
        self.assertNotIn("https", joined)
        self.assertNotIn("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", joined)

    def test_bm25_manifest_validates_chunk_count_and_source_id(self):
        temp_dir = Path(tempfile.mkdtemp(prefix="bm25-test-"))
        try:
            index_dir = bm25_root_dir() / temp_dir.name
            repo = Bm25Repository(index_dir)
            docs = [make_doc("黑屏有效资料" * 20, route="bm25", chunk_id="chunk-1")]

            manifest = repo.build_index(
                docs,
                index_name=temp_dir.name,
                chunk_size=1500,
                chunk_overlap=200,
                collection_reference="its-knowledge-clean-v1",
                collection_chunk_count=1,
            )

            self.assertEqual(manifest["source_id_missing_count"], 0)
            self.assertTrue(manifest["chunk_count_match"])
            repo.load_index()
            self.assertEqual(len(repo.search("黑屏")), 1)
        finally:
            shutil.rmtree(bm25_root_dir() / temp_dir.name, ignore_errors=True)

    def test_build_clean_chunks_uses_stable_ids_and_cleaning(self):
        temp_dir = Path(tempfile.mkdtemp(prefix="bm25-md-"))
        try:
            md_path = temp_dir / "case.md"
            md_path.write_text("# 黑屏处理\n\n<script>bad</script>\n电脑黑屏无法开机。" * 8, encoding="utf-8")
            with patch("config.settings.settings.CRAWL_OUTPUT_DIR", str(temp_dir)):
                docs, manifest = build_clean_bm25_index.build_clean_chunks(
                    collection_name="its-knowledge-clean-v1",
                    chunk_size=1500,
                    chunk_overlap=200,
                    min_effective_chars=10,
                )
            self.assertEqual(manifest["source_id_missing_count"], 0)
            self.assertTrue(docs)
            self.assertEqual(docs[0].metadata["source_id"], "case.md")
            self.assertTrue(docs[0].metadata["chunk_id"])
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_retrieval_service_does_not_depend_on_eval_labels(self):
        paths = [
            Path(KNOWLEDGE_ROOT) / "services" / "retrieval_service.py",
            Path(KNOWLEDGE_ROOT) / "repositories" / "bm25_repository.py",
        ]
        forbidden = ["expected_answerability", "expected_title_contains", "case_id"]
        for path in paths:
            content = path.read_text(encoding="utf-8")
            for token in forbidden:
                self.assertNotIn(token, content)

    def test_comparison_validation_requires_82_cases_for_v2_82(self):
        baseline = {
            "cases_file": "rag_eval_cases_v2.json",
            "summary": {"total_cases": 24, "bm25_mode": "off"},
            "settings": {
                "collection_name": "its-knowledge-clean-v1",
                "RAG_ANCHOR_EVIDENCE_MODE": "hard-soft-negative",
                "EMBEDDING_MODEL": "Qwen/Qwen3-Embedding-8B",
                "VECTOR_DISTANCE_SPACE": "cosine",
                "RAG_VECTOR_CANDIDATE_TOP_K": 15,
                "RAG_TITLE_CANDIDATE_TOP_K": 10,
                "RAG_FINAL_TOP_K": 2,
                "RAG_MIN_RERANK_SCORE": 0.35,
            },
        }
        experiment = {
            **baseline,
            "summary": {"total_cases": 24, "bm25_mode": "experimental"},
        }

        with self.assertRaises(ValueError):
            validate_comparable_reports(baseline, experiment, expected_total_cases=82)

    def test_comparison_validation_accepts_only_bm25_difference(self):
        baseline = {
            "cases_file": "rag_eval_cases_v2.json",
            "summary": {"total_cases": 82, "bm25_mode": "off"},
            "settings": {
                "collection_name": "its-knowledge-clean-v1",
                "RAG_ANCHOR_EVIDENCE_MODE": "hard-soft-negative",
                "EMBEDDING_MODEL": "Qwen/Qwen3-Embedding-8B",
                "VECTOR_DISTANCE_SPACE": "cosine",
                "RAG_VECTOR_CANDIDATE_TOP_K": 15,
                "RAG_TITLE_CANDIDATE_TOP_K": 10,
                "RAG_FINAL_TOP_K": 2,
                "RAG_MIN_RERANK_SCORE": 0.35,
            },
        }
        experiment = {
            **baseline,
            "summary": {"total_cases": 82, "bm25_mode": "experimental"},
        }

        validate_comparable_reports(baseline, experiment, expected_total_cases=82)


if __name__ == "__main__":
    unittest.main()

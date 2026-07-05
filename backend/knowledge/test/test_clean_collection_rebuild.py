import sys
import tempfile
import unittest
from pathlib import Path


KNOWLEDGE_ROOT = Path(__file__).resolve().parents[1]
if str(KNOWLEDGE_ROOT) not in sys.path:
    sys.path.insert(0, str(KNOWLEDGE_ROOT))

from scripts.rebuild_clean_rag_collection import (
    REQUIRED_METADATA_FIELDS,
    build_documents,
    validate_collection_name,
)
from config.settings import settings


class CleanCollectionRebuildTests(unittest.TestCase):
    def test_refuses_production_collection(self):
        with self.assertRaises(ValueError):
            validate_collection_name("its-knowledge")

    def test_refuses_non_experiment_collection_prefix(self):
        with self.assertRaises(ValueError):
            validate_collection_name("other-clean-collection")

    def test_accepts_clean_experiment_collection_prefix(self):
        validate_collection_name("its-knowledge-clean-v1")

    def test_build_documents_writes_required_metadata(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            md_path = Path(tmpdir) / "001-test.md"
            md_path.write_text("这是一个足够长的清洗后测试文档。" * 10, encoding="utf-8")
            manifest = {
                "records": [
                    {
                        "source_path": str(md_path),
                        "source_id": "001-test.md",
                        "title": "test",
                        "indexable": True,
                    }
                ]
            }

            docs, ids, errors = build_documents(
                manifest,
                collection_name="its-knowledge-clean-test",
                chunk_size=1000,
                chunk_overlap=120,
            )

        self.assertGreater(len(docs), 0)
        self.assertEqual(len(docs), len(ids))
        self.assertEqual(errors, [])
        for field in REQUIRED_METADATA_FIELDS:
            self.assertIn(field, docs[0].metadata)
            self.assertIsNotNone(docs[0].metadata[field])

    def test_default_collection_setting_is_not_changed_by_experiment_helpers(self):
        self.assertEqual(settings.VECTOR_COLLECTION_NAME, "its-knowledge")


if __name__ == "__main__":
    unittest.main()

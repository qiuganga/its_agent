import sys
import unittest
from pathlib import Path


KNOWLEDGE_ROOT = Path(__file__).resolve().parents[1]
if str(KNOWLEDGE_ROOT) not in sys.path:
    sys.path.insert(0, str(KNOWLEDGE_ROOT))

from services.document_cleaning_service import clean_document_text, count_effective_content_chars, is_indexable


class DocumentCleaningTests(unittest.TestCase):
    def test_plain_markdown_image_and_url_do_not_count_as_effective_text(self):
        result = clean_document_text("![](https://example.com/step.png)\nhttps://example.com/detail?id=123")

        self.assertNotIn("https://", result.cleaned_text)
        self.assertEqual(result.image_markdown_count, 1)
        self.assertEqual(result.url_count, 2)
        self.assertFalse(is_indexable(result, min_effective_chars=80))

    def test_meaningful_image_alt_text_is_preserved_without_url(self):
        result = clean_document_text("![进入设备管理器界面](https://example.com/step.png)")

        self.assertIn("进入设备管理器界面", result.cleaned_text)
        self.assertNotIn("https://", result.cleaned_text)

    def test_markdown_link_keeps_anchor_and_removes_url(self):
        result = clean_document_text("[打开设备管理器](https://example.com/detail)")

        self.assertIn("打开设备管理器", result.cleaned_text)
        self.assertNotIn("https://", result.cleaned_text)

    def test_bare_url_and_html_tags_are_removed(self):
        result = clean_document_text("<p>解决方案</p> https://example.com/a.png")

        self.assertIn("解决方案", result.cleaned_text)
        self.assertNotIn("<p>", result.cleaned_text)
        self.assertNotIn("https://", result.cleaned_text)
        self.assertEqual(result.html_tag_count, 2)

    def test_metadata_lines_are_removed(self):
        result = clean_document_text("文档来源: abc\n创建时间: 2020\n真正的解决步骤如下。")

        self.assertNotIn("文档来源", result.cleaned_text)
        self.assertNotIn("创建时间", result.cleaned_text)
        self.assertIn("真正的解决步骤如下", result.cleaned_text)
        self.assertEqual(result.removed_metadata_blocks, 2)

    def test_low_effective_content_is_not_indexable(self):
        result = clean_document_text("![](https://a.com/1.png)\n![](https://a.com/2.png)")

        self.assertFalse(is_indexable(result, min_effective_chars=80))

    def test_many_images_and_little_text_marks_mineru_candidate(self):
        result = clean_document_text(
            "![](https://a.com/1.png)\n![](https://a.com/2.png)\n![图](https://a.com/3.png)\n少量文字"
        )

        self.assertTrue(result.mineru_candidate)

    def test_cleaning_is_stable(self):
        raw = "![进入设备管理器界面](https://example.com/step.png)\n<p>打开蓝牙设置</p>"

        first = clean_document_text(raw)
        second = clean_document_text(raw)

        self.assertEqual(first.cleaned_text, second.cleaned_text)
        self.assertEqual(first.content_hash, second.content_hash)

    def test_effective_char_count_ignores_urls_and_html(self):
        count = count_effective_content_chars("<p>ABC中文</p> https://example.com/a.png")

        self.assertEqual(count, len("ABC中文"))


if __name__ == "__main__":
    unittest.main()

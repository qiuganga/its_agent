from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field


MEANINGLESS_ALT_TEXT = {
    "",
    "图片",
    "截图",
    "图",
    "image",
    "img",
    "png",
    "jpg",
    "jpeg",
    "gif",
}


@dataclass(frozen=True)
class CleanedDocumentResult:
    raw_text: str
    cleaned_text: str
    original_char_count: int
    cleaned_char_count: int
    effective_content_chars: int
    image_markdown_count: int
    url_count: int
    html_tag_count: int
    removed_metadata_blocks: int
    mineru_candidate: bool
    content_hash: str
    paragraph_count: int


def clean_document_text(raw_markdown: str) -> CleanedDocumentResult:
    raw_text = raw_markdown or ""
    image_markdown_count = len(re.findall(r"!\[[^\]]*]\([^)]+\)", raw_text))
    url_count = len(re.findall(r"https?://[^\s)>\]]+", raw_text))
    html_tag_count = len(re.findall(r"<[^>]+>", raw_text))

    text, removed_metadata_blocks = _remove_metadata_lines(raw_text)
    text = _replace_markdown_images(text)
    text = _replace_markdown_links(text)
    text = re.sub(r"https?://[^\s)>\]]+", " ", text)
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    text = _remove_navigation_noise(text)
    text = _normalize_markdown_text(text)

    effective_chars = count_effective_content_chars(text)
    paragraph_count = len([line for line in text.splitlines() if len(line.strip()) >= 12])
    mineru_candidate = _is_mineru_candidate(
        raw_text=raw_text,
        image_markdown_count=image_markdown_count,
        paragraph_count=paragraph_count,
        effective_chars=effective_chars,
    )
    return CleanedDocumentResult(
        raw_text=raw_text,
        cleaned_text=text,
        original_char_count=len(raw_text),
        cleaned_char_count=len(text),
        effective_content_chars=effective_chars,
        image_markdown_count=image_markdown_count,
        url_count=url_count,
        html_tag_count=html_tag_count,
        removed_metadata_blocks=removed_metadata_blocks,
        mineru_candidate=mineru_candidate,
        content_hash=hashlib.sha256(text.encode("utf-8")).hexdigest(),
        paragraph_count=paragraph_count,
    )


def count_effective_content_chars(text: str) -> int:
    without_urls = re.sub(r"https?://[^\s)>\]]+", " ", text or "")
    without_html = re.sub(r"<[^>]+>", " ", without_urls)
    effective = re.findall(r"[\u4e00-\u9fffA-Za-z0-9，。；：？！、,.!?;:()（）《》-]", without_html)
    return len(effective)


def is_indexable(cleaned_result: CleanedDocumentResult, min_effective_chars: int = 80) -> bool:
    return cleaned_result.effective_content_chars >= min_effective_chars


def _replace_markdown_images(text: str) -> str:
    def replace(match: re.Match) -> str:
        alt_text = (match.group(1) or "").strip()
        normalized = re.sub(r"\s+", " ", alt_text).strip()
        if normalized.lower() in MEANINGLESS_ALT_TEXT:
            return " "
        if len(normalized) < 4 and not re.search(r"[\u4e00-\u9fffA-Za-z0-9]", normalized):
            return " "
        return f"\n{normalized}\n"

    return re.sub(r"!\[([^\]]*)]\(([^)]+)\)", replace, text or "")


def _replace_markdown_links(text: str) -> str:
    return re.sub(r"(?<!!)\[([^\]]+)]\((https?://[^)]+)\)", r"\1", text or "")


def _remove_metadata_lines(text: str) -> tuple[str, int]:
    metadata_patterns = [
        r"^\s*文档来源[:：].*$",
        r"^\s*知识库编号[:：].*$",
        r"^\s*创建时间[:：].*$",
        r"^\s*更新时间[:：].*$",
        r"^\s*版本号?[:：].*$",
        r"^\s*版本[:：].*$",
        r"^\s*分类[:：]\s*$",
        r"^\s*关键词[:：]\s*$",
        r"^\s*##\s*元信息\s*$",
    ]
    removed = 0
    kept_lines = []
    for line in (text or "").splitlines():
        if any(re.search(pattern, line, flags=re.IGNORECASE) for pattern in metadata_patterns):
            removed += 1
            continue
        kept_lines.append(line)
    return "\n".join(kept_lines), removed


def _remove_navigation_noise(text: str) -> str:
    noise_patterns = [
        r"^\s*上一篇[:：].*$",
        r"^\s*下一篇[:：].*$",
        r"^\s*返回顶部\s*$",
        r"^\s*相关链接[:：].*$",
        r"^\s*更多信息[:：].*$",
        r"^\s*点击(这里|此处).*$",
        r"^\s*联想专家一对一.*$",
    ]
    lines = []
    for line in (text or "").splitlines():
        if any(re.search(pattern, line, flags=re.IGNORECASE) for pattern in noise_patterns):
            continue
        lines.append(line)
    return "\n".join(lines)


def _normalize_markdown_text(text: str) -> str:
    normalized_lines = []
    previous = None
    for line in (text or "").splitlines():
        cleaned = re.sub(r"[ \t]+", " ", line).strip()
        cleaned = re.sub(r"!\[\]\([^)]*\)", " ", cleaned)
        cleaned = cleaned.strip()
        if not cleaned:
            if normalized_lines and normalized_lines[-1] != "":
                normalized_lines.append("")
            continue
        if cleaned == previous:
            continue
        normalized_lines.append(cleaned)
        previous = cleaned
    text = "\n".join(normalized_lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _is_mineru_candidate(
    *,
    raw_text: str,
    image_markdown_count: int,
    paragraph_count: int,
    effective_chars: int,
) -> bool:
    image_url_count = len(re.findall(r"https?://[^\s)>\]]+\.(?:png|jpe?g|gif|webp)", raw_text or "", flags=re.I))
    if image_markdown_count >= 2 and effective_chars < 150:
        return True
    if image_markdown_count > paragraph_count and effective_chars < 300:
        return True
    if len(raw_text or "") > 1000 and effective_chars < 80:
        return True
    if image_url_count >= 2 and effective_chars < 150:
        return True
    return False

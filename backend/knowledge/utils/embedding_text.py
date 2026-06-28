import hashlib
import os
import re


SOURCE_PREFIX = "文档来源:"


def normalize_title(title: str | None) -> str:
    value = (title or "").strip()
    value = os.path.basename(value)
    if value.lower().endswith(".md"):
        value = value[:-3]
    value = re.sub(r"\s+", " ", value).strip()
    return value or "unknown-source"


def strip_existing_source_prefixes(content: str) -> str:
    text = (content or "").strip()
    while True:
        stripped = re.sub(rf"^\s*{re.escape(SOURCE_PREFIX)}[^\n]*(?:\n|$)", "", text, count=1).strip()
        if stripped == text:
            return stripped
        text = stripped


def _strip_html_comments(content: str) -> str:
    return re.sub(r"<!--.*?-->", "", content or "", flags=re.DOTALL).strip()


def has_effective_content(content: str | None) -> bool:
    text = strip_existing_source_prefixes(_strip_html_comments(content or ""))
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return False
    if len(lines) == 1 and lines[0].startswith("#"):
        return False
    return bool("\n".join(lines).strip())


def build_embedding_text(title: str | None, content: str | None) -> str:
    normalized_title = normalize_title(title)
    cleaned_content = strip_existing_source_prefixes(_strip_html_comments(content or ""))
    lines = [line.rstrip() for line in cleaned_content.splitlines()]
    cleaned_content = "\n".join(lines).strip()
    if not has_effective_content(cleaned_content):
        cleaned_content = ""
    return f"{SOURCE_PREFIX}{normalized_title}\n{cleaned_content}".strip()


def build_content_hash(content: str) -> str:
    return hashlib.sha256((content or "").encode("utf-8")).hexdigest()


def build_document_id(source_id: str) -> str:
    normalized_source = re.sub(r"\s+", " ", (source_id or "unknown-source").strip())
    return hashlib.sha256(normalized_source.encode("utf-8")).hexdigest()


def build_chunk_id(document_id: str, chunk_index: int, canonical_content: str) -> str:
    raw = f"{document_id}:{chunk_index}:{build_content_hash(canonical_content)}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AliasRule:
    canonical: str
    alias: str


class AliasMappingService:
    """Apply canonical entity aliases after query normalization."""

    def __init__(self, aliases_path: str | os.PathLike[str] | None = None) -> None:
        self.aliases_path = Path(aliases_path) if aliases_path else self._default_aliases_path()
        self.alias_map = self._load_aliases(self.aliases_path)
        self.rules = self._build_rules(self.alias_map)
        self.last_alias_applied = False

    def map_alias(self, query: str | None) -> str:
        text = query or ""
        if not text or not self.rules:
            self.last_alias_applied = False
            return text

        protected_spans = self._canonical_spans(text)
        candidates = []
        for rule in self.rules:
            for match in re.finditer(re.escape(rule.alias), text, flags=re.IGNORECASE):
                start, end = match.span()
                if self._overlaps_any(start, end, protected_spans):
                    continue
                if self._is_embedded_ascii_token(text, start, end):
                    continue
                candidates.append((start, end, len(rule.alias), rule.canonical))

        if not candidates:
            self.last_alias_applied = False
            return text

        candidates.sort(key=lambda item: (item[0], -item[2]))
        selected = []
        occupied: list[tuple[int, int]] = []
        for start, end, _, canonical in candidates:
            if self._overlaps_any(start, end, occupied):
                continue
            selected.append((start, end, canonical))
            occupied.append((start, end))

        if not selected:
            self.last_alias_applied = False
            return text

        parts = []
        cursor = 0
        for start, end, canonical in sorted(selected, key=lambda item: item[0]):
            parts.append(text[cursor:start])
            parts.append(canonical)
            cursor = end
        parts.append(text[cursor:])
        mapped = "".join(parts)
        self.last_alias_applied = mapped != text
        return mapped

    def _canonical_spans(self, text: str) -> list[tuple[int, int]]:
        spans = []
        for canonical in self.alias_map:
            for match in re.finditer(re.escape(canonical), text):
                spans.append(match.span())
        return spans

    @staticmethod
    def _overlaps_any(start: int, end: int, spans: list[tuple[int, int]]) -> bool:
        return any(start < span_end and end > span_start for span_start, span_end in spans)

    @staticmethod
    def _is_embedded_ascii_token(text: str, start: int, end: int) -> bool:
        previous_char = text[start - 1] if start > 0 else ""
        next_char = text[end] if end < len(text) else ""
        current = text[start:end]
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9 ._-]*[A-Za-z0-9]", current) and not re.fullmatch(r"[A-Za-z0-9]+", current):
            return False
        return bool(
            (previous_char and re.match(r"[A-Za-z0-9_]", previous_char))
            or (next_char and re.match(r"[A-Za-z0-9_]", next_char))
        )

    @staticmethod
    def _build_rules(alias_map: dict[str, list[str]]) -> list[AliasRule]:
        rules = []
        seen_aliases = set()
        for canonical, aliases in alias_map.items():
            for alias in aliases:
                alias = alias.strip()
                if not alias:
                    continue
                key = alias.casefold()
                if alias == canonical or key in seen_aliases:
                    continue
                seen_aliases.add(key)
                rules.append(AliasRule(canonical=canonical, alias=alias))
        return sorted(rules, key=lambda rule: len(rule.alias), reverse=True)

    @staticmethod
    def _load_aliases(path: Path) -> dict[str, list[str]]:
        aliases: dict[str, list[str]] = {}
        if not path.exists():
            return aliases
        current_key = None
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if not raw_line.startswith(" ") and line.endswith(":"):
                current_key = line[:-1].strip()
                aliases.setdefault(current_key, [])
                continue
            if current_key and line.startswith("- "):
                aliases[current_key].append(line[2:].strip())
        return aliases

    @staticmethod
    def _default_aliases_path() -> Path:
        return Path(__file__).resolve().parents[1] / "config" / "query_aliases.yaml"


query_alias_mapping_service = AliasMappingService()

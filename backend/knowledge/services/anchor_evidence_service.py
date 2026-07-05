from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


ANCHOR_TYPE_HARD = "HARD"
ANCHOR_TYPE_SOFT = "SOFT"
ANCHOR_TYPE_NEGATIVE = "NEGATIVE"
ANCHOR_TYPE_GENERIC = "GENERIC"

NO_STRONG_ANCHOR = "NO_STRONG_ANCHOR"
NO_ANCHOR_EVIDENCE = "NO_ANCHOR_EVIDENCE"
PARTIAL_ANCHOR_EVIDENCE = "PARTIAL_ANCHOR_EVIDENCE"
FULL_ANCHOR_EVIDENCE = "FULL_ANCHOR_EVIDENCE"
ANCHOR_EVIDENCE_MISSING = "ANCHOR_EVIDENCE_MISSING"
HARD_EVIDENCE_EXISTS_OUTSIDE_TOPK = "HARD_EVIDENCE_EXISTS_OUTSIDE_TOPK"


GENERIC_TERMS = {
    "computer",
    "system",
    "network",
    "device",
    "file",
    "picture",
    "black screen",
    "boot",
    "startup",
    "issue",
    "problem",
    "电脑",
    "系统",
    "网络",
    "设备",
    "文件",
    "图片",
    "黑屏",
    "开机",
    "启动",
}

SOFT_ANCHOR_ALIASES: dict[str, tuple[str, ...]] = {
    "Windows": ("windows",),
    "BIOS": ("bios",),
    "Outlook": ("outlook",),
    "Word": ("word",),
    "Excel": ("excel",),
    "Bluetooth": ("bluetooth", "蓝牙"),
    "蓝牙设备": ("bluetooth", "蓝牙", "蓝牙设备"),
    "Wi-Fi": ("wi-fi", "wifi", "wireless network", "无线网络"),
    "printer driver": ("printer driver", "打印机驱动", "打印机硬件驱动程序"),
    "Office": ("office",),
    "display brightness": ("display brightness", "screen brightness", "屏幕亮度", "屏幕的亮度"),
    "blue screen": ("blue screen", "蓝屏"),
    "startup": ("startup", "boot", "开机", "启动"),
}

HARD_PHRASE_ALIASES: dict[str, tuple[str, ...]] = {
    "折叠屏铰链": ("folding screen hinge", "折叠屏铰链"),
    "量子网络": ("quantum network", "量子网络"),
    "冰箱冷冻室": ("freezer cold room", "冰箱冷冻室"),
    "任务栏输入法图标": ("taskbar input method icon", "任务栏输入法图标"),
    "无线键鼠": (
        "wireless keyboard and mouse",
        "wireless keyboard mouse",
        "无线键盘鼠标",
        "无线键鼠",
    ),
}

ALIAS_GROUPS: tuple[tuple[str, ...], ...] = tuple(
    tuple(dict.fromkeys(values)) for values in [*SOFT_ANCHOR_ALIASES.values(), *HARD_PHRASE_ALIASES.values()]
)

ERROR_CODE_RE = re.compile(
    r"(?<![A-Za-z0-9])(?:0x[0-9a-fA-F]{6,10}|[A-Z][A-Z]?\d{3,6})(?![A-Za-z0-9])"
)
HTTP_STATUS_RE = re.compile(r"(?<![A-Za-z0-9])(?:404|500)(?![A-Za-z0-9])")
MODEL_RE = re.compile(
    r"\b(?:ThinkPad\s+X\d{1,2}|Lenovo\s+G\d{3,4}|[A-Z]{1,3}\d{3,5})\b",
    re.IGNORECASE,
)
NEGATION_RE = re.compile(
    r"(?:not\s+(?:a\s+|an\s+)?|non-|不是|非|不属于|不是.*?)([A-Za-z][A-Za-z0-9+\-. ]{1,40}|[\u4e00-\u9fffA-Za-z0-9+\-. ]{1,20})",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Anchor:
    term: str
    normalized_term: str
    anchor_type: str
    aliases: tuple[str, ...] = field(default_factory=tuple)
    source: str = "rule"

    @property
    def kind(self) -> str:
        return self.source


@dataclass
class DocumentEvidence:
    anchor_terms: list[str]
    matched_anchor_terms: list[str]
    missing_anchor_terms: list[str]
    anchor_coverage_ratio: float | None
    anchor_evidence_status: str
    matched_locations: dict[str, list[str]]
    hard_anchor_terms: list[str] = field(default_factory=list)
    soft_anchor_terms: list[str] = field(default_factory=list)
    negative_anchor_terms: list[str] = field(default_factory=list)
    matched_hard_anchor_terms: list[str] = field(default_factory=list)
    matched_soft_anchor_terms: list[str] = field(default_factory=list)
    matched_negative_anchor_terms: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "anchor_terms": self.anchor_terms,
            "matched_anchor_terms": self.matched_anchor_terms,
            "missing_anchor_terms": self.missing_anchor_terms,
            "anchor_coverage_ratio": self.anchor_coverage_ratio,
            "anchor_evidence_status": self.anchor_evidence_status,
            "matched_locations": self.matched_locations,
            "hard_anchor_terms": self.hard_anchor_terms,
            "soft_anchor_terms": self.soft_anchor_terms,
            "negative_anchor_terms": self.negative_anchor_terms,
            "matched_hard_anchor_terms": self.matched_hard_anchor_terms,
            "matched_soft_anchor_terms": self.matched_soft_anchor_terms,
            "matched_negative_anchor_terms": self.matched_negative_anchor_terms,
        }


@dataclass
class RetrievalEvidenceDecision:
    ok: bool
    reason_code: str | None
    message: str
    anchors: list[str]
    matched_anchor_terms: list[str]
    final_top_k_statuses: list[str]
    hard_anchors: list[str] = field(default_factory=list)
    soft_anchors: list[str] = field(default_factory=list)
    negative_anchors: list[str] = field(default_factory=list)
    candidate_window_statuses: list[str] = field(default_factory=list)
    hard_evidence_exists_outside_topk: bool = False

    def as_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "reason_code": self.reason_code,
            "message": self.message,
            "anchor_evidence": {
                "anchors": self.anchors,
                "hard_anchors": self.hard_anchors,
                "soft_anchors": self.soft_anchors,
                "negative_anchors": self.negative_anchors,
                "matched_anchor_terms": self.matched_anchor_terms,
                "final_top_k_statuses": self.final_top_k_statuses,
                "candidate_window_statuses": self.candidate_window_statuses,
                "hard_evidence_exists_outside_topk": self.hard_evidence_exists_outside_topk,
            },
        }


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", "", (text or "").lower())


def normalize_phrase(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip()).lower()


def aliases_for(term: str) -> tuple[str, ...]:
    normalized = normalize_phrase(term)
    aliases = {term, normalized}
    for group in ALIAS_GROUPS:
        if any(normalize_phrase(item) == normalized for item in group):
            aliases.update(group)
    return tuple(sorted({item for item in aliases if item}))


def extract_anchors(original_question: str) -> list[Anchor]:
    text = original_question or ""
    anchors: list[Anchor] = []
    seen: set[tuple[str, str]] = set()
    negative_terms = _extract_negative_terms(text)

    def add(term: str, anchor_type: str, source: str, aliases: tuple[str, ...] | None = None) -> None:
        clean = re.sub(r"\s+", " ", (term or "").strip())
        normalized = normalize_phrase(clean)
        if not clean or not normalized:
            return
        if (normalized, anchor_type) in seen:
            return
        seen.add((normalized, anchor_type))
        anchors.append(
            Anchor(
                term=clean,
                normalized_term=normalized,
                anchor_type=anchor_type,
                aliases=aliases or aliases_for(clean),
                source=source,
            )
        )

    for term in negative_terms:
        add(term, ANCHOR_TYPE_NEGATIVE, "negative_phrase", aliases_for(term))

    negative_aliases = {normalize_phrase(alias) for term in negative_terms for alias in aliases_for(term)}

    for match in ERROR_CODE_RE.finditer(text):
        add(match.group(0), ANCHOR_TYPE_HARD, "error_code", (match.group(0),))
    for match in HTTP_STATUS_RE.finditer(text):
        add(match.group(0), ANCHOR_TYPE_HARD, "error_code", (match.group(0),))
    for match in MODEL_RE.finditer(text):
        add(match.group(0), ANCHOR_TYPE_HARD, "model", (match.group(0),))
    for term, aliases in HARD_PHRASE_ALIASES.items():
        if _text_contains_any_alias(text, aliases):
            add(term, ANCHOR_TYPE_HARD, "configured_hard_phrase", aliases)
    for term, aliases in SOFT_ANCHOR_ALIASES.items():
        if _text_contains_any_alias(text, aliases) and normalize_phrase(term) not in negative_aliases:
            add(term, ANCHOR_TYPE_SOFT, "configured_soft_phrase", aliases)
    for term in sorted(GENERIC_TERMS, key=len, reverse=True):
        if term and _text_contains_any_alias(text, (term,)):
            add(term, ANCHOR_TYPE_GENERIC, "generic_term", (term,))
    return anchors


def extract_strong_anchors(original_question: str) -> list[Anchor]:
    return [anchor for anchor in extract_anchors(original_question) if anchor.anchor_type in {ANCHOR_TYPE_HARD, ANCHOR_TYPE_SOFT}]


def extract_hard_anchors(original_question: str) -> list[Anchor]:
    return [anchor for anchor in extract_anchors(original_question) if anchor.anchor_type == ANCHOR_TYPE_HARD]


def evaluate_document_evidence(anchors: list[Anchor], document: Any) -> DocumentEvidence:
    evidence_anchors = [anchor for anchor in anchors if anchor.anchor_type in {ANCHOR_TYPE_HARD, ANCHOR_TYPE_SOFT, ANCHOR_TYPE_NEGATIVE}]
    anchor_terms = [anchor.term for anchor in evidence_anchors]
    hard_terms = [anchor.term for anchor in evidence_anchors if anchor.anchor_type == ANCHOR_TYPE_HARD]
    soft_terms = [anchor.term for anchor in evidence_anchors if anchor.anchor_type == ANCHOR_TYPE_SOFT]
    negative_terms = [anchor.term for anchor in evidence_anchors if anchor.anchor_type == ANCHOR_TYPE_NEGATIVE]
    matched_locations = {"title": [], "keywords": [], "content": []}
    if not evidence_anchors:
        return DocumentEvidence(anchor_terms, [], [], None, NO_STRONG_ANCHOR, matched_locations)

    metadata = getattr(document, "metadata", None) or {}
    fields = {
        "title": str(metadata.get("title") or ""),
        "keywords": str(metadata.get("keywords") or ""),
        "content": str(getattr(document, "page_content", "") or ""),
    }

    matched: list[str] = []
    matched_hard: list[str] = []
    matched_soft: list[str] = []
    matched_negative: list[str] = []
    for anchor in evidence_anchors:
        aliases = set(anchor.aliases or (anchor.term,))
        aliases.add(anchor.term)
        anchor_matched = False
        for location, value in fields.items():
            if _matches_any_alias(anchor, aliases, value):
                matched_locations[location].append(anchor.term)
                anchor_matched = True
        if anchor_matched:
            matched.append(anchor.term)
            if anchor.anchor_type == ANCHOR_TYPE_HARD:
                matched_hard.append(anchor.term)
            elif anchor.anchor_type == ANCHOR_TYPE_SOFT:
                matched_soft.append(anchor.term)
            elif anchor.anchor_type == ANCHOR_TYPE_NEGATIVE:
                matched_negative.append(anchor.term)

    positive_terms = hard_terms + soft_terms
    positive_matched = [term for term in matched if term in positive_terms]
    missing = [term for term in positive_terms if term not in positive_matched]
    ratio = len(positive_matched) / len(positive_terms) if positive_terms else None
    if not positive_terms:
        status = NO_STRONG_ANCHOR
    elif not positive_matched:
        status = NO_ANCHOR_EVIDENCE
    elif len(positive_matched) == len(positive_terms):
        status = FULL_ANCHOR_EVIDENCE
    else:
        status = PARTIAL_ANCHOR_EVIDENCE
    return DocumentEvidence(
        anchor_terms,
        matched,
        missing,
        ratio,
        status,
        matched_locations,
        hard_terms,
        soft_terms,
        negative_terms,
        matched_hard,
        matched_soft,
        matched_negative,
    )


def evaluate_retrieval_evidence(original_question: str, ranked_documents: list[Any]) -> RetrievalEvidenceDecision:
    anchors = extract_strong_anchors(original_question)
    anchor_terms = [anchor.term for anchor in anchors]
    if not anchors:
        return RetrievalEvidenceDecision(True, None, "No strong anchor was extracted.", [], [], [])

    document_evidence = [evaluate_document_evidence(anchors, document) for document in ranked_documents]
    matched = sorted({term for evidence in document_evidence for term in evidence.matched_anchor_terms})
    statuses = [evidence.anchor_evidence_status for evidence in document_evidence]
    if matched:
        return RetrievalEvidenceDecision(True, None, "At least one final document contains anchor evidence.", anchor_terms, matched, statuses)
    return RetrievalEvidenceDecision(
        False,
        ANCHOR_EVIDENCE_MISSING,
        "No final document contains the extracted anchor evidence.",
        anchor_terms,
        [],
        statuses,
    )


def evaluate_hard_soft_negative_gate(
    original_question: str,
    final_documents: list[Any],
    candidate_window_documents: list[Any],
) -> RetrievalEvidenceDecision:
    anchors = extract_anchors(original_question)
    hard_anchors = [anchor for anchor in anchors if anchor.anchor_type == ANCHOR_TYPE_HARD]
    soft_anchors = [anchor for anchor in anchors if anchor.anchor_type == ANCHOR_TYPE_SOFT]
    negative_anchors = [anchor for anchor in anchors if anchor.anchor_type == ANCHOR_TYPE_NEGATIVE]
    final_evidence = [evaluate_document_evidence(anchors, document) for document in final_documents]
    window_evidence = [evaluate_document_evidence(anchors, document) for document in candidate_window_documents]
    final_matched_hard = sorted({term for evidence in final_evidence for term in evidence.matched_hard_anchor_terms})
    window_matched_hard = sorted({term for evidence in window_evidence for term in evidence.matched_hard_anchor_terms})
    hard_terms = [anchor.term for anchor in hard_anchors]
    final_statuses = [evidence.anchor_evidence_status for evidence in final_evidence]
    window_statuses = [evidence.anchor_evidence_status for evidence in window_evidence]
    outside_topk = bool(window_matched_hard and not final_matched_hard)
    if not hard_anchors:
        return RetrievalEvidenceDecision(
            True,
            None,
            "No hard anchor was extracted; soft or negative anchors cannot trigger hard rejection.",
            [anchor.term for anchor in anchors],
            sorted({term for evidence in final_evidence for term in evidence.matched_anchor_terms}),
            final_statuses,
            hard_terms,
            [anchor.term for anchor in soft_anchors],
            [anchor.term for anchor in negative_anchors],
            window_statuses,
            outside_topk,
        )
    if window_matched_hard:
        reason = HARD_EVIDENCE_EXISTS_OUTSIDE_TOPK if outside_topk else None
        return RetrievalEvidenceDecision(
            True,
            reason,
            "Hard anchor evidence exists in the candidate window.",
            [anchor.term for anchor in anchors],
            window_matched_hard,
            final_statuses,
            hard_terms,
            [anchor.term for anchor in soft_anchors],
            [anchor.term for anchor in negative_anchors],
            window_statuses,
            outside_topk,
        )
    return RetrievalEvidenceDecision(
        False,
        ANCHOR_EVIDENCE_MISSING,
        "No candidate-window document contains hard anchor evidence.",
        [anchor.term for anchor in anchors],
        [],
        final_statuses,
        hard_terms,
        [anchor.term for anchor in soft_anchors],
        [anchor.term for anchor in negative_anchors],
        window_statuses,
        False,
    )


def apply_anchor_adjustment(
    original_question: str,
    documents: list[Any],
    *,
    match_boost: float = 0.08,
    missing_penalty: float = 0.10,
    hard_match_boost: float | None = None,
    hard_missing_penalty: float | None = None,
    soft_match_boost: float = 0.03,
    soft_missing_penalty: float = 0.0,
    negative_match_penalty: float = 0.10,
) -> list[tuple[Any, DocumentEvidence]]:
    anchors = extract_anchors(original_question)
    hard_match_boost = match_boost if hard_match_boost is None else hard_match_boost
    hard_missing_penalty = missing_penalty if hard_missing_penalty is None else hard_missing_penalty
    adjusted: list[tuple[Any, DocumentEvidence]] = []
    for document in documents:
        evidence = evaluate_document_evidence(anchors, document)
        metadata = dict(getattr(document, "metadata", None) or {})
        base_score = _to_float(metadata.get("final_rerank_score"), 0.0)
        hard_adjustment = 0.0
        soft_adjustment = 0.0
        negative_adjustment = 0.0
        if evidence.hard_anchor_terms:
            hard_adjustment = (
                float(hard_match_boost) * (len(evidence.matched_hard_anchor_terms) / len(evidence.hard_anchor_terms))
                if evidence.matched_hard_anchor_terms
                else -float(hard_missing_penalty)
            )
        if evidence.soft_anchor_terms and evidence.matched_soft_anchor_terms:
            soft_adjustment = float(soft_match_boost) * (
                len(evidence.matched_soft_anchor_terms) / len(evidence.soft_anchor_terms)
            )
        elif evidence.soft_anchor_terms:
            soft_adjustment = -float(soft_missing_penalty)
        positive_matched = bool(evidence.matched_hard_anchor_terms or evidence.matched_soft_anchor_terms)
        if evidence.matched_negative_anchor_terms and not positive_matched:
            negative_adjustment = -float(negative_match_penalty)
        total_adjustment = hard_adjustment + soft_adjustment + negative_adjustment
        metadata.update(evidence.as_dict())
        metadata["hard_anchor_adjustment"] = hard_adjustment
        metadata["soft_anchor_adjustment"] = soft_adjustment
        metadata["negative_anchor_adjustment"] = negative_adjustment
        metadata["anchor_adjustment"] = total_adjustment
        metadata["evidence_adjusted_score"] = max(base_score + total_adjustment, 0.0)
        document.metadata = metadata
        adjusted.append((document, evidence))
    return adjusted


def _extract_negative_terms(text: str) -> list[str]:
    found: list[str] = []
    lowered = text.lower()
    for term, aliases in {**SOFT_ANCHOR_ALIASES, **HARD_PHRASE_ALIASES}.items():
        for alias in aliases:
            alias_l = alias.lower()
            patterns = (
                f"not {alias_l}",
                f"not a {alias_l}",
                f"not an {alias_l}",
                f"non-{alias_l}",
                f"不是{alias}",
                f"不是 {alias}",
                f"非{alias}",
                f"非 {alias}",
                f"不属于{alias}",
                f"不属于 {alias}",
            )
            if any(pattern in lowered or pattern in text for pattern in patterns):
                found.append(term)
                break
    return list(dict.fromkeys(found))


def _text_contains_any_alias(text: str, aliases: tuple[str, ...]) -> bool:
    normalized_text = normalize_text(text)
    lowered = (text or "").lower()
    for alias in aliases:
        if not alias:
            continue
        normalized_alias = normalize_text(alias)
        if re.search(r"[A-Za-z]", alias):
            if re.search(rf"(?<![A-Za-z0-9]){re.escape(alias.lower())}(?![A-Za-z0-9])", lowered):
                return True
        elif normalized_alias and normalized_alias in normalized_text:
            return True
    return False


def _matches_any_alias(anchor: Anchor, aliases: set[str], value: str) -> bool:
    for alias in aliases:
        if not alias:
            continue
        if _text_contains_any_alias(value, (alias,)):
            if anchor.term == "Wi-Fi" and _text_contains_any_alias(value, ("wireless keyboard and mouse", "无线键鼠", "无线键盘鼠标")):
                continue
            return True
    return False


def _to_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default

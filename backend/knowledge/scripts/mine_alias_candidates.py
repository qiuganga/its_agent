"""Mine alias mapping candidates from offline RAG evaluation reports.

This script is intentionally offline: it only reads existing JSON/YAML files and
does not call embedding, reranker, Chroma, LLM, MCP, or network services.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


KNOWLEDGE_ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = KNOWLEDGE_ROOT / "config"
TESTDATA_DIR = KNOWLEDGE_ROOT / "testdata"

DEFAULT_ALIAS_FILE = CONFIG_DIR / "query_aliases.yaml"
DEFAULT_CASES_FILE = TESTDATA_DIR / "rag_eval_cases_v2.json"
DEFAULT_RERANKER_REPORT = TESTDATA_DIR / "rag_eval_report_v2_82_hsn_bm25_siliconflow_reranker.json"
DEFAULT_BM25_REPORT = TESTDATA_DIR / "rag_eval_report_v2_82_hsn_bm25_experimental.json"
DEFAULT_THRESHOLD_ANALYSIS = TESTDATA_DIR / "rag_threshold_analysis.json"
DEFAULT_OUTPUT_JSON = TESTDATA_DIR / "alias_candidate_suggestions.json"
DEFAULT_OUTPUT_MD = TESTDATA_DIR / "alias_candidate_suggestions.md"

GENERIC_TERMS = {
    "系统",
    "电脑",
    "文件",
    "问题",
    "怎么办",
    "处理",
    "异常",
    "失败",
    "无法",
    "不能",
    "设置",
    "设备",
    "用户",
    "方法",
    "使用",
    "安装",
    "软件",
    "程序",
    "功能",
    "提示",
}

KNOWN_ALIAS_GROUPS: dict[str, list[str]] = {
    "Wi-Fi": ["Wi-Fi", "wifi", "WiFi", "WIFI", "wireless", "Wireless", "无线网", "无线网络", "无线连接", "WLAN", "wlan"],
    "蓝牙": ["蓝牙", "Bluetooth", "bluetooth", "BT", "bt", "蓝牙设备"],
    "Microsoft Office": [
        "Microsoft Office",
        "Office",
        "office",
        "Office365",
        "office365",
        "Office 365",
        "Microsoft 365",
        "microsoft365",
        "O365",
        "o365",
    ],
    "Excel": ["Excel", "excel", "EXCEL", "xls", "xlsx", "Microsoft Excel"],
    "Word": ["Word", "word", "WORD", "doc", "docx", "Microsoft Word"],
    "Outlook": ["Outlook", "outlook", "OUTLOOK", "Microsoft Outlook"],
    "PowerPoint": ["PowerPoint", "powerpoint", "PPT", "ppt", "Microsoft PowerPoint"],
    "BIOS": ["BIOS", "bios", "UEFI", "uefi"],
    "ThinkPad": ["ThinkPad", "Think Pad", "think pad", "TP", "tp"],
    "Lenovo": ["Lenovo", "lenovo", "LENOVO", "联想", "联想电脑"],
    "Windows": ["Windows", "windows", "Win10", "win10", "Windows10", "windows10", "Win11", "win11", "Windows11", "windows11"],
    "Windows 7": ["Windows 7", "Windows7", "windows7", "Win7", "win7"],
    "Windows XP": ["Windows XP", "windows xp", "XP", "xp"],
    "打印机": ["打印机", "printer", "Printer", "打印设备"],
    "显卡驱动": ["显卡驱动", "graphics driver", "display driver", "GPU driver"],
    "任务栏输入法图标": ["任务栏输入法图标", "输入法图标", "语言栏", "language bar"],
}


@dataclass
class Evidence:
    case_id: str
    question_term: str | None
    document_term: str | None
    source: str
    reason: str


@dataclass
class Candidate:
    canonical: str
    aliases: set[str] = field(default_factory=set)
    evidence: list[Evidence] = field(default_factory=list)
    status: str = "new_suggestion"
    confidence_score: float = 0.0
    risk: str = "medium"

    @property
    def evidence_cases(self) -> list[str]:
        return sorted({item.case_id for item in self.evidence})


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_token(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip()).casefold()


def contains_term(text: str, term: str) -> bool:
    if not text or not term:
        return False
    return normalize_token(term) in normalize_token(text)


def load_existing_aliases(path: Path) -> tuple[dict[str, set[str]], set[str]]:
    """Parse the simple canonical: list YAML used by query_aliases.yaml."""
    groups: dict[str, set[str]] = {}
    current: str | None = None
    if not path.exists():
        return groups, set()

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if not line.startswith(" ") and line.endswith(":"):
            current = line[:-1].strip()
            groups.setdefault(current, set()).add(current)
            continue
        if current and line.lstrip().startswith("- "):
            alias = line.lstrip()[2:].strip()
            if alias:
                groups[current].add(alias)

    normalized = {normalize_token(term) for terms in groups.values() for term in terms if term}
    return groups, normalized


def collect_case_text(result: dict[str, Any], case: dict[str, Any] | None) -> dict[str, str]:
    titles: list[str] = []
    routes: list[str] = []
    matched_queries: list[str] = []
    anchor_terms: list[str] = []
    for field_name in ("final_documents", "documents_before_threshold"):
        for doc in result.get(field_name) or []:
            title = str(doc.get("title") or "")
            source_id = str(doc.get("source_id") or "")
            titles.extend([title, source_id])
            route_value = doc.get("retrieval_routes") or doc.get("retrieval_route") or []
            if isinstance(route_value, list):
                routes.extend(str(item) for item in route_value)
            else:
                routes.append(str(route_value))
            matched = doc.get("matched_by_bm25_query")
            if matched:
                matched_queries.append(str(matched))
            for anchor_key in (
                "anchor_terms",
                "matched_anchor_terms",
                "missing_anchor_terms",
                "hard_anchor_terms",
                "soft_anchor_terms",
                "negative_anchor_terms",
            ):
                values = doc.get(anchor_key) or []
                if isinstance(values, list):
                    anchor_terms.extend(str(item) for item in values)

    expected = []
    if case:
        expected.extend(str(item) for item in case.get("expected_keywords") or [])
        expected.extend(str(item) for item in case.get("expected_title_contains") or [])

    return {
        "question": " ".join(
            [
                str(result.get("original_question") or ""),
                str(result.get("normalized_question") or ""),
                " ".join(str(item) for item in result.get("query_variants") or []),
            ]
        ),
        "documents": " ".join(titles + anchor_terms),
        "expected": " ".join(expected),
        "routes": " ".join(routes),
        "matched_queries": " ".join(matched_queries),
    }


def is_problem_case(result: dict[str, Any], baseline: dict[str, Any] | None) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    if result.get("expected_answerability") == "answerable" and (
        result.get("rejected_by_low_confidence") or result.get("rejected_by_anchor_evidence")
    ):
        reasons.append("FALSE_REJECTION")
    if result.get("expected_answerability") == "answerable" and not result.get("top2_title_weak_hit"):
        reasons.append("TOP2_TITLE_MISS")
    if (result.get("ab_comparison") or {}).get("classification") in {"negative", "changed"}:
        reasons.append("AB_CHANGED_OR_NEGATIVE")
    if baseline:
        baseline_hit = bool(baseline.get("top2_title_weak_hit"))
        current_hit = bool(result.get("top2_title_weak_hit"))
        if baseline_hit and not current_hit:
            reasons.append("RERANKER_REGRESSION")
        if baseline.get("expected_answerability") == "answerable" and baseline.get("final_topk_count", 0) > result.get(
            "final_topk_count", 0
        ):
            reasons.append("CANDIDATE_LOST_AFTER_RERANKER")
    return bool(reasons), reasons


def score_candidate(candidate: Candidate, existing_terms: set[str]) -> None:
    aliases = [alias for alias in candidate.aliases if normalize_token(alias) not in existing_terms]
    case_count = len(candidate.evidence_cases)
    source_count = len({item.source for item in candidate.evidence})
    cross_language = any(re.search(r"[A-Za-z]", alias) for alias in aliases + [candidate.canonical]) and any(
        re.search(r"[\u4e00-\u9fff]", alias) for alias in aliases + [candidate.canonical]
    )
    generic_hit = any(normalize_token(alias) in {normalize_token(item) for item in GENERIC_TERMS} for alias in aliases)

    score = 0.35
    score += min(case_count, 4) * 0.08
    score += min(source_count, 4) * 0.05
    if cross_language:
        score += 0.12
    if len(aliases) >= 2:
        score += 0.08
    if any(item.source in {"question_document_pair", "expected_document_pair"} for item in candidate.evidence):
        score += 0.12
    if generic_hit:
        score -= 0.25

    candidate.confidence_score = round(max(0.0, min(1.0, score)), 4)
    if candidate.status == "existing_alias":
        candidate.risk = "existing"
    elif generic_hit or candidate.confidence_score < 0.55:
        candidate.risk = "high"
    elif candidate.confidence_score < 0.75:
        candidate.risk = "medium"
    else:
        candidate.risk = "low"


def add_evidence(
    candidates: dict[str, Candidate],
    canonical: str,
    alias: str,
    evidence: Evidence,
    existing_terms: set[str],
) -> None:
    if normalize_token(alias) in {normalize_token(item) for item in GENERIC_TERMS}:
        return
    candidate = candidates.setdefault(canonical, Candidate(canonical=canonical))
    candidate.aliases.add(alias)
    candidate.evidence.append(evidence)
    if normalize_token(alias) in existing_terms or normalize_token(canonical) in existing_terms:
        candidate.status = "existing_alias"


def mine_candidates(
    alias_file: Path = DEFAULT_ALIAS_FILE,
    cases_file: Path = DEFAULT_CASES_FILE,
    reranker_report_file: Path = DEFAULT_RERANKER_REPORT,
    bm25_report_file: Path = DEFAULT_BM25_REPORT,
    threshold_analysis_file: Path = DEFAULT_THRESHOLD_ANALYSIS,
) -> dict[str, Any]:
    _, existing_terms = load_existing_aliases(alias_file)
    cases = {str(item["id"]): item for item in load_json(cases_file)}
    reranker_results = {str(item["case_id"]): item for item in load_json(reranker_report_file).get("results", [])}
    bm25_results = {str(item["case_id"]): item for item in load_json(bm25_report_file).get("results", [])}
    threshold_analysis = load_json(threshold_analysis_file) if threshold_analysis_file.exists() else {}

    candidates: dict[str, Candidate] = {}
    problem_reason_counter: Counter[str] = Counter()

    for case_id, result in reranker_results.items():
        baseline = bm25_results.get(case_id)
        problem, reasons = is_problem_case(result, baseline)
        problem_reason_counter.update(reasons)
        case = cases.get(case_id)
        text_parts = collect_case_text(result, case)

        for canonical, terms in KNOWN_ALIAS_GROUPS.items():
            question_terms = [term for term in terms if contains_term(text_parts["question"], term)]
            document_terms = [
                term
                for term in terms
                if contains_term(text_parts["documents"], term) or contains_term(text_parts["expected"], term)
            ]
            route_terms = [term for term in terms if contains_term(text_parts["matched_queries"], term)]

            if not (question_terms or document_terms or route_terms):
                continue

            source = "observed_non_problem_case"
            if problem:
                source = "question_document_pair" if question_terms and document_terms else "problem_case_observed"
            elif question_terms and document_terms:
                source = "expected_document_pair"

            observed_terms = sorted(set(question_terms + document_terms + route_terms), key=lambda item: (-len(item), item))
            for alias in observed_terms:
                add_evidence(
                    candidates,
                    canonical,
                    alias,
                    Evidence(
                        case_id=case_id,
                        question_term=question_terms[0] if question_terms else None,
                        document_term=document_terms[0] if document_terms else None,
                        source=source,
                        reason=";".join(reasons) if reasons else "OBSERVED_ALIAS_VARIANT",
                    ),
                    existing_terms,
                )

    # Add existing aliases that are visible in the report, so reviewers can see
    # that they were detected but intentionally not duplicated as new advice.
    for canonical, terms in KNOWN_ALIAS_GROUPS.items():
        if normalize_token(canonical) in existing_terms:
            candidate = candidates.setdefault(canonical, Candidate(canonical=canonical, status="existing_alias"))
            for term in terms:
                if normalize_token(term) in existing_terms:
                    candidate.aliases.add(term)
            if not candidate.evidence:
                candidate.evidence.append(
                    Evidence(
                        case_id="existing_config",
                        question_term=None,
                        document_term=None,
                        source="query_aliases.yaml",
                        reason="ALREADY_CONFIGURED",
                    )
                )

    for candidate in candidates.values():
        score_candidate(candidate, existing_terms)

    serialized = sorted(
        (serialize_candidate(item, existing_terms) for item in candidates.values()),
        key=lambda item: (
            item["status"] != "new_suggestion",
            {"low": 0, "medium": 1, "high": 2, "existing": 3}.get(item["risk"], 4),
            -item["confidence_score"],
            item["canonical"],
        ),
    )

    status_counts = Counter(item["status"] for item in serialized)
    confidence_counts = Counter(item["confidence_band"] for item in serialized)
    risk_counts = Counter(item["risk"] for item in serialized)

    return {
        "schema_version": "alias-candidate-mining-v1",
        "inputs": {
            "alias_file": str(alias_file),
            "cases_file": str(cases_file),
            "reranker_report_file": str(reranker_report_file),
            "bm25_report_file": str(bm25_report_file),
            "threshold_analysis_file": str(threshold_analysis_file),
        },
        "summary": {
            "total_candidates": len(serialized),
            "new_suggestion_count": status_counts.get("new_suggestion", 0),
            "existing_alias_count": status_counts.get("existing_alias", 0),
            "high_confidence_count": confidence_counts.get("high", 0),
            "medium_confidence_count": confidence_counts.get("medium", 0),
            "low_confidence_count": confidence_counts.get("low", 0),
            "risk_counts": dict(sorted(risk_counts.items())),
            "problem_reason_counts": dict(sorted(problem_reason_counter.items())),
            "threshold_recommendation": threshold_analysis.get("recommendation", {}),
        },
        "suggestions": serialized,
        "notes": [
            "This is offline analysis only.",
            "query_aliases.yaml is read but not modified.",
            "Existing aliases are marked as existing_alias and are not duplicated as new suggestions.",
            "Generic terms are filtered from standalone suggestions.",
        ],
    }


def confidence_band(score: float) -> str:
    if score >= 0.75:
        return "high"
    if score >= 0.55:
        return "medium"
    return "low"


def serialize_candidate(candidate: Candidate, existing_terms: set[str]) -> dict[str, Any]:
    aliases = sorted(candidate.aliases, key=lambda item: (-len(item), item.casefold()))
    new_aliases = [alias for alias in aliases if normalize_token(alias) not in existing_terms]
    return {
        "canonical": candidate.canonical,
        "aliases": aliases,
        "new_aliases": new_aliases,
        "confidence_score": candidate.confidence_score,
        "confidence_band": confidence_band(candidate.confidence_score),
        "status": candidate.status,
        "risk": candidate.risk,
        "evidence_cases": candidate.evidence_cases,
        "evidence": [
            {
                "case_id": item.case_id,
                "question_term": item.question_term,
                "document_term": item.document_term,
                "source": item.source,
                "reason": item.reason,
            }
            for item in candidate.evidence[:20]
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Alias Candidate Suggestions",
        "",
        "This report was generated from existing offline RAG evaluation reports only.",
        "",
        "## Summary",
        "",
        f"- Total candidates: {summary['total_candidates']}",
        f"- New suggestions: {summary['new_suggestion_count']}",
        f"- Existing aliases detected: {summary['existing_alias_count']}",
        f"- High confidence: {summary['high_confidence_count']}",
        f"- Medium confidence: {summary['medium_confidence_count']}",
        f"- Low confidence: {summary['low_confidence_count']}",
        "",
        "## Top New Suggestions",
        "",
        "| Rank | Canonical | New Aliases | Score | Risk | Evidence Cases |",
        "| --- | --- | --- | ---: | --- | --- |",
    ]
    new_items = [item for item in report["suggestions"] if item["status"] == "new_suggestion"]
    for idx, item in enumerate(new_items[:20], 1):
        lines.append(
            f"| {idx} | {item['canonical']} | {', '.join(item['new_aliases']) or '-'} | "
            f"{item['confidence_score']:.4f} | {item['risk']} | {', '.join(item['evidence_cases'][:8])} |"
        )

    lines.extend(["", "## Risky Candidates Not Recommended Directly", ""])
    risky = [item for item in new_items if item["risk"] == "high"]
    if not risky:
        lines.append("- None")
    else:
        for item in risky[:20]:
            lines.append(
                f"- {item['canonical']}: {', '.join(item['new_aliases']) or '-'} "
                f"(score={item['confidence_score']:.4f}, cases={', '.join(item['evidence_cases'][:6])})"
            )

    lines.extend(["", "## Existing Aliases Detected", ""])
    existing = [item for item in report["suggestions"] if item["status"] == "existing_alias"]
    if not existing:
        lines.append("- None")
    else:
        for item in existing:
            lines.append(f"- {item['canonical']}: {', '.join(item['aliases'])}")

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- This script does not modify `query_aliases.yaml`.",
            "- This script does not call network, Embedding, Reranker, Chroma, LLM, or MCP services.",
            "- Candidates require manual review before a formal alias config update.",
            "",
        ]
    )
    return "\n".join(lines)


def write_outputs(report: dict[str, Any], output_json: Path, output_md: Path) -> None:
    output_json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    output_md.write_text(render_markdown(report), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Mine alias candidates from offline RAG reports.")
    parser.add_argument("--alias-file", type=Path, default=DEFAULT_ALIAS_FILE)
    parser.add_argument("--cases-file", type=Path, default=DEFAULT_CASES_FILE)
    parser.add_argument("--reranker-report-file", type=Path, default=DEFAULT_RERANKER_REPORT)
    parser.add_argument("--bm25-report-file", type=Path, default=DEFAULT_BM25_REPORT)
    parser.add_argument("--threshold-analysis-file", type=Path, default=DEFAULT_THRESHOLD_ANALYSIS)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    args = parser.parse_args()

    report = mine_candidates(
        alias_file=args.alias_file,
        cases_file=args.cases_file,
        reranker_report_file=args.reranker_report_file,
        bm25_report_file=args.bm25_report_file,
        threshold_analysis_file=args.threshold_analysis_file,
    )
    write_outputs(report, args.output_json, args.output_md)

    summary = report["summary"]
    print("Alias candidate mining complete")
    print(f"total_candidates={summary['total_candidates']}")
    print(f"new_suggestions={summary['new_suggestion_count']}")
    print(f"existing_aliases={summary['existing_alias_count']}")
    print(f"output_json={args.output_json}")
    print(f"output_md={args.output_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

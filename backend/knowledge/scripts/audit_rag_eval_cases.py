from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
KNOWLEDGE_ROOT = SCRIPT_PATH.parents[1]
REPO_ROOT = KNOWLEDGE_ROOT.parents[1]
if str(KNOWLEDGE_ROOT) not in sys.path:
    sys.path.insert(0, str(KNOWLEDGE_ROOT))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from services.anchor_evidence_service import extract_strong_anchors


TESTDATA = KNOWLEDGE_ROOT / "testdata"
DEFAULT_CASES = TESTDATA / "rag_eval_cases_v2.json"
DEFAULT_CRAWL_DIR = KNOWLEDGE_ROOT / "data" / "crawl"
GROUP_REQUIREMENTS = {
    "A_anchor_answerable": 20,
    "B_anchor_unanswerable": 15,
    "C_generic_answerable": 20,
    "D_generic_unanswerable": 8,
    "E_confusing": 8,
}
NEW_CATEGORIES = {
    "anchor_answerable",
    "anchor_unanswerable",
    "generic_answerable",
    "generic_unanswerable",
    "confusing",
}


def load_json(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def normalize_question(question: str) -> str:
    return re.sub(r"\s+", "", (question or "").strip().lower())


def load_markdown_index(crawl_dir: Path) -> dict[str, dict[str, str]]:
    index: dict[str, dict[str, str]] = {}
    for path in sorted(crawl_dir.rglob("*.md")):
        source_id = path.relative_to(crawl_dir).as_posix()
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            content = ""
        title = path.stem
        if "-" in title:
            title = title.split("-", 1)[1]
        index[source_id] = {
            "source_id": source_id,
            "title": title,
            "content": content,
            "search_text": f"{title}\n{content}",
        }
    return index


def derive_group(case: dict[str, Any]) -> str:
    category = case.get("category") or ""
    if category == "anchor_answerable":
        return "A_anchor_answerable"
    if category == "anchor_unanswerable":
        return "B_anchor_unanswerable"
    if category == "generic_answerable":
        return "C_generic_answerable"
    if category == "generic_unanswerable":
        return "D_generic_unanswerable"
    if category == "confusing":
        return "E_confusing"

    expected_no_answer = bool(case.get("expected_no_answer"))
    anchors = extract_strong_anchors(case.get("question", ""))
    if expected_no_answer and anchors:
        return "B_anchor_unanswerable"
    if expected_no_answer:
        return "D_generic_unanswerable"
    if "容易混淆" in category:
        return "E_confusing"
    if anchors:
        return "A_anchor_answerable"
    return "C_generic_answerable"


def expected_answerability(case: dict[str, Any]) -> str:
    if case.get("expected_answerability") in {"answerable", "unanswerable"}:
        return case["expected_answerability"]
    return "unanswerable" if case.get("expected_no_answer") else "answerable"


def audit_case(
    case: dict[str, Any],
    markdown_index: dict[str, dict[str, str]],
    question_counts: Counter,
    source_counts: Counter,
) -> dict[str, Any]:
    case_id = case.get("id")
    question = case.get("question") or ""
    answerability = expected_answerability(case)
    group = derive_group(case)
    expected_source_ids = case.get("expected_source_ids") or []
    expected_title_contains = case.get("expected_title_contains") or []
    expected_anchor_terms = case.get("expected_anchor_terms") or [anchor.term for anchor in extract_strong_anchors(question)]
    notes: list[str] = []
    status = "VALID"

    empty_fields = []
    for field in ("id", "question", "category"):
        if not case.get(field):
            empty_fields.append(field)
    if case.get("category") in NEW_CATEGORIES:
        for field in ("expected_answerability", "gold_evidence_note", "review_status"):
            if not case.get(field):
                empty_fields.append(field)

    source_id_found = [source_id for source_id in expected_source_ids if source_id in markdown_index]
    source_id_missing = [source_id for source_id in expected_source_ids if source_id not in markdown_index]
    title_hits = []
    for term in expected_title_contains:
        if not term:
            continue
        for source_id, record in markdown_index.items():
            if term in record["search_text"]:
                title_hits.append({"term": term, "source_id": source_id, "title": record["title"]})
                break

    duplicate_question = question_counts[normalize_question(question)] > 1
    duplicate_source_ids = [source_id for source_id in expected_source_ids if source_counts[source_id] > 1]
    category_valid = (case.get("category") in NEW_CATEGORIES) or not case.get("expected_answerability")

    if empty_fields:
        status = "INVALID"
        notes.append(f"missing_fields={empty_fields}")
    if not category_valid:
        status = "INVALID"
        notes.append("invalid_category_for_v2_schema")
    if answerability == "answerable" and not source_id_found and not title_hits:
        status = "INVALID"
        notes.append("answerable case lacks verifiable expected_source_ids or expected_title_contains")
    if answerability == "unanswerable" and expected_source_ids:
        status = "INVALID"
        notes.append("unanswerable case must not contain expected_source_ids")
    if source_id_missing:
        status = "INVALID"
        notes.append(f"missing_source_ids={source_id_missing}")
    if duplicate_question:
        status = "DUPLICATE"
        notes.append("duplicate_question")
    if duplicate_source_ids:
        notes.append(f"duplicate_source_ids={duplicate_source_ids}")

    obvious_unanswerable_hits = []
    if answerability == "unanswerable":
        for term in expected_anchor_terms:
            if not term:
                continue
            for source_id, record in markdown_index.items():
                if term in record["search_text"]:
                    obvious_unanswerable_hits.append({"term": term, "source_id": source_id, "title": record["title"]})
                    break
        if obvious_unanswerable_hits:
            status = "NEEDS_MANUAL_REVIEW" if status == "VALID" else status
            notes.append("unanswerable anchor term appears in local markdown")

    return {
        "case_id": case_id,
        "question": question,
        "category": case.get("category"),
        "group": group,
        "expected_answerability": answerability,
        "expected_title_contains": expected_title_contains,
        "expected_source_ids": expected_source_ids,
        "expected_anchor_terms": expected_anchor_terms,
        "source_id_found": source_id_found,
        "source_id_missing": source_id_missing,
        "title_contains_found": title_hits,
        "duplicate_question": duplicate_question,
        "duplicate_source_ids": duplicate_source_ids,
        "empty_fields": empty_fields,
        "obvious_unanswerable_hits": obvious_unanswerable_hits,
        "audit_status": status,
        "audit_notes": notes,
    }


def build_audit(cases_file: Path, crawl_dir: Path) -> dict[str, Any]:
    cases = load_json(cases_file)
    markdown_index = load_markdown_index(crawl_dir)
    question_counts = Counter(normalize_question(case.get("question", "")) for case in cases)
    source_counts = Counter(
        source_id
        for case in cases
        for source_id in (case.get("expected_source_ids") or [])
    )
    records = [audit_case(case, markdown_index, question_counts, source_counts) for case in cases]
    group_counts = Counter(record["group"] for record in records)
    status_counts = Counter(record["audit_status"] for record in records)
    invalid_records = [record for record in records if record["audit_status"] == "INVALID"]
    duplicate_records = [record for record in records if record["audit_status"] == "DUPLICATE"]
    manual_records = [record for record in records if record["audit_status"] == "NEEDS_MANUAL_REVIEW"]
    requirement_violations = {
        group: {"required": required, "actual": group_counts.get(group, 0)}
        for group, required in GROUP_REQUIREMENTS.items()
        if group_counts.get(group, 0) < required
    }
    answerable = [record for record in records if record["expected_answerability"] == "answerable"]
    answerable_covered = [
        record
        for record in answerable
        if record["source_id_found"] or record["title_contains_found"]
    ]
    return {
        "status": "passed" if not invalid_records and not duplicate_records and not requirement_violations else "failed",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "cases_file": str(cases_file),
        "crawl_dir": str(crawl_dir),
        "summary": {
            "total_cases": len(cases),
            "valid_cases": status_counts.get("VALID", 0),
            "invalid_cases": len(invalid_records),
            "duplicate_cases": len(duplicate_records),
            "needs_manual_review_cases": len(manual_records),
            "group_counts": dict(group_counts),
            "requirement_violations": requirement_violations,
            "answerable_cases": len(answerable),
            "answerable_evidence_covered": len(answerable_covered),
            "answerable_evidence_coverage_rate": round(len(answerable_covered) / len(answerable), 4) if answerable else 0.0,
        },
        "records": records,
        "notes": [
            "Audit is local-only and does not call Embedding, Chroma, LLM, network, or /query.",
            "expected_title_contains is weak evidence for offline audit, not ground-truth retrieval correctness.",
        ],
    }


def output_paths(cases_file: Path) -> tuple[Path, Path]:
    stem = cases_file.stem
    return TESTDATA / f"{stem}_audit.json", TESTDATA / f"{stem}_audit.md"


def write_reports(audit: dict[str, Any], json_path: Path, md_path: Path) -> None:
    json_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown(audit), encoding="utf-8")


def render_markdown(audit: dict[str, Any]) -> str:
    summary = audit["summary"]
    lines = [
        "# RAG Eval Cases Audit",
        "",
        f"- Status: `{audit['status']}`",
        f"- Generated at: `{audit['generated_at']}`",
        f"- Cases file: `{audit['cases_file']}`",
        "",
        "## Summary",
        "",
        f"- Total cases: {summary['total_cases']}",
        f"- Valid cases: {summary['valid_cases']}",
        f"- Invalid cases: {summary['invalid_cases']}",
        f"- Duplicate cases: {summary['duplicate_cases']}",
        f"- Needs manual review: {summary['needs_manual_review_cases']}",
        f"- Answerable evidence coverage: {summary['answerable_evidence_covered']}/{summary['answerable_cases']} ({summary['answerable_evidence_coverage_rate']})",
        "",
        "## Group Counts",
        "",
    ]
    for group, count in summary["group_counts"].items():
        lines.append(f"- {group}: {count}")
    if summary["requirement_violations"]:
        lines.extend(["", "## Requirement Violations", ""])
        for group, item in summary["requirement_violations"].items():
            lines.append(f"- {group}: required={item['required']} actual={item['actual']}")
    lines.extend(["", "## Non-Valid Records", ""])
    for record in audit["records"]:
        if record["audit_status"] != "VALID":
            lines.append(f"- {record['case_id']} `{record['audit_status']}` notes={record['audit_notes']}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit local RAG evaluation cases against Markdown evidence.")
    parser.add_argument("--cases-file", default=str(DEFAULT_CASES))
    parser.add_argument("--crawl-dir", default=str(DEFAULT_CRAWL_DIR))
    args = parser.parse_args()
    cases_file = Path(args.cases_file)
    crawl_dir = Path(args.crawl_dir)
    audit = build_audit(cases_file, crawl_dir)
    json_path, md_path = output_paths(cases_file)
    write_reports(audit, json_path, md_path)
    print("RAG eval case audit completed")
    print(f"status={audit['status']}")
    print(f"summary={audit['summary']}")
    print(f"json_report={json_path}")
    print(f"md_report={md_path}")
    return 0 if audit["status"] == "passed" else 2


if __name__ == "__main__":
    raise SystemExit(main())

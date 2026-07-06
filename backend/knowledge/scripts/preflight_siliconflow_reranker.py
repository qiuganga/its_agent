from __future__ import annotations

import json
import sys
import traceback
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

from config.settings import settings
from repositories.reranker_repository import SiliconFlowRerankerRepository


REPORT_PATH = KNOWLEDGE_ROOT / "testdata" / "rag_qwen_reranker_preflight.md"


def run_preflight() -> dict[str, Any]:
    query = "蓝屏 0x0000007B 怎么处理"
    documents = [
        "Windows 蓝屏错误 0x0000007B 的排查方法",
        "如何设置桌面壁纸",
    ]
    report: dict[str, Any] = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "provider": "SiliconFlow",
        "base_url": settings.RAG_RERANKER_BASE_URL,
        "endpoint": "POST /rerank",
        "api_key_configured": bool(settings.SILICONFLOW_API_KEY),
        "model_configured": bool(settings.RAG_RERANKER_MODEL),
        "model": settings.RAG_RERANKER_MODEL,
        "http_status": None,
        "schema_valid": False,
        "ranking_valid": False,
        "passed": False,
        "error_type": None,
        "error_message": None,
        "results": [],
    }
    if not settings.SILICONFLOW_API_KEY:
        report["error_type"] = "missing_api_key"
        report["error_message"] = "SILICONFLOW_API_KEY is not configured"
        return report
    if not settings.RAG_RERANKER_MODEL:
        report["error_type"] = "missing_model"
        report["error_message"] = "RAG_RERANKER_MODEL is not configured"
        return report

    repository = SiliconFlowRerankerRepository()
    try:
        results = repository.rerank(query, documents, top_n=2)
        stats = repository.last_call_stats
        report["http_status"] = stats.http_status if stats else 200
        report["schema_valid"] = bool(results)
        report["results"] = [
            {
                "index": result.candidate_index,
                "relevance_score": result.reranker_score,
                "rank": result.rank,
                "document_label": "blue_screen" if result.candidate_index == 0 else "wallpaper",
            }
            for result in results
        ]
        score_by_index = {result.candidate_index: result.reranker_score for result in results}
        report["ranking_valid"] = score_by_index.get(0, -1.0) > score_by_index.get(1, -1.0)
        report["passed"] = bool(report["http_status"] == 200 and report["schema_valid"] and report["ranking_valid"])
        return report
    except Exception as exc:
        report["error_type"] = exc.__class__.__name__
        report["error_message"] = str(exc)
        report["traceback_tail"] = traceback.format_exc().splitlines()[-5:]
        return report


def write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# Qwen Reranker Preflight",
        "",
        f"- Generated at: `{report.get('generated_at')}`",
        f"- Provider: `{report.get('provider')}`",
        f"- Base URL: `{report.get('base_url')}`",
        f"- Endpoint: `{report.get('endpoint')}`",
        f"- SILICONFLOW_API_KEY configured: `{report.get('api_key_configured')}`",
        f"- RAG_RERANKER_MODEL configured: `{report.get('model_configured')}`",
        f"- Model: `{report.get('model')}`",
        f"- HTTP status: `{report.get('http_status')}`",
        f"- Schema valid: `{report.get('schema_valid')}`",
        f"- Ranking valid: `{report.get('ranking_valid')}`",
        f"- Passed: `{report.get('passed')}`",
        "",
        "## Probe",
        "",
        "- Query: `蓝屏 0x0000007B 怎么处理`",
        "- Documents: `blue_screen`, `wallpaper`",
        "",
        "## Results",
        "",
        "```json",
        json.dumps(report.get("results") or [], ensure_ascii=False, indent=2),
        "```",
        "",
    ]
    if not report.get("passed"):
        lines.extend([
            "## Failure",
            "",
            f"- Error type: `{report.get('error_type')}`",
            f"- Error message: `{report.get('error_message')}`",
            "",
            "No fallback rerank was used. Do not run the 82-case experiment until this preflight passes.",
        ])
    else:
        lines.extend([
            "## Decision",
            "",
            "Preflight passed. The 82-case reranker experiment can run.",
        ])
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = run_preflight()
    write_markdown(report)
    print(f"passed={report.get('passed')}")
    print(f"http_status={report.get('http_status')}")
    print(f"schema_valid={report.get('schema_valid')}")
    print(f"ranking_valid={report.get('ranking_valid')}")
    print(f"report={REPORT_PATH}")
    return 0 if report.get("passed") else 2


if __name__ == "__main__":
    raise SystemExit(main())

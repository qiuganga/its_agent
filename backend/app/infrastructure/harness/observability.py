import json
from typing import Any

from app.infrastructure.logging.logger import logger


SENSITIVE_KEYS = {
    "authorization",
    "api_key",
    "apikey",
    "ak",
    "password",
    "token",
    "secret",
}

MCP_OBSERVABILITY_KEYS = {
    "provider",
    "mcp_tool_name",
    "schema_version",
    "mcp_ok",
    "error_code",
    "retryable",
    "latency_ms",
    "result_item_count",
}


def scrub_metadata(data: dict[str, Any]) -> dict[str, Any]:
    scrubbed: dict[str, Any] = {}
    for key, value in data.items():
        lower_key = key.lower()
        if any(sensitive in lower_key for sensitive in SENSITIVE_KEYS):
            scrubbed[key] = "***"
        else:
            scrubbed[key] = value
    return scrubbed


def log_harness_event(**fields: Any) -> None:
    safe_fields = scrub_metadata(fields)
    try:
        logger.info("[Harness] %s", json.dumps(safe_fields, ensure_ascii=False, default=str))
    except Exception:
        logger.info("[Harness] %s", safe_fields)


def log_mcp_contract_event(**fields: Any) -> None:
    safe_fields = scrub_metadata(fields)
    try:
        logger.info("[MCPContract] %s", json.dumps(safe_fields, ensure_ascii=False, default=str))
    except Exception:
        logger.info("[MCPContract] %s", safe_fields)

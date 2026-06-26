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

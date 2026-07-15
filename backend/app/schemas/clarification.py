from typing import Literal

from pydantic import BaseModel, Field


ClarificationType = Literal[
    "missing_location",
    "missing_destination",
    "missing_device_info",
    "missing_error_detail",
    "ambiguous_intent",
    "insufficient_evidence",
    "tool_unavailable",
    "unknown",
]


class ClarificationResult(BaseModel):
    ok: bool = False
    need_clarification: bool = True
    clarification_type: ClarificationType = "unknown"
    missing_fields: list[str] = Field(default_factory=list)
    clarification_question: str
    source: str = "agent"
    original_query: str | None = None
    suggested_examples: list[str] = Field(default_factory=list)


def is_clarification_payload(payload: object) -> bool:
    if not isinstance(payload, dict):
        return False
    return payload.get("need_clarification") is True and isinstance(
        payload.get("clarification_question"), str
    )


def make_clarification_result(
    *,
    clarification_type: ClarificationType,
    missing_fields: list[str],
    clarification_question: str,
    source: str,
    original_query: str | None = None,
    suggested_examples: list[str] | None = None,
) -> dict:
    return ClarificationResult(
        clarification_type=clarification_type,
        missing_fields=missing_fields,
        clarification_question=clarification_question,
        source=source,
        original_query=original_query,
        suggested_examples=suggested_examples or [],
    ).model_dump(mode="json")

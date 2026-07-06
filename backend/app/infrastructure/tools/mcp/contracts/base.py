from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, Field, model_validator


T = TypeVar("T")


class McpError(BaseModel):
    code: str
    message: str
    retryable: bool = False
    provider_code: str | None = None


class McpMeta(BaseModel):
    provider: str
    tool_name: str
    schema_version: str = "v1"
    latency_ms: int | None = None


class McpResult(BaseModel, Generic[T]):
    ok: bool
    data: T | None = None
    error: McpError | None = None
    meta: McpMeta

    @model_validator(mode="after")
    def validate_result_shape(self) -> "McpResult[T]":
        if self.ok:
            if self.error is not None:
                raise ValueError("ok=True result must not include error")
            if self.data is None:
                raise ValueError("ok=True result must include data")
        else:
            if self.data is not None:
                raise ValueError("ok=False result must not include data")
            if self.error is None:
                raise ValueError("ok=False result must include error")
        return self


def is_mcp_result_instance(value: object) -> bool:
    return isinstance(value, McpResult)


def is_mcp_result_payload(value: object) -> bool:
    if not isinstance(value, dict):
        return False
    meta = value.get("meta")
    return (
        isinstance(meta, dict)
        and meta.get("schema_version") == "v1"
        and isinstance(meta.get("provider"), str)
        and isinstance(meta.get("tool_name"), str)
        and isinstance(value.get("ok"), bool)
    )


def mcp_result_to_agent_payload(result: McpResult[object]) -> dict[str, object]:
    return result.model_dump(mode="json")


def result_item_count(result: McpResult[object]) -> int | None:
    if not result.ok or result.data is None:
        return None
    data = result.data
    items = getattr(data, "items", None)
    if isinstance(items, list):
        return len(items)
    return None

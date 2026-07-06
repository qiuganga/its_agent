from __future__ import annotations

import asyncio
import json
import time
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError

from app.infrastructure.tools.mcp.contracts.base import McpError, McpMeta, McpResult
from app.infrastructure.tools.mcp.contracts.tools import (
    GeocodeDestinationData,
    GeocodeDestinationInput,
    LocationData,
    MapNavigationData,
    MapNavigationInput,
    QueryNearestRepairShopsInput,
    ResolveUserLocationInput,
    SearchWebData,
    SearchWebInput,
    SearchWebItem,
)


T = TypeVar("T", bound=BaseModel)

MCP_RESPONSE_JSON_INVALID = "MCP_RESPONSE_JSON_INVALID"
MCP_RESPONSE_SCHEMA_INVALID = "MCP_RESPONSE_SCHEMA_INVALID"
MCP_TIMEOUT = "MCP_TIMEOUT"
MCP_NETWORK_ERROR = "MCP_NETWORK_ERROR"
MCP_PROVIDER_AUTH_ERROR = "MCP_PROVIDER_AUTH_ERROR"
MCP_PROVIDER_ERROR = "MCP_PROVIDER_ERROR"
MCP_INPUT_VALIDATION_ERROR = "MCP_INPUT_VALIDATION_ERROR"


INPUT_MODELS: dict[str, type[BaseModel]] = {
    "search_web": SearchWebInput,
    "geocode_destination": GeocodeDestinationInput,
    "resolve_user_location_from_text": ResolveUserLocationInput,
    "map_navigation_tool": MapNavigationInput,
    "query_nearest_repair_shops_by_coords": QueryNearestRepairShopsInput,
}


def make_success_result(
    *,
    provider: str,
    tool_name: str,
    data: BaseModel,
    latency_ms: int | None = None,
) -> McpResult[BaseModel]:
    return McpResult(
        ok=True,
        data=data,
        error=None,
        meta=McpMeta(provider=provider, tool_name=tool_name, latency_ms=latency_ms),
    )


def make_error_result(
    *,
    provider: str,
    tool_name: str,
    code: str,
    message: str,
    retryable: bool = False,
    provider_code: str | None = None,
    latency_ms: int | None = None,
) -> McpResult[BaseModel]:
    return McpResult(
        ok=False,
        data=None,
        error=McpError(
            code=code,
            message=message,
            retryable=retryable,
            provider_code=provider_code,
        ),
        meta=McpMeta(provider=provider, tool_name=tool_name, latency_ms=latency_ms),
    )


def validate_input(tool_name: str, arguments: dict[str, Any]) -> BaseModel | McpResult[BaseModel]:
    model = INPUT_MODELS.get(tool_name)
    if model is None:
        return make_error_result(
            provider="unknown",
            tool_name=tool_name,
            code=MCP_INPUT_VALIDATION_ERROR,
            message=f"Unsupported MCP tool contract: {tool_name}",
        )
    try:
        return model.model_validate(arguments)
    except ValidationError as exc:
        return make_error_result(
            provider="unknown",
            tool_name=tool_name,
            code=MCP_INPUT_VALIDATION_ERROR,
            message=_short_message(str(exc)),
        )


async def call_mcp_with_contract(
    *,
    provider: str,
    tool_name: str,
    arguments: dict[str, Any],
    action: Callable[[dict[str, Any]], Awaitable[Any]],
) -> McpResult[BaseModel]:
    validated = validate_input(tool_name, arguments)
    if isinstance(validated, McpResult):
        validated.meta.provider = provider
        return validated

    started_at = time.monotonic()
    try:
        raw_result = await action(validated.model_dump(mode="json", exclude_none=True))
    except Exception as exc:
        latency_ms = int((time.monotonic() - started_at) * 1000)
        return adapt_exception(provider=provider, tool_name=tool_name, exc=exc, latency_ms=latency_ms)

    latency_ms = int((time.monotonic() - started_at) * 1000)
    return adapt_provider_response(
        provider=provider,
        tool_name=tool_name,
        raw_result=raw_result,
        latency_ms=latency_ms,
    )


def adapt_exception(
    *,
    provider: str,
    tool_name: str,
    exc: BaseException,
    latency_ms: int | None = None,
) -> McpResult[BaseModel]:
    if isinstance(exc, asyncio.TimeoutError):
        return make_error_result(
            provider=provider,
            tool_name=tool_name,
            code=MCP_TIMEOUT,
            message="MCP provider call timed out.",
            retryable=True,
            latency_ms=latency_ms,
        )

    text = str(exc)
    lowered = text.lower()
    if any(marker in lowered for marker in ("unauthorized", "forbidden", "401", "403", "api key", "token", "auth")):
        return make_error_result(
            provider=provider,
            tool_name=tool_name,
            code=MCP_PROVIDER_AUTH_ERROR,
            message="MCP provider authentication failed.",
            retryable=False,
            latency_ms=latency_ms,
        )

    if isinstance(exc, (ConnectionError, OSError, TimeoutError)):
        return make_error_result(
            provider=provider,
            tool_name=tool_name,
            code=MCP_NETWORK_ERROR,
            message="MCP provider network error.",
            retryable=True,
            latency_ms=latency_ms,
        )

    return make_error_result(
        provider=provider,
        tool_name=tool_name,
        code=MCP_PROVIDER_ERROR,
        message=_short_message(text or exc.__class__.__name__),
        retryable=False,
        latency_ms=latency_ms,
    )


def adapt_provider_response(
    *,
    provider: str,
    tool_name: str,
    raw_result: Any,
    latency_ms: int | None = None,
) -> McpResult[BaseModel]:
    payload_or_error = _coerce_payload(provider, tool_name, raw_result, latency_ms)
    if isinstance(payload_or_error, McpResult):
        return payload_or_error
    payload = payload_or_error

    provider_error = _provider_error(provider, tool_name, payload, latency_ms)
    if provider_error is not None:
        return provider_error

    try:
        data = _parse_data(tool_name, payload)
    except ValidationError as exc:
        return make_error_result(
            provider=provider,
            tool_name=tool_name,
            code=MCP_RESPONSE_SCHEMA_INVALID,
            message=_short_message(str(exc)),
            latency_ms=latency_ms,
        )
    except (TypeError, ValueError) as exc:
        return make_error_result(
            provider=provider,
            tool_name=tool_name,
            code=MCP_RESPONSE_SCHEMA_INVALID,
            message=_short_message(str(exc)),
            latency_ms=latency_ms,
        )

    return make_success_result(provider=provider, tool_name=tool_name, data=data, latency_ms=latency_ms)


def _coerce_payload(
    provider: str,
    tool_name: str,
    raw_result: Any,
    latency_ms: int | None,
) -> Any | McpResult[BaseModel]:
    raw_result = _extract_mcp_content_text(raw_result)
    if raw_result is None:
        return {}
    if isinstance(raw_result, (dict, list)):
        return raw_result
    if isinstance(raw_result, bytes):
        raw_result = raw_result.decode("utf-8", errors="replace")
    if isinstance(raw_result, str):
        text = raw_result.strip()
        if not text:
            return {}
        if text[0] in "[{":
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                return make_error_result(
                    provider=provider,
                    tool_name=tool_name,
                    code=MCP_RESPONSE_JSON_INVALID,
                    message="MCP provider returned invalid JSON.",
                    retryable=False,
                    latency_ms=latency_ms,
                )
        return {"text": text}
    return {"text": str(raw_result)}


def _extract_mcp_content_text(raw_result: Any) -> Any:
    content = getattr(raw_result, "content", None)
    if content is None:
        return raw_result
    texts: list[str] = []
    for item in content:
        text = getattr(item, "text", None)
        if text:
            texts.append(text)
    return "\n".join(texts)


def _provider_error(
    provider: str,
    tool_name: str,
    payload: Any,
    latency_ms: int | None,
) -> McpResult[BaseModel] | None:
    if not isinstance(payload, dict):
        return None

    status = payload.get("status")
    if status not in (None, 0, "0", "ok", "OK", "success", "SUCCESS", True):
        return make_error_result(
            provider=provider,
            tool_name=tool_name,
            code=MCP_PROVIDER_ERROR,
            message=_short_message(str(payload.get("message") or payload.get("msg") or "MCP provider returned an error.")),
            retryable=False,
            provider_code=str(status),
            latency_ms=latency_ms,
        )

    error = payload.get("error")
    if error:
        message = error.get("message") if isinstance(error, dict) else str(error)
        provider_code = error.get("code") if isinstance(error, dict) else payload.get("code")
        lowered = str(message).lower()
        if any(marker in lowered for marker in ("unauthorized", "forbidden", "401", "403", "api key", "token", "auth")):
            return make_error_result(
                provider=provider,
                tool_name=tool_name,
                code=MCP_PROVIDER_AUTH_ERROR,
                message="MCP provider authentication failed.",
                retryable=False,
                provider_code=str(provider_code) if provider_code else None,
                latency_ms=latency_ms,
            )
        return make_error_result(
            provider=provider,
            tool_name=tool_name,
            code=MCP_PROVIDER_ERROR,
            message=_short_message(str(message)),
            retryable=False,
            provider_code=str(provider_code) if provider_code else None,
            latency_ms=latency_ms,
        )
    return None


def _parse_data(tool_name: str, payload: Any) -> BaseModel:
    if tool_name == "search_web":
        return _parse_search_web(payload)
    if tool_name in ("geocode_destination", "resolve_user_location_from_text"):
        return _parse_geocode_or_location(tool_name, payload)
    if tool_name == "map_navigation_tool":
        return _parse_navigation(payload)
    raise ValueError(f"No MCP response parser registered for {tool_name}")


def _parse_search_web(payload: Any) -> SearchWebData:
    if payload in ({}, [], None):
        return SearchWebData(items=[])
    if isinstance(payload, list):
        return SearchWebData(items=[_search_item(item) for item in payload])
    if not isinstance(payload, dict):
        raise TypeError("search_web payload must be object or array")
    if "text" in payload and len(payload) == 1:
        return SearchWebData(items=[], text=str(payload["text"]))
    candidates = payload.get("pages") or payload.get("items") or payload.get("results") or payload.get("data") or []
    if isinstance(candidates, dict):
        candidates = candidates.get("pages") or candidates.get("items") or candidates.get("results") or []
    if not isinstance(candidates, list):
        raise TypeError("search_web items must be a list")
    return SearchWebData(items=[_search_item(item) for item in candidates])


def _search_item(item: Any) -> SearchWebItem:
    if isinstance(item, str):
        return SearchWebItem(snippet=item)
    if not isinstance(item, dict):
        raise TypeError("search item must be object or string")
    return SearchWebItem(
        title=item.get("title") or item.get("name"),
        url=item.get("url") or item.get("link"),
        snippet=item.get("snippet") or item.get("summary") or item.get("content") or item.get("text"),
        source=item.get("hostname") or item.get("source"),
    )


def _parse_geocode_or_location(tool_name: str, payload: Any) -> BaseModel:
    if payload in ({}, [], None):
        return LocationData(source="empty") if tool_name == "resolve_user_location_from_text" else GeocodeDestinationData()
    if not isinstance(payload, dict):
        raise TypeError("geocode payload must be object")
    if "text" in payload and len(payload) == 1:
        return LocationData(source="text", address=str(payload["text"])) if tool_name == "resolve_user_location_from_text" else GeocodeDestinationData(address=str(payload["text"]))

    result = payload.get("result") if isinstance(payload.get("result"), dict) else payload
    content = payload.get("content") if isinstance(payload.get("content"), dict) else {}
    point = content.get("point") if isinstance(content.get("point"), dict) else None
    if point and tool_name == "resolve_user_location_from_text":
        x_str = point.get("x")
        y_str = point.get("y")
        if x_str is None or y_str is None:
            raise ValueError("missing ip location point coordinates")
        lng, lat = _bd09mc_to_bd09(float(x_str), float(y_str))
        return LocationData(lat=lat, lng=lng, source="ip")

    location = result.get("location") if isinstance(result.get("location"), dict) else result
    lat = location.get("lat")
    lng = location.get("lng")
    address = result.get("formatted_address") or result.get("address") or payload.get("address")
    if tool_name == "resolve_user_location_from_text":
        return LocationData(lat=lat, lng=lng, source=str(payload.get("source") or "geocode"), address=address)
    return GeocodeDestinationData(
        address=payload.get("address"),
        lat=lat,
        lng=lng,
        formatted_address=address,
    )


def _parse_navigation(payload: Any) -> MapNavigationData:
    if payload in ({}, [], None):
        return MapNavigationData()
    if isinstance(payload, str):
        return MapNavigationData(url=payload)
    if not isinstance(payload, dict):
        raise TypeError("navigation payload must be object or string")
    if "text" in payload and len(payload) == 1:
        return MapNavigationData(url=str(payload["text"]))
    url = payload.get("url") or payload.get("uri") or payload.get("link")
    return MapNavigationData(
        url=url,
        markdown_link=payload.get("markdown_link"),
        origin=payload.get("origin"),
        destination=payload.get("destination"),
        mode=payload.get("mode"),
    )


def _bd09mc_to_bd09(lng: float, lat: float) -> tuple[float, float]:
    import math

    if abs(lat) < 1e-6 or abs(lng) < 1e-6:
        return (0.0, 0.0)
    converted_lng = lng / 20037508.34 * 180
    converted_lat = lat / 20037508.34 * 180
    converted_lat = 180 / math.pi * (
        2 * math.atan(math.exp(converted_lat * math.pi / 180)) - math.pi / 2
    )
    return (converted_lng, converted_lat)


def _short_message(text: str, limit: int = 240) -> str:
    text = text.strip()
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."

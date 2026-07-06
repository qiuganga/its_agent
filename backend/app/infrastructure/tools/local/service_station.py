import json
import math
from urllib.parse import quote

import stun
from agents import RunContextWrapper, function_tool
from pymysql.cursors import DictCursor

from app.infrastructure.database.database_pool import pool
from app.infrastructure.harness.context import AgentRunContext
from app.infrastructure.logging.logger import logger
from app.infrastructure.tools.mcp.contracts import (
    LocationData,
    call_mcp_with_contract,
    make_error_result,
    make_success_result,
)
from app.infrastructure.tools.mcp.mcp_servers import baidu_mcp_client


RELATIVE_LOCATIONS = {
    "附近", "这", "这里", "这儿", "周围", "周边",
    "我的位置", "当前位置", "所在位置", "nearby", "here"
}


def bd09mc_to_bd09(lng: float, lat: float) -> tuple[float, float]:
    x = lng
    y = lat
    if abs(y) < 1e-6 or abs(x) < 1e-6:
        return (0.0, 0.0)

    lng = x / 20037508.34 * 180
    lat = y / 20037508.34 * 180
    lat = 180 / math.pi * (2 * math.atan(math.exp(lat * math.pi / 180)) - math.pi / 2)
    return (lng, lat)


def get_ip_via_stun():
    try:
        _nat_type, external_ip, _external_port = stun.get_ip_info()
        return external_ip
    except Exception as e:
        logger.warning("[Location] STUN lookup failed: %s", e)
        return None


async def resolve_user_location_from_text_impl(user_input: str):
    user_input = user_input.strip() if user_input else ""
    if user_input in RELATIVE_LOCATIONS:
        logger.info("[Location] Relative term detected; using IP/fallback location")
        user_input = ""

    if user_input:
        geocode_result = await call_mcp_with_contract(
            provider="baidu_map",
            tool_name="resolve_user_location_from_text",
            arguments={"user_input": user_input},
            action=lambda _args: baidu_mcp_client.call_tool("map_geocode", {"address": user_input}),
        )
        if (
            geocode_result.ok
            and geocode_result.data
            and geocode_result.data.lat is not None
            and geocode_result.data.lng is not None
        ):
            geocode_result.data.source = "geocode"
            return geocode_result
        logger.warning("[Location] Geocode failed or returned no coordinates")

    user_ip = get_ip_via_stun()
    if user_ip and user_ip not in ("127.0.0.1", "localhost", "::1"):
        ip_result = await call_mcp_with_contract(
            provider="baidu_map",
            tool_name="resolve_user_location_from_text",
            arguments={"user_input": user_ip},
            action=lambda _args: baidu_mcp_client.call_tool("map_ip_location", {"ip": user_ip}),
        )
        if ip_result.ok and ip_result.data and ip_result.data.lat is not None and ip_result.data.lng is not None:
            return ip_result
        logger.warning("[Location] IP location failed or returned no coordinates")

    return make_success_result(
        provider="local_fallback",
        tool_name="resolve_user_location_from_text",
        data=LocationData(lat=39.9042, lng=116.4074, source="fallback", fallback=True),
    )


@function_tool
async def resolve_user_location_from_text(
    ctx: RunContextWrapper[AgentRunContext],
    user_input: str,
) -> str:
    result = await ctx.context.system_harness.invoke(
        run_context=ctx.context,
        agent_key="service_agent",
        tool_name="resolve_user_location_from_text",
        arguments={"user_input": user_input},
        action=lambda: resolve_user_location_from_text_impl(user_input),
    )
    if isinstance(result, dict):
        return json.dumps(result, ensure_ascii=False)
    return result


def query_nearest_repair_shops_by_coords_impl(lat: float, lng: float, limit: int = 3) -> str:
    connection = None
    cursor = None
    try:
        connection = pool.connection()
        cursor = connection.cursor(DictCursor)
        sql = """
        SELECT
            id,
            service_station_name,
            province,
            city,
            district,
            address,
            phone,
            manager,
            manager_phone,
            opening_hours,
            repair_types,
            repair_specialties,
            repair_services,
            supported_brands,
            rating,
            established_year,
            employee_count,
            service_station_description,
            latitude,
            longitude,
            (
                6371 * acos(
                    cos(radians(%s)) *
                    cos(radians(latitude)) *
                    cos(radians(longitude) - radians(%s)) +
                    sin(radians(%s)) *
                    sin(radians(latitude))
                )
            ) AS distance_km
        FROM repair_shops
        WHERE
            latitude IS NOT NULL
            AND longitude IS NOT NULL
            AND ABS(latitude) <= 90
            AND ABS(longitude) <= 180
        ORDER BY distance_km ASC
        LIMIT %s
        """
        cursor.execute(sql, (lat, lng, lat, limit))
        rows = cursor.fetchall()
        return json.dumps({
            "ok": True,
            "count": len(rows),
            "data": rows,
            "query": {"lat": lat, "lng": lng, "limit": limit},
        }, ensure_ascii=False, default=str)
    except Exception as e:
        logger.error("[NearestShops] DB query failed: %s", e, exc_info=True)
        return json.dumps({
            "ok": False,
            "error": f"数据库查询失败: {str(e)}",
            "query": {"lat": lat, "lng": lng, "limit": limit},
        }, ensure_ascii=False)
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


@function_tool
async def query_nearest_repair_shops_by_coords(
    ctx: RunContextWrapper[AgentRunContext],
    lat: float,
    lng: float,
    limit: int = 3,
) -> str:
    result = await ctx.context.system_harness.invoke(
        run_context=ctx.context,
        agent_key="service_agent",
        tool_name="query_nearest_repair_shops_by_coords",
        arguments={"lat": lat, "lng": lng, "limit": limit},
        action=lambda: query_nearest_repair_shops_by_coords_impl(lat, lng, limit),
    )
    if isinstance(result, dict):
        return json.dumps(result, ensure_ascii=False)
    return result


async def geocode_destination_impl(address: str):
    return await call_mcp_with_contract(
        provider="baidu_map",
        tool_name="geocode_destination",
        arguments={"address": address},
        action=lambda args: baidu_mcp_client.call_tool("map_geocode", args),
    )


@function_tool
async def geocode_destination(
    ctx: RunContextWrapper[AgentRunContext],
    address: str,
) -> str:
    result = await ctx.context.system_harness.invoke(
        run_context=ctx.context,
        agent_key="service_agent",
        tool_name="geocode_destination",
        arguments={"address": address},
        action=lambda: geocode_destination_impl(address),
    )
    if isinstance(result, dict):
        return json.dumps(result, ensure_ascii=False)
    return result


def encode_baidu_url(url: str) -> str:
    return quote(url, safe=":/?&=%")


async def map_navigation_tool_impl(
    origin: str,
    destination: str,
    mode: str = "driving",
    region: str = "北京",
):
    if not origin or not destination:
        return make_error_result(
            provider="local_validation",
            tool_name="map_navigation_tool",
            code="MCP_INPUT_VALIDATION_ERROR",
            message="origin and destination must not be empty.",
        )

    result = await call_mcp_with_contract(
        provider="baidu_map",
        tool_name="map_navigation_tool",
        arguments={
            "origin": origin,
            "destination": destination,
            "mode": mode,
            "region": region,
        },
        action=lambda args: baidu_mcp_client.call_tool(
            "map_uri",
            {
                "service": "direction",
                **args,
            },
        ),
    )
    if result.ok and result.data and result.data.url:
        result.data.markdown_link = f"[点击开始导航]({result.data.url})"
        result.data.origin = origin
        result.data.destination = destination
        result.data.mode = mode
    return result


@function_tool
async def map_navigation_tool(
    ctx: RunContextWrapper[AgentRunContext],
    origin: str,
    destination: str,
    mode: str = "driving",
    region: str = "北京",
) -> str:
    result = await ctx.context.system_harness.invoke(
        run_context=ctx.context,
        agent_key="service_agent",
        tool_name="map_navigation_tool",
        arguments={
            "origin": origin,
            "destination": destination,
            "mode": mode,
            "region": region,
        },
        action=lambda: map_navigation_tool_impl(origin, destination, mode, region),
    )
    if isinstance(result, dict):
        return json.dumps(result, ensure_ascii=False)
    return result

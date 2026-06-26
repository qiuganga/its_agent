import json
import math
from urllib.parse import quote

import stun
from agents import RunContextWrapper, function_tool
from pymysql.cursors import DictCursor

from app.infrastructure.database.database_pool import pool
from app.infrastructure.harness.context import AgentRunContext
from app.infrastructure.logging.logger import logger
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


async def _baidu_tool_text(tool_name: str, arguments: dict) -> str:
    result = await baidu_mcp_client.call_tool(tool_name, arguments)
    texts = []
    for content in result.content:
        if hasattr(content, "text") and content.text:
            texts.append(content.text)
    return "\n".join(texts)


async def resolve_user_location_from_text_impl(user_input: str) -> str:
    user_input = user_input.strip() if user_input else ""
    if user_input in RELATIVE_LOCATIONS:
        logger.info("[Location] Relative term detected; using IP/fallback location")
        user_input = ""

    if user_input:
        try:
            text = await _baidu_tool_text("map_geocode", {"address": user_input})
            data = json.loads(text)
            result = data.get("result", {})
            location = result.get("location", {})
            if "lat" in location and "lng" in location:
                return json.dumps({
                    "ok": True,
                    "lat": float(location["lat"]),
                    "lng": float(location["lng"]),
                    "source": "geocode",
                }, ensure_ascii=False)
        except Exception as e:
            logger.warning("[Location] Geocode failed: %s", e)

    user_ip = get_ip_via_stun()
    if user_ip and user_ip not in ("127.0.0.1", "localhost", "::1"):
        try:
            text = await _baidu_tool_text("map_ip_location", {"ip": user_ip})
            data = json.loads(text)
            if data.get("status") != 0:
                raise ValueError(data.get("message", "ip location failed"))
            point = data.get("content", {}).get("point", {})
            x_str = point.get("x")
            y_str = point.get("y")
            if not x_str or not y_str:
                raise ValueError("missing x/y coordinates")
            lng, lat = bd09mc_to_bd09(float(x_str), float(y_str))
            return json.dumps({
                "ok": True,
                "lat": lat,
                "lng": lng,
                "source": "ip",
            }, ensure_ascii=False)
        except Exception as e:
            logger.warning("[Location] IP location failed: %s", e)

    return json.dumps({
        "ok": False,
        "error": "无法解析用户位置，使用默认坐标",
        "lat": 39.9042,
        "lng": 116.4074,
        "source": "fallback",
    }, ensure_ascii=False)


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


async def geocode_destination_impl(address: str) -> str:
    try:
        return await _baidu_tool_text("map_geocode", {"address": address})
    except Exception as e:
        logger.error("[GeocodeDestination] failed: %s", e, exc_info=True)
        return json.dumps({
            "ok": False,
            "error": f"destination geocode failed: {str(e)}",
        }, ensure_ascii=False)


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
) -> str:
    try:
        if not origin or not destination:
            return json.dumps({
                "ok": False,
                "error": "起点或终点为空，无法生成导航链接",
            }, ensure_ascii=False)

        text = await _baidu_tool_text(
            "map_uri",
            {
                "service": "direction",
                "origin": origin,
                "destination": destination,
                "mode": mode,
                "region": region,
            },
        )
        url = None
        for part in text.splitlines() or [text]:
            part = part.strip()
            if not part:
                continue
            try:
                data = json.loads(part)
                url = data.get("url") or data.get("uri") or data.get("link")
            except json.JSONDecodeError:
                url = part
            if url:
                break

        if not url:
            return json.dumps({
                "ok": False,
                "error": "百度地图 MCP 未返回导航链接",
            }, ensure_ascii=False)

        return json.dumps({
            "ok": True,
            "url": url,
            "markdown_link": f"[点击开始导航]({url})",
        }, ensure_ascii=False)
    except Exception as e:
        logger.error("[MapNavigation] failed: %s", e, exc_info=True)
        return json.dumps({
            "ok": False,
            "error": f"导航链接生成失败: {str(e)}",
        }, ensure_ascii=False)


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

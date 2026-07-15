import asyncio
import json
from typing import Any

import httpx
from agents.mcp import MCPServerStreamableHttp

from app.config.settings import settings


def _mcp_httpx_client_factory(headers=None, timeout=None, auth=None):
    return httpx.AsyncClient(
        headers=headers,
        timeout=timeout,
        auth=auth,
        trust_env=False,
    )


search_mcp_client = MCPServerStreamableHttp(
    name="通用联网搜索",
    params={
        "url": settings.DASHSCOPE_BASE_URL,
        "headers": {
            "Authorization": f"Bearer {settings.DASHSCOPE_API_KEY}",
        },
        "timeout": 60,
        "httpx_client_factory": _mcp_httpx_client_factory,
    },
    client_session_timeout_seconds=60 * 10,
    cache_tools_list=True,
    tool_filter={"allowed_tool_names": ["bailian_web_search"]},
    max_retry_attempts=0,
)

baidu_mcp_client = MCPServerStreamableHttp(
    name="百度地图",
    params={
        "url": f"https://mcp.map.baidu.com/mcp?ak={settings.BAIDUMAP_AK}",
        "timeout": 60,
        "sse_read_timeout": 60 * 30,
        "httpx_client_factory": _mcp_httpx_client_factory,
    },
    client_session_timeout_seconds=60 * 10,
    cache_tools_list=True,
    tool_filter={"allowed_tool_names": ["map_geocode", "map_ip_location", "map_uri"]},
    max_retry_attempts=0,
)


async def run_mcp_call(
    mcp_instance: MCPServerStreamableHttp,
    tool_name: str,
    tool_args: dict[str, Any],
) -> None:
    server_name = mcp_instance.name
    print(f"\n{'=' * 60}")
    print(f"[MCP probe] server: {server_name}")
    print(f"{'=' * 60}")

    try:
        print("[connect] connecting...")
        await mcp_instance.connect()
        print("[connect] ok")

        print("[tools] listing tools...")
        tools_list = await mcp_instance.list_tools()
        print(f"[tools] found {len(tools_list)} tools")
        for index, tool in enumerate(tools_list, 1):
            print(f"[{index}] {tool.name}")
            print(json.dumps(tool.inputSchema, indent=2, ensure_ascii=False))

        print(f"[call] {tool_name} args={json.dumps(tool_args, ensure_ascii=False)}")
        result = await mcp_instance.call_tool(tool_name, tool_args)
        print("[response] received")

        for content in result.content:
            if hasattr(content, "text") and content.text is not None:
                text = content.text
                print("\n========== raw text ==========")
                print(repr(text))
                if not text.strip():
                    print("empty response")
                    continue
                try:
                    parsed = json.loads(text)
                    print(json.dumps(parsed, indent=2, ensure_ascii=False))
                except json.JSONDecodeError:
                    print(text)
            elif getattr(content, "type", None) == "image":
                print("\n========== image payload ==========")
                print(f"mimeType: {getattr(content, 'mimeType', None)}")
            else:
                print(f"\n[non-text] {content}")

    except Exception as exc:
        print(f"[error] MCP probe failed: {exc}")
        import traceback

        traceback.print_exc()

    finally:
        print("[cleanup] closing...")
        await mcp_instance.cleanup()
        print(f"[done] {server_name}\n")


async def test_bailian_search() -> None:
    await run_mcp_call(
        mcp_instance=search_mcp_client,
        tool_name="bailian_web_search",
        tool_args={"query": "小米公司今天的股价如何?"},
    )


async def test_baidu_map() -> None:
    await run_mcp_call(
        mcp_instance=baidu_mcp_client,
        tool_name="map_uri",
        tool_args={
            "service": "direction",
            "origin": "name:天安门|latlng:39.908823,116.397470",
            "destination": "name:北京南站|latlng:39.865195,116.378545",
            "mode": "driving",
            "region": "北京市",
        },
    )


async def main() -> None:
    await test_baidu_map()


if __name__ == "__main__":
    asyncio.run(main())

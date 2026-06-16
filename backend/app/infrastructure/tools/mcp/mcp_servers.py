import asyncio
import json
from app.config.settings import settings
from agents.mcp import MCPServerSse, MCPServerStreamableHttp
from typing import Dict, Any

# 1. 定义百炼的通用搜索MCP客户端
search_mcp_client = MCPServerStreamableHttp(
    name="通用联网搜索",
    params={
        "url": settings.DASHSCOPE_BASE_URL,
        "headers": {
            "Authorization": f"Bearer {settings.AL_BAILIAN_API_KEY}"
        },
        "timeout": 60,
    },
    client_session_timeout_seconds=60 * 10,
    cache_tools_list=True,
)

# 2. 定义百度地图相关的MCP客户端(AK)
baidu_mcp_client = MCPServerStreamableHttp(
    name="百度地图",
    params={  # https://mcp.map.baidu.com/sse?ak=您的ak
        "url": f"https://mcp.map.baidu.com/mcp?ak={settings.BAIDUMAP_AK}",
        "timeout": 60,  # 客户端和mcp服务端建立连接的最大时间（s）（小一些）
        "sse_read_timeout": 60 * 30  # 客户端接收mcp服务端接收数据（数据包）的最大等待时间（大一些）
    },
    client_session_timeout_seconds=60 * 10,  # 客户端基于会话级别的超时时间
    cache_tools_list=True,
)


# ==============================================================================
# 3. 通用测试执行器 (新增：列出工具 -> 查看参数 -> 调用)
# ==============================================================================
async def run_mcp_call(
        mcp_instance: MCPServerStreamableHttp,
        tool_name: str,
        tool_args: Dict[str, Any]
):
    """
    执行流程：连接 -> 列出所有工具(看参数) -> 调用指定工具 -> 打印结果 -> 断开
    """
    server_name = mcp_instance.name
    print(f"\n{'=' * 60}")
    print(f" [测试启动] 服务: {server_name}")
    print(f"{'=' * 60}")

    try:
        # --- 1. 连接 ---
        print(f" [连接] 正在连接服务器...")
        await mcp_instance.connect()
        print(f" [连接] 成功")

        # --- 2. 列出工具  mcp服务下有多少个工具---
        print(f"\n [列表] 正在获取工具列表及参数定义...")
        tools_list = await mcp_instance.list_tools()

        if tools_list:
            print(f"   发现 {len(tools_list)} 个工具：")
            for i, tool in enumerate(tools_list, 1):
                print(f"\n    [{i}] 工具名: {tool.name}")
                print(f"       描述: {tool.description}")
                print(f"       参数定义 (Schema):")
                # 使用 indent=2 让参数结构清晰可见(inputSchema:工具参数（字典）)
                print(json.dumps(tool.inputSchema, indent=2, ensure_ascii=False))
        else:
            print("    未获取到工具列表")

        print(f"\n{'-' * 40}")

        # # --- 3. 调用工具 ---

        print(f"    发送参数: {json.dumps(tool_args, ensure_ascii=False)}")

        # 执行核心调用（调用mcp服务中某一个工具）
        result = await mcp_instance.call_tool(tool_name, tool_args)
        print(f"\n [响应] 服务器返回结果:")

        # --- 4. 打印结果 ---
        # for content in result.content:
        #     if hasattr(content, 'text'):
        #         # 尝试解析 JSON 字符串以便美化打印
        #         json_res = json.loads(content.text)
        #         print(json.dumps(json_res, indent=2, ensure_ascii=False))
                # try:
                #     json_res = json.loads(content.text)
                #
                #     print("\n========== 搜索结果 ==========")
                #     print(f"状态码: {json_res.get('status')}")
                #     print(f"请求ID: {json_res.get('request_id')}")
                #
                #     pages = json_res.get("pages", [])
                #     print(f"结果数量: {len(pages)}")
                #
                #     for index, page in enumerate(pages, 1):
                #         print(f"\n---------- 结果 {index} ----------")
                #         print(f"标题: {page.get('title')}")
                #         print(f"来源: {page.get('hostname')}")
                #         print(f"链接: {page.get('url')}")
                #         print(f"摘要: {page.get('snippet')}")
                #
                # except json.JSONDecodeError:
                #     print("返回内容不是合法 JSON:")
                #     print(content.text)
        for content in result.content:
            # 文本内容
            if hasattr(content, "text") and content.text is not None:
                text = content.text

                print("\n========== 原始文本返回 ==========")
                print(repr(text))

                if not text.strip():
                    print("返回内容为空")
                    continue

                try:
                    json_res = json.loads(text)
                    print("\n========== JSON 格式化结果 ==========")
                    print(json.dumps(json_res, indent=2, ensure_ascii=False))
                except json.JSONDecodeError:
                    print("\n返回内容不是合法 JSON，按普通文本输出:")
                    print(text)

            # 图片内容，例如二维码
            elif getattr(content, "type", None) == "image":
                print("\n========== 图片返回 ==========")
                print(f"图片类型: {getattr(content, 'mimeType', None)}")
                print("这是 base64 图片数据，通常是二维码或地图图片，不要用 json.loads 解析。")

            else:
                print(f"\n[Non-Text]: {content}")

    except Exception as e:
        print(f"\n [异常] 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

    finally:
        # --- 5. 清理 ---
        print(f"\n [断开] 正在清理连接...")
        await mcp_instance.cleanup()
        print(f" {server_name} 测试结束\n")


# ==============================================================================
# 4. 分别封装的测试函数
# ==============================================================================

async def test_bailian_search():
    """
    测试百炼搜索 (使用全局 search_mcp)
    """
    await run_mcp_call(
        mcp_instance=search_mcp_client,
        tool_name="bailian_web_search",  # 准备测试联网搜索工具
        tool_args={"query": "小米公司今天的股价如何?"}  # query
    )


async def test_baidu_map():
    """
    测试百度地图 (使用全局 baidu_mcp)
    """
    # await run_mcp_call(
    #     mcp_instance=baidu_mcp_client,
    #     tool_name="map_geocode",  # (地理位置编码)
    #     tool_args={
    #         "address": "北京市昌平区",
    #     }
    # )

    # await run_mcp_call(
    #     mcp_instance=baidu_mcp_client,
    #     tool_name="map_ip_location",  # (根据ip获取经纬度)
    #     tool_args={
    #         "ip": "123.120.109.232",
    #     }
    # )

    await run_mcp_call(
        mcp_instance=baidu_mcp_client,
        tool_name="map_uri",
        tool_args={
            "service": "direction",
            "origin": "name:天安门|latlng:39.908823,116.397470",
            "destination": "name:北京南站|latlng:39.865195,116.378545",
            "mode": "driving",
            "region": "北京市"
        }
    )
# ==============================================================================
# 5. 主程序入口
# ==============================================================================
async def main():
    # 你可以在这里注释掉不需要跑的测试

    # 任务 1
    # await test_bailian_search()

    # 任务 2
    await test_baidu_map()


if __name__ == '__main__':
    asyncio.run(main())

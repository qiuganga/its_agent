import asyncio
from typing import Dict, Any

import httpx
from agents import RunContextWrapper, function_tool

from app.infrastructure.logging.logger import logger
from app.config.settings import settings
from app.infrastructure.harness.context import AgentRunContext
from app.infrastructure.tools.mcp.mcp_servers import search_mcp_client


async def query_knowledge_impl(question: str) -> Dict[str, Any]:
    """
    普通函数：真正请求知识库服务。
    这个函数可以在 main() 中直接 await 调用，用于测试接口是否正常。
    """

    if not question:
        return {
            "status": "error",
            "error_msg": "question 不能为空"
        }

    if not settings.KNOWLEDGE_BASE_URL:
        return {
            "status": "error",
            "error_msg": "KNOWLEDGE_BASE_URL 未配置"
        }

    url = f"{settings.KNOWLEDGE_BASE_URL.rstrip('/')}/query"

    async with httpx.AsyncClient(trust_env=False) as client:
        try:
            response = await client.post(
                url=url,
                json={"question": question},
                timeout=60
            )

            # 4xx / 5xx 会在这里抛出 httpx.HTTPStatusError
            response.raise_for_status()

            return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(
                f"知识库服务返回错误状态码: "
                f"status_code={e.response.status_code}, "
                f"response={e.response.text}"
            )
            return {
                "status": "error",
                "error_msg": f"知识库服务返回错误状态码: {e.response.status_code}",
                "detail": e.response.text
            }

        except httpx.RequestError as e:
            logger.error(f"请求知识库服务失败: {str(e)}")
            return {
                "status": "error",
                "error_msg": f"请求知识库服务失败: {e}"
            }

        except Exception as e:
            logger.error(f"未知错误: {str(e)}")
            return {
                "status": "error",
                "error_msg": f"未知错误: {e}"
            }


@function_tool
async def query_knowledge(ctx: RunContextWrapper[AgentRunContext], question: str) -> Dict[str, Any]:
    """
    查询电脑问题知识库服务，用于检索与用户问题相关的技术文档或解决方案。

    Args:
        question: 需要查询的具体问题文本。

    Returns:
        dict: 包含查询结果的字典，例如：
              {
                  "question": "用户输入问题",
                  "answer": "知识库返回答案"
              }
    """
    return await ctx.context.system_harness.invoke(
        run_context=ctx.context,
        agent_key="technical_agent",
        tool_name="query_knowledge",
        arguments={"question": question},
        action=lambda: query_knowledge_impl(question),
    )


async def search_web_impl(query: str) -> str:
    result = await search_mcp_client.call_tool(
        "bailian_web_search",
        {"query": query}
    )
    texts = []
    for content in result.content:
        if hasattr(content, "text") and content.text:
            texts.append(content.text)
    return "\n".join(texts)


@function_tool
async def search_web(ctx: RunContextWrapper[AgentRunContext], query: str) -> str:
    """
    Search the public web for current information. Use only after the private
    knowledge base has no useful result, or for real-time information.
    """
    result = await ctx.context.system_harness.invoke(
        run_context=ctx.context,
        agent_key="technical_agent",
        tool_name="search_web",
        arguments={"query": query},
        action=lambda: search_web_impl(query),
    )
    if isinstance(result, dict):
        return json.dumps(result, ensure_ascii=False)
    return result


async def main():
    """
    本地测试时调用普通函数 query_knowledge_impl，不要直接调用 query_knowledge。
    因为 query_knowledge 被 @function_tool 包装后已经变成 FunctionTool 对象。
    """

    result = await query_knowledge_impl(question="开机屏幕黑屏或蓝屏报错,无法正常进入系统怎么办?")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())

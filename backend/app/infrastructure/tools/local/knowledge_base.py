import asyncio
from typing import Dict, Any
import json
import httpx
from agents import RunContextWrapper, function_tool

from app.infrastructure.logging.logger import logger
from app.config.settings import settings
from app.infrastructure.harness.context import AgentRunContext
from app.infrastructure.tools.mcp.mcp_servers import search_mcp_client
from app.infrastructure.tools.mcp.contracts import call_mcp_with_contract
from app.schemas.clarification import make_clarification_result


def is_vague_technical_query(query: str) -> bool:
    query = (query or "").strip()
    if len(query) <= 4:
        return True
    vague_terms = ["坏了", "不能用", "有问题", "报错", "黑屏", "蓝屏", "连不上", "打不开"]
    has_vague_term = any(term in query for term in vague_terms)
    detail_tokens = [
        "错误码", "型号", "Windows", "windows", "win10", "win11", "ThinkPad",
        "小新", "拯救者", "BIOS", "bios", "驱动", "电源灯", "风扇", "Logo", "logo",
    ]
    has_detail = any(token in query for token in detail_tokens)
    return has_vague_term and not has_detail


async def query_knowledge_impl(question: str) -> Dict[str, Any]:
    """
    普通函数：真正请求知识库服务。
    这个函数可以在 main() 中直接 await 调用，用于测试接口是否正常。
    """

    if not question:
        return make_clarification_result(
            clarification_type="missing_error_detail",
            missing_fields=["error_detail"],
            clarification_question="请补充具体故障现象或报错信息，我可以继续帮你排查。",
            source="query_knowledge",
            original_query=question,
            suggested_examples=["开机黑屏但电源灯亮", "蓝屏错误码 CRITICAL_PROCESS_DIED"],
        )

    if is_vague_technical_query(question):
        return make_clarification_result(
            clarification_type="missing_device_info",
            missing_fields=["device_model", "os_version", "error_detail"],
            clarification_question="请补充设备型号、系统版本，以及具体故障现象或报错信息，我可以继续帮你排查。",
            source="query_knowledge",
            original_query=question,
            suggested_examples=[
                "ThinkPad T14，Windows 11，开机黑屏但电源灯亮",
                "小新 Pro，蓝屏错误码 CRITICAL_PROCESS_DIED",
            ],
        )

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

    url = f"{settings.KNOWLEDGE_BASE_URL.rstrip('/')}/retrieve"

    async with httpx.AsyncClient(trust_env=False) as client:
        try:
            response = await client.post(
                url=url,
                json={"question": question},
                timeout=20
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
    return await call_mcp_with_contract(
        provider="bailian",
        tool_name="search_web",
        arguments={"query": query},
        action=lambda args: search_mcp_client.call_tool("bailian_web_search", args),
    )


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

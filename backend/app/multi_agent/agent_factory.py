import json

from agents import RunContextWrapper, Runner, function_tool
from agents.run import RunConfig, ToolExecutionConfig

from app.infrastructure.harness.context import AgentRunContext
from app.infrastructure.tools.local.knowledge_base import is_vague_technical_query
from app.infrastructure.logging.logger import logger
from app.multi_agent.service_agent import comprehensive_service_agent
from app.multi_agent.technical_agent import technical_agent
from app.schemas.clarification import make_clarification_result


def build_controlled_run_config(ctx: AgentRunContext) -> RunConfig:
    trace_enabled = ctx.system_harness.policy.trace_enabled
    return RunConfig(
        tracing_disabled=not trace_enabled,
        trace_include_sensitive_data=False,
        workflow_name="its_agent",
        group_id=ctx.session_id,
        trace_metadata={
            "run_id": ctx.run_id,
            "session_id": ctx.session_id,
        },
        tool_execution=ToolExecutionConfig(max_function_tool_concurrency=1),
    )


async def _run_technical_agent(ctx: AgentRunContext, query: str) -> str:
    logger.info("[Route] transfer to technical expert")
    result = await Runner.run(
        technical_agent,
        input=query,
        context=ctx,
        max_turns=ctx.system_harness.policy.technical_agent_max_turns,
        run_config=build_controlled_run_config(ctx),
    )
    return result.final_output


async def _run_service_agent(ctx: AgentRunContext, query: str) -> str:
    logger.info("[Route] transfer to service expert")
    result = await Runner.run(
        comprehensive_service_agent,
        input=query,
        context=ctx,
        max_turns=ctx.system_harness.policy.service_agent_max_turns,
        run_config=build_controlled_run_config(ctx),
    )
    return result.final_output


def _has_location_hint(query: str) -> bool:
    text = (query or "").strip()
    if not text:
        return False
    location_markers = [
        "我在", "位于", "北京", "上海", "广州", "深圳", "成都", "杭州", "南京", "武汉",
        "重庆", "天津", "西安", "苏州", "中关村", "故宫", "三里屯", "市", "区", "县",
        "镇", "路", "街", "号", "大厦", "广场", "机场", "车站",
    ]
    for marker in location_markers:
        if marker == "路" and "路" in text:
            if text.replace("路线", "").find("路") == -1:
                continue
        if marker in text:
            return True
    return False


def _needs_location_clarification(query: str) -> bool:
    text = (query or "").strip()
    if not text or _has_location_hint(text):
        return False
    intent_markers = ["我这里", "附近", "最近", "服务站", "维修站", "路线", "导航", "怎么走"]
    return any(marker in text for marker in intent_markers)


def _is_vague_technical_request(query: str) -> bool:
    text = (query or "").strip()
    if is_vague_technical_query(text):
        return True
    vague_terms = ["黑屏", "蓝屏", "坏了", "不能用", "有问题", "报错", "连不上", "打不开"]
    detail_terms = [
        "错误码", "型号", "Windows", "windows", "win10", "win11", "ThinkPad",
        "小新", "拯救者", "BIOS", "bios", "驱动", "电源灯", "风扇", "Logo", "logo",
    ]
    return any(term in text for term in vague_terms) and not any(term in text for term in detail_terms)


async def _record_clarification(ctx: AgentRunContext, payload: dict) -> dict:
    await ctx.run_state.set_pending_clarification(payload)
    return payload


@function_tool
async def consult_technical_expert(
    ctx: RunContextWrapper[AgentRunContext],
    query: str,
) -> str:
    """
    Consult the technical expert for device troubleshooting, repair advice,
    and real-time information tasks.
    """
    if _is_vague_technical_request(query):
        payload = make_clarification_result(
            clarification_type="missing_device_info",
            missing_fields=["device_model", "os_version", "error_detail"],
            clarification_question="请补充设备型号、系统版本，以及具体故障现象或报错信息，我可以继续帮你排查。",
            source="consult_technical_expert",
            original_query=query,
            suggested_examples=[
                "ThinkPad T14，Windows 11，开机黑屏但电源灯亮",
                "小新 Pro，蓝屏错误码 CRITICAL_PROCESS_DIED",
            ],
        )
        await _record_clarification(ctx.context, payload)
        return json.dumps(payload, ensure_ascii=False)

    result = await ctx.context.system_harness.invoke(
        run_context=ctx.context,
        agent_key="orchestrator",
        tool_name="consult_technical_expert",
        arguments={"query": query},
        action=lambda: _run_technical_agent(ctx.context, query),
    )
    if isinstance(result, dict):
        return json.dumps(result, ensure_ascii=False)
    return result


async def consult_technical_expert_impl(ctx: AgentRunContext, query: str) -> str:
    return await _run_technical_agent(ctx, query)


@function_tool
async def query_service_station_and_navigate(
    ctx: RunContextWrapper[AgentRunContext],
    query: str,
) -> str:
    """
    Ask the service expert to query repair shops, resolve locations, and
    generate navigation links.
    """
    if _needs_location_clarification(query):
        payload = make_clarification_result(
            clarification_type="missing_location",
            missing_fields=["city_or_address"],
            clarification_question="请提供你所在的城市或具体地址，我再帮你查询附近服务站或生成导航。",
            source="query_service_station_and_navigate",
            original_query=query,
            suggested_examples=["北京市海淀区中关村", "上海市徐汇区漕河泾", "深圳市南山区科技园"],
        )
        await _record_clarification(ctx.context, payload)
        return json.dumps(payload, ensure_ascii=False)

    result = await ctx.context.system_harness.invoke(
        run_context=ctx.context,
        agent_key="orchestrator",
        tool_name="query_service_station_and_navigate",
        arguments={"query": query},
        action=lambda: _run_service_agent(ctx.context, query),
    )
    if isinstance(result, dict):
        return json.dumps(result, ensure_ascii=False)
    return result


async def query_service_station_and_navigate_impl(ctx: AgentRunContext, query: str) -> str:
    return await _run_service_agent(ctx, query)


AGENT_TOOLS = [
    consult_technical_expert,
    query_service_station_and_navigate,
]

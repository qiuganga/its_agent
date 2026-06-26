import json

from agents import RunContextWrapper, Runner, function_tool
from agents.run import RunConfig, ToolExecutionConfig

from app.infrastructure.harness.context import AgentRunContext
from app.infrastructure.logging.logger import logger
from app.multi_agent.service_agent import comprehensive_service_agent
from app.multi_agent.technical_agent import technical_agent


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


@function_tool
async def consult_technical_expert(
    ctx: RunContextWrapper[AgentRunContext],
    query: str,
) -> str:
    """
    Consult the technical expert for device troubleshooting, repair advice,
    and real-time information tasks.
    """
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

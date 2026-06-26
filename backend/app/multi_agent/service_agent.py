from agents import Agent, ModelSettings, Runner

from app.infrastructure.ai.openai_client import sub_model
from app.infrastructure.ai.prompt_loader import load_prompt
from app.infrastructure.tools.local.service_station import (
    geocode_destination,
    map_navigation_tool,
    query_nearest_repair_shops_by_coords,
    resolve_user_location_from_text,
)


comprehensive_service_agent = Agent(
    name="全能业务智能体",
    instructions=load_prompt("comprehensive_service_agent"),
    model=sub_model,
    model_settings=ModelSettings(
        temperature=0,
        max_tokens=2048,
        parallel_tool_calls=False,
    ),
    tools=[
        resolve_user_location_from_text,
        query_nearest_repair_shops_by_coords,
        geocode_destination,
        map_navigation_tool,
    ],
)


async def run_single_test(case_name: str, input_text: str):
    print(f"\n{'=' * 80}")
    print(f"测试用例: {case_name}")
    print(f"输入: \"{input_text}\"")
    print("-" * 80)
    result = await Runner.run(
        comprehensive_service_agent,
        input=input_text,
        max_turns=5,
    )
    print(f"\n\nAgent最终输出: {result.final_output}")

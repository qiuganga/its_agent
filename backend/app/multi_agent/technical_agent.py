from agents import Agent, ModelSettings, Runner
from agents.run import RunConfig

from app.infrastructure.ai.openai_client import sub_model
from app.infrastructure.ai.prompt_loader import load_prompt
from app.infrastructure.tools.local.knowledge_base import query_knowledge, search_web


technical_agent = Agent(
    name="资讯与技术专家",
    instructions=load_prompt("technical_agent"),
    model=sub_model,
    model_settings=ModelSettings(temperature=0, parallel_tool_calls=False),
    tools=[query_knowledge, search_web],
)


async def run_single_test(case_name: str, input_text: str):
    print(f"\n{'=' * 80}")
    print(f"测试用例: {case_name}")
    print(f"输入: \"{input_text}\"")
    print("-" * 80)
    result = await Runner.run(
        technical_agent,
        input=input_text,
        max_turns=4,
        run_config=RunConfig(tracing_disabled=True),
    )
    print(f"\n\nAgent最终输出: {result.final_output}")

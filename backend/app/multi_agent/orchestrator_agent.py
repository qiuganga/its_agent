from agents import Agent, ModelSettings

from app.infrastructure.ai.openai_client import sub_model
from app.infrastructure.ai.prompt_loader import load_prompt
from app.multi_agent.agent_factory import AGENT_TOOLS


orchestrator_agent = Agent(
    name="主调度智能体",
    instructions=load_prompt("orchestrator_v1"),
    model=sub_model,
    model_settings=ModelSettings(
        temperature=0,
        parallel_tool_calls=False,
    ),
    tools=AGENT_TOOLS,
)

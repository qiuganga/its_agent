from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping, Optional, Tuple


@dataclass(frozen=True)
class ToolPolicy:
    tool_name: str
    allowed_agents: Tuple[str, ...]
    max_calls_per_run: int
    max_calls_per_session: Optional[int]
    timeout_seconds: float
    max_concurrency: int
    count_toward_total_budget: bool = True
    count_as_sub_agent_call: bool = False


@dataclass(frozen=True)
class HarnessPolicy:
    orchestrator_max_turns: int
    technical_agent_max_turns: int
    service_agent_max_turns: int
    max_total_agent_visible_tool_calls: int
    max_total_sub_agent_tool_calls: int
    max_request_seconds: float
    max_concurrent_runs: int
    session_ttl_seconds: int
    session_max_total_tool_calls: int
    trace_enabled: bool
    tool_policies: Mapping[str, ToolPolicy]

    def get_tool_policy(self, tool_name: str) -> ToolPolicy | None:
        return self.tool_policies.get(tool_name)


def freeze_tool_policies(policies: Mapping[str, ToolPolicy]) -> Mapping[str, ToolPolicy]:
    return MappingProxyType(dict(policies))

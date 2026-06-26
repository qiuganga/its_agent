from dataclasses import dataclass
from typing import TYPE_CHECKING

from app.infrastructure.harness.run_state import RunHarnessState

if TYPE_CHECKING:
    from app.infrastructure.harness.system_harness import SystemHarness


@dataclass
class AgentRunContext:
    user_id: str
    session_id: str
    run_id: str
    user_query: str
    system_harness: "SystemHarness"
    run_state: RunHarnessState

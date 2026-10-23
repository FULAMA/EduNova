from dataclasses import dataclass

from tools.edunova.agents.role import AgentRole


@dataclass(frozen=True)
class AgentResult:
    agent: str
    role: AgentRole
    success: bool
    message: str
    provider: str = ""
    model: str = ""
    duration_ms: int = 0
    error: str | None = None

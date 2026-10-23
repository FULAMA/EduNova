from abc import ABC, abstractmethod

from tools.edunova.agents.result import AgentResult
from tools.edunova.agents.role import AgentRole


class Agent(ABC):
    name: str
    role: AgentRole

    @abstractmethod
    def run(self, task: str) -> AgentResult:
        """Execute an agent task."""
        raise NotImplementedError

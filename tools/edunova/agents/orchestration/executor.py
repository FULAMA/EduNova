from abc import ABC, abstractmethod

from tools.edunova.agents.provider import AgentProvider
from tools.edunova.agents.result import AgentResult


class ProviderExecutor(ABC):
    def execute(
        self,
        provider: AgentProvider,
        task: str,
    ) -> AgentResult:
        if not task.strip():
            raise ValueError("Task cannot be empty.")

        if not provider.name.strip():
            raise ValueError("Provider name cannot be empty.")

        return self.execute_provider(provider, task)

    @abstractmethod
    def execute_provider(
        self,
        provider: AgentProvider,
        task: str,
    ) -> AgentResult:
        raise NotImplementedError

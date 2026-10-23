from abc import ABC, abstractmethod

from tools.edunova.agents.provider import AgentProvider
from tools.edunova.agents.result import AgentResult


class ProviderAdapter(ABC):
    @abstractmethod
    def generate(
        self,
        provider: AgentProvider,
        task: str,
    ) -> AgentResult:
        raise NotImplementedError

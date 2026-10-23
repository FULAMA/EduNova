from collections.abc import Sequence

from tools.edunova.agents.provider import AgentProvider
from tools.edunova.agents.result import AgentResult


class FallbackManager:
    def __init__(self, executor) -> None:
        self._executor = executor

    def execute(
        self,
        providers: Sequence[AgentProvider],
        task: str,
    ) -> AgentResult:
        if not providers:
            raise ValueError("Provider list cannot be empty.")

        if not task.strip():
            raise ValueError("Task cannot be empty.")

        last_result: AgentResult | None = None

        for provider in providers:
            result = self._executor.execute(provider, task)
            last_result = result

            if result.success:
                return result

        assert last_result is not None
        return last_result

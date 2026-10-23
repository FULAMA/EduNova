from dataclasses import dataclass

from tools.edunova.agents.orchestration.executor import ProviderExecutor
from tools.edunova.agents.provider import AgentProvider
from tools.edunova.agents.providers.groq import GroqAdapter
from tools.edunova.agents.result import AgentResult


@dataclass
class FakeGroqMessage:
    content: str


@dataclass
class FakeGroqChoice:
    message: FakeGroqMessage


@dataclass
class FakeGroqResponse:
    choices: list[FakeGroqChoice]


class FakeGroqCompletions:
    def create(self, **kwargs):
        return FakeGroqResponse(
            choices=[
                FakeGroqChoice(
                    message=FakeGroqMessage(
                        content="Analyse terminée."
                    )
                )
            ]
        )


class FakeGroqChat:
    def __init__(self):
        self.completions = FakeGroqCompletions()


class FakeGroqClient:
    def __init__(self):
        self.chat = FakeGroqChat()


class GroqProviderExecutor(ProviderExecutor):
    def __init__(self, adapter: GroqAdapter) -> None:
        self._adapter = adapter

    def execute_provider(
        self,
        provider: AgentProvider,
        task: str,
    ) -> AgentResult:
        return self._adapter.generate(provider, task)


def test_executor_runs_groq_adapter():
    provider = AgentProvider(name="groq")
    adapter = GroqAdapter(FakeGroqClient())
    executor = GroqProviderExecutor(adapter)

    result = executor.execute(
        provider,
        "Analyse le domaine academic-records.",
    )

    assert result.success is True
    assert result.agent == "groq"
    assert result.message == "Analyse terminée."

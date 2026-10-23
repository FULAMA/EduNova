from dataclasses import dataclass

from tools.edunova.agents.provider import AgentProvider
from tools.edunova.agents.providers.openrouter import OpenRouterAdapter
from tools.edunova.agents.role import AgentRole


@dataclass
class FakeOpenRouterMessage:
    content: str


@dataclass
class FakeOpenRouterChoice:
    message: FakeOpenRouterMessage


@dataclass
class FakeOpenRouterResponse:
    choices: list[FakeOpenRouterChoice]


class FakeOpenRouterCompletions:
    def create(self, **kwargs):
        assert kwargs["model"] == "openrouter/free"
        assert kwargs["messages"][0]["role"] == "user"

        return FakeOpenRouterResponse(
            choices=[
                FakeOpenRouterChoice(
                    message=FakeOpenRouterMessage(
                        content="Réponse simulée d'OpenRouter."
                    )
                )
            ]
        )


class FakeOpenRouterChat:
    def __init__(self):
        self.completions = FakeOpenRouterCompletions()


class FakeOpenRouterClient:
    def __init__(self):
        self.chat = FakeOpenRouterChat()


def test_openrouter_adapter_generates_agent_result():
    provider = AgentProvider(name="openrouter")

    adapter = OpenRouterAdapter(FakeOpenRouterClient())

    result = adapter.generate(
        provider,
        "Analyse le module academic-records.",
    )

    assert result.success is True
    assert result.agent == "openrouter"
    assert result.role == AgentRole.BUILDER
    assert result.message == "Réponse simulée d'OpenRouter."
    assert result.provider == "openrouter"
    assert result.model == "openrouter/free"


def test_openrouter_adapter_rejects_empty_task():
    provider = AgentProvider(name="openrouter")
    adapter = OpenRouterAdapter(FakeOpenRouterClient())

    try:
        adapter.generate(provider, "")
    except ValueError as exc:
        assert "task" in str(exc).lower()
    else:
        raise AssertionError("Expected ValueError")

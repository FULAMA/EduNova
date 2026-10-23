from dataclasses import dataclass

from tools.edunova.agents.provider import AgentProvider
from tools.edunova.agents.providers.groq import GroqAdapter
from tools.edunova.agents.result import AgentResult
from tools.edunova.agents.role import AgentRole


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
        assert kwargs["model"] == "openai/gpt-oss-20b"
        assert kwargs["messages"][0]["role"] == "user"

        return FakeGroqResponse(
            choices=[
                FakeGroqChoice(
                    message=FakeGroqMessage(
                        content="Réponse simulée de Groq."
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


def test_groq_adapter_generates_agent_result():
    provider = AgentProvider(name="groq")

    adapter = GroqAdapter(FakeGroqClient())

    result = adapter.generate(
        provider,
        "Analyse le module academic-records.",
    )

    assert result.success is True
    assert result.agent == "groq"
    assert result.role == AgentRole.BUILDER
    assert result.message == "Réponse simulée de Groq."


def test_groq_adapter_rejects_empty_task():
    provider = AgentProvider(name="groq")
    adapter = GroqAdapter(FakeGroqClient())

    try:
        adapter.generate(provider, "")
    except ValueError as exc:
        assert "task" in str(exc).lower()
    else:
        raise AssertionError("Expected ValueError")

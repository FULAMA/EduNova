from types import SimpleNamespace

import pytest

from tools.edunova.agents.provider import AgentProvider
from tools.edunova.agents.role import AgentRole
from tools.edunova.agents.providers.mistral import (
    MistralAdapter,
    MistralClientFactory,
    MistralProviderFactory,
)
from tools.edunova.agents.orchestration.config import ProviderConfig


class FakeCompletions:
    def __init__(self, content):
        self.content = content

    def create(self, **kwargs):
        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content=self.content)
                )
            ]
        )


class FakeClient:
    def __init__(self, content):
        self.chat = SimpleNamespace(
            completions=FakeCompletions(content)
        )


def test_mistral_adapter_returns_success():
    adapter = MistralAdapter(
        client=FakeClient("MISTRAL_OK"),
        model="mistral-small-latest",
    )

    result = adapter.generate(
        AgentProvider(name="mistral"),
        "Réponds uniquement MISTRAL_OK",
    )

    assert result.success is True
    assert result.message == "MISTRAL_OK"
    assert result.provider == "mistral"
    assert result.model == "mistral-small-latest"
    assert result.role == AgentRole.BUILDER


def test_mistral_adapter_detects_empty_response():
    adapter = MistralAdapter(
        client=FakeClient(""),
        model="mistral-small-latest",
    )

    result = adapter.generate(
        AgentProvider(name="mistral"),
        "test",
    )

    assert result.success is False
    assert result.error == "empty_response"


def test_mistral_client_factory_requires_api_key(monkeypatch):
    monkeypatch.delenv("MISTRAL_API_KEY", raising=False)

    factory = MistralClientFactory()

    with pytest.raises(ValueError, match="MISTRAL_API_KEY"):
        factory.create(
            ProviderConfig(
                name="mistral",
                model="mistral-small-latest",
            )
        )


def test_mistral_client_factory_rejects_wrong_provider():
    factory = MistralClientFactory()

    with pytest.raises(ValueError, match="mistral"):
        factory.create(
            ProviderConfig(
                name="groq",
                model="mistral-small-latest",
            )
        )


def test_mistral_provider_factory_creates_adapter(monkeypatch):
    monkeypatch.setenv("MISTRAL_API_KEY", "test-key")

    class FakeClientFactory:
        def create(self, config):
            return FakeClient("MISTRAL_FACTORY_OK")

    factory = MistralProviderFactory(FakeClientFactory())

    adapter = factory.create(
        ProviderConfig(
            name="mistral",
            model="mistral-small-latest",
        )
    )

    result = adapter.generate(
        AgentProvider(name="mistral"),
        "test",
    )

    assert result.success is True
    assert result.message == "MISTRAL_FACTORY_OK"

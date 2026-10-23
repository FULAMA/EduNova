import pytest

from tools.edunova.agents.orchestration.config import ProviderConfig
from tools.edunova.agents.providers.groq import GroqClientFactory


def test_groq_factory_requires_api_key(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)

    config = ProviderConfig(
        name="groq",
        model="openai/gpt-oss-20b",
        timeout=60,
    )

    factory = GroqClientFactory()

    with pytest.raises(ValueError, match="GROQ_API_KEY"):
        factory.create(config)


def test_groq_factory_creates_client(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-groq-key")

    config = ProviderConfig(
        name="groq",
        model="openai/gpt-oss-20b",
        timeout=60,
    )

    factory = GroqClientFactory()

    client = factory.create(config)

    assert client is not None


def test_groq_factory_rejects_wrong_provider():
    config = ProviderConfig(
        name="gemini",
        model="some-model",
        timeout=60,
    )

    factory = GroqClientFactory()

    with pytest.raises(ValueError, match="groq"):
        factory.create(config)

import pytest

from tools.edunova.agents.orchestration.config import ProviderConfig
from tools.edunova.agents.providers.openrouter import OpenRouterClientFactory


def test_openrouter_factory_requires_api_key(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

    config = ProviderConfig(
        name="openrouter",
        model="openrouter/free",
        timeout=60,
    )

    factory = OpenRouterClientFactory()

    with pytest.raises(ValueError, match="OPENROUTER_API_KEY"):
        factory.create(config)


def test_openrouter_factory_creates_client(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-openrouter-key")

    config = ProviderConfig(
        name="openrouter",
        model="openrouter/free",
        timeout=60,
    )

    factory = OpenRouterClientFactory()

    client = factory.create(config)

    assert client is not None
    assert str(client.base_url).rstrip("/") == (
        "https://openrouter.ai/api/v1"
    )


def test_openrouter_factory_rejects_wrong_provider():
    config = ProviderConfig(
        name="groq",
        model="openai/gpt-oss-20b",
        timeout=60,
    )

    factory = OpenRouterClientFactory()

    with pytest.raises(ValueError, match="openrouter"):
        factory.create(config)

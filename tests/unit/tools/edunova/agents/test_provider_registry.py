import pytest

from tools.edunova.agents.provider import AgentProvider
from tools.edunova.agents.orchestration.registry import ProviderRegistry


def test_registry_registers_provider() -> None:
    registry = ProviderRegistry()
    provider = AgentProvider("gemini")

    registry.register(provider)

    assert registry.has("gemini")
    assert registry.get("gemini") == provider


def test_registry_supports_multiple_providers() -> None:
    registry = ProviderRegistry()

    registry.register(AgentProvider("gemini"))
    registry.register(AgentProvider("openrouter"))
    registry.register(AgentProvider("local"))

    assert registry.names() == (
        "gemini",
        "openrouter",
        "local",
    )


def test_registry_rejects_duplicate_provider() -> None:
    registry = ProviderRegistry()

    registry.register(AgentProvider("gemini"))

    with pytest.raises(ValueError, match="already registered"):
        registry.register(AgentProvider("gemini"))


def test_registry_get_unknown_provider_raises_key_error() -> None:
    registry = ProviderRegistry()

    with pytest.raises(KeyError):
        registry.get("unknown")


def test_registry_has_returns_false_for_unknown_provider() -> None:
    registry = ProviderRegistry()

    assert registry.has("unknown") is False

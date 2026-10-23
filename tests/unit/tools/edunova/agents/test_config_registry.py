from tools.edunova.agents.orchestration.config import ProviderConfig
from tools.edunova.agents.orchestration.registry import ProviderRegistry


def test_registry_accepts_provider_config() -> None:
    registry = ProviderRegistry()
    config = ProviderConfig(name="gemini")

    registry.register_config(config)

    assert registry.has_config("gemini")


def test_registry_returns_provider_config() -> None:
    registry = ProviderRegistry()
    config = ProviderConfig(
        name="openrouter",
        priority=2,
        model="test-model",
        timeout=120,
    )

    registry.register_config(config)

    result = registry.get_config("openrouter")

    assert result == config


def test_registry_rejects_duplicate_provider_config() -> None:
    registry = ProviderRegistry()

    registry.register_config(ProviderConfig(name="gemini"))

    try:
        registry.register_config(ProviderConfig(name="gemini"))
    except ValueError as exc:
        assert "already registered" in str(exc).lower()
    else:
        raise AssertionError("Expected ValueError")


def test_registry_lists_provider_configs() -> None:
    registry = ProviderRegistry()

    registry.register_config(ProviderConfig(name="gemini"))
    registry.register_config(ProviderConfig(name="openrouter"))

    assert registry.config_names() == ("gemini", "openrouter")

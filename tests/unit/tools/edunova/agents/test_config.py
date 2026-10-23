from tools.edunova.agents.orchestration.config import (
    ProviderConfig,
)


def test_provider_config_requires_name() -> None:
    try:
        ProviderConfig(name="")
    except ValueError as exc:
        assert "provider" in str(exc).lower()
    else:
        raise AssertionError("Expected ValueError")


def test_provider_config_has_defaults() -> None:
    config = ProviderConfig(name="gemini")

    assert config.name == "gemini"
    assert config.enabled
    assert config.priority == 1
    assert config.model == ""
    assert config.timeout == 60


def test_provider_config_accepts_custom_values() -> None:
    config = ProviderConfig(
        name="openrouter",
        enabled=False,
        priority=3,
        model="test-model",
        timeout=120,
    )

    assert config.name == "openrouter"
    assert not config.enabled
    assert config.priority == 3
    assert config.model == "test-model"
    assert config.timeout == 120


def test_provider_config_rejects_invalid_priority() -> None:
    try:
        ProviderConfig(name="gemini", priority=0)
    except ValueError as exc:
        assert "priority" in str(exc).lower()
    else:
        raise AssertionError("Expected ValueError")


def test_provider_config_rejects_invalid_timeout() -> None:
    try:
        ProviderConfig(name="gemini", timeout=0)
    except ValueError as exc:
        assert "timeout" in str(exc).lower()
    else:
        raise AssertionError("Expected ValueError")


def test_provider_config_is_immutable() -> None:
    config = ProviderConfig(name="gemini")

    try:
        config.enabled = False
    except AttributeError:
        pass
    else:
        raise AssertionError(
            "ProviderConfig must be immutable."
        )

import pytest

from tools.edunova.agents.orchestration.config import ProviderConfig
from tools.edunova.agents.providers.groq import (
    GroqProviderFactory,
)


class FakeFactory:
    def create(self, config):
        return f"adapter:{config.name}"


def test_provider_factory_registry_registers_and_resolves():
    from tools.edunova.agents.orchestration.factory_registry import (
        ProviderFactoryRegistry,
    )

    registry = ProviderFactoryRegistry()
    factory = FakeFactory()

    registry.register("groq", factory)

    assert registry.has("groq") is True
    assert registry.get("groq") is factory


def test_provider_factory_registry_rejects_duplicates():
    from tools.edunova.agents.orchestration.factory_registry import (
        ProviderFactoryRegistry,
    )

    registry = ProviderFactoryRegistry()

    registry.register("groq", FakeFactory())

    with pytest.raises(ValueError, match="already registered"):
        registry.register("groq", FakeFactory())


def test_provider_factory_registry_rejects_unknown_provider():
    from tools.edunova.agents.orchestration.factory_registry import (
        ProviderFactoryRegistry,
    )

    registry = ProviderFactoryRegistry()

    with pytest.raises(KeyError):
        registry.get("groq")

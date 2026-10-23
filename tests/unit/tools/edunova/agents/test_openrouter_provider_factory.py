from tools.edunova.agents.orchestration.config import ProviderConfig
from tools.edunova.agents.providers.openrouter import (
    OpenRouterAdapter,
    OpenRouterProviderFactory,
)


class FakeClient:
    pass


class FakeClientFactory:
    def __init__(self):
        self.received_config = None

    def create(self, config):
        self.received_config = config
        return FakeClient()


def test_openrouter_provider_factory_builds_adapter_from_config():
    config = ProviderConfig(
        name="openrouter",
        model="openrouter/free",
        timeout=45,
    )

    client_factory = FakeClientFactory()
    factory = OpenRouterProviderFactory(client_factory)

    adapter = factory.create(config)

    assert isinstance(adapter, OpenRouterAdapter)
    assert client_factory.received_config is config
    assert adapter._model == "openrouter/free"
    assert adapter._timeout == 45


def test_openrouter_provider_factory_rejects_wrong_provider():
    config = ProviderConfig(
        name="groq",
        model="openai/gpt-oss-20b",
        timeout=60,
    )

    factory = OpenRouterProviderFactory(FakeClientFactory())

    try:
        factory.create(config)
    except ValueError as exc:
        assert "openrouter" in str(exc).lower()
    else:
        raise AssertionError("Expected ValueError")

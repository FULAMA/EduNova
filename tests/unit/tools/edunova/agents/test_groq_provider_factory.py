from tools.edunova.agents.orchestration.config import ProviderConfig
from tools.edunova.agents.providers.groq import (
    GroqAdapter,
    GroqProviderFactory,
)


class FakeClient:
    pass


class FakeClientFactory:
    def __init__(self):
        self.received_config = None

    def create(self, config):
        self.received_config = config
        return FakeClient()


def test_groq_provider_factory_builds_adapter_from_config():
    config = ProviderConfig(
        name="groq",
        model="openai/gpt-oss-20b",
        timeout=45,
    )

    client_factory = FakeClientFactory()
    factory = GroqProviderFactory(client_factory)

    adapter = factory.create(config)

    assert isinstance(adapter, GroqAdapter)
    assert client_factory.received_config is config
    assert adapter._model == "openai/gpt-oss-20b"
    assert adapter._timeout == 45


def test_groq_provider_factory_rejects_wrong_provider():
    config = ProviderConfig(
        name="gemini",
        model="some-model",
        timeout=60,
    )

    factory = GroqProviderFactory(FakeClientFactory())

    try:
        factory.create(config)
    except ValueError as exc:
        assert "groq" in str(exc).lower()
    else:
        raise AssertionError("Expected ValueError")

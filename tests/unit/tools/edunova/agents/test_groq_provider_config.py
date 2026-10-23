from tools.edunova.agents.orchestration.config import ProviderConfig
from tools.edunova.agents.providers.groq import (
    GroqAdapter,
    GroqClientFactory,
)


class FakeClient:
    pass


class FakeFactory(GroqClientFactory):
    def __init__(self):
        self.config = None

    def create(self, config):
        self.config = config
        return FakeClient()


def test_groq_provider_configuration_is_preserved():
    config = ProviderConfig(
        name="groq",
        model="openai/gpt-oss-20b",
        timeout=45,
    )

    factory = FakeFactory()
    client = factory.create(config)

    adapter = GroqAdapter(
        client=client,
        model=config.model,
        timeout=config.timeout,
    )

    assert factory.config is config
    assert adapter._model == "openai/gpt-oss-20b"
    assert adapter._timeout == 45

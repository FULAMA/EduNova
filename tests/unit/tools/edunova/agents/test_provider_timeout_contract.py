from types import SimpleNamespace

import pytest

from tools.edunova.agents.orchestration.config import ProviderConfig
from tools.edunova.agents.provider import AgentProvider
from tools.edunova.agents.providers.mistral import (
    MistralAdapter,
    MistralProviderFactory,
)
from tools.edunova.agents.providers.qwen import (
    QwenAdapter,
    QwenProviderFactory,
)


class RecordingCompletions:
    def __init__(self) -> None:
        self.kwargs = None

    def create(self, **kwargs):
        self.kwargs = kwargs
        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content="OK")
                )
            ]
        )


class FakeClient:
    def __init__(self) -> None:
        self.completions = RecordingCompletions()
        self.chat = SimpleNamespace(completions=self.completions)


class FakeClientFactory:
    def __init__(self, client: FakeClient) -> None:
        self.client = client

    def create(self, config: ProviderConfig) -> FakeClient:
        return self.client


@pytest.mark.parametrize(
    ("adapter_class", "provider_name", "model"),
    [
        (MistralAdapter, "mistral", "mistral-small-latest"),
        (QwenAdapter, "qwen", "qwen-plus"),
    ],
)
def test_adapter_passes_configured_timeout(
    adapter_class,
    provider_name: str,
    model: str,
) -> None:
    client = FakeClient()
    adapter = adapter_class(
        client=client,
        model=model,
        timeout=7,
    )

    result = adapter.generate(
        AgentProvider(name=provider_name),
        "Test timeout",
    )

    assert result.success is True
    assert client.completions.kwargs["timeout"] == 7


@pytest.mark.parametrize(
    ("factory_class", "provider_name", "model"),
    [
        (MistralProviderFactory, "mistral", "mistral-small-latest"),
        (QwenProviderFactory, "qwen", "qwen-plus"),
    ],
)
def test_provider_factory_propagates_configured_timeout(
    factory_class,
    provider_name: str,
    model: str,
) -> None:
    client = FakeClient()
    factory = factory_class(FakeClientFactory(client))
    config = ProviderConfig(
        name=provider_name,
        model=model,
        timeout=17,
    )

    adapter = factory.create(config)
    result = adapter.generate(
        AgentProvider(name=provider_name),
        "Test factory timeout",
    )

    assert result.success is True
    assert client.completions.kwargs["timeout"] == 17

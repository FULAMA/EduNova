from types import SimpleNamespace

import pytest

from tools.edunova.agents.provider import AgentProvider
from tools.edunova.agents.role import AgentRole
from tools.edunova.agents.providers.qwen import (
    QwenAdapter,
    QwenClientFactory,
    QwenProviderFactory,
)
from tools.edunova.agents.orchestration.config import ProviderConfig


class FakeCompletions:
    def __init__(self, content):
        self.content = content

    def create(self, **kwargs):
        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content=self.content)
                )
            ]
        )


class FakeClient:
    def __init__(self, content):
        self.chat = SimpleNamespace(
            completions=FakeCompletions(content)
        )


def test_qwen_adapter_returns_success():
    adapter = QwenAdapter(
        client=FakeClient("QWEN_OK"),
        model="qwen-plus",
    )

    result = adapter.generate(
        AgentProvider(name="qwen"),
        "Réponds uniquement QWEN_OK",
    )

    assert result.success is True
    assert result.message == "QWEN_OK"
    assert result.provider == "qwen"
    assert result.model == "qwen-plus"
    assert result.role == AgentRole.BUILDER


def test_qwen_adapter_detects_empty_response():
    adapter = QwenAdapter(
        client=FakeClient(""),
        model="qwen-plus",
    )

    result = adapter.generate(
        AgentProvider(name="qwen"),
        "test",
    )

    assert result.success is False
    assert result.error == "empty_response"


def test_qwen_client_factory_requires_api_key(monkeypatch):
    monkeypatch.delenv("DASHSCOPE_API_KEY", raising=False)

    factory = QwenClientFactory()

    with pytest.raises(ValueError, match="DASHSCOPE_API_KEY"):
        factory.create(
            ProviderConfig(
                name="qwen",
                model="qwen-plus",
            )
        )


def test_qwen_client_factory_rejects_wrong_provider():
    factory = QwenClientFactory()

    with pytest.raises(ValueError, match="qwen"):
        factory.create(
            ProviderConfig(
                name="groq",
                model="qwen-plus",
            )
        )


def test_qwen_provider_factory_creates_adapter(monkeypatch):
    monkeypatch.setenv("DASHSCOPE_API_KEY", "test-key")

    class FakeClientFactory:
        def create(self, config):
            return FakeClient("QWEN_FACTORY_OK")

    factory = QwenProviderFactory(FakeClientFactory())

    adapter = factory.create(
        ProviderConfig(
            name="qwen",
            model="qwen-plus",
        )
    )

    result = adapter.generate(
        AgentProvider(name="qwen"),
        "test",
    )

    assert result.success is True
    assert result.message == "QWEN_FACTORY_OK"

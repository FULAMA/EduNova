from tools.edunova.agents.orchestration.config import ProviderConfig
from tools.edunova.agents.orchestration.factory_registry import (
    ProviderFactoryRegistry,
)
from tools.edunova.agents.orchestration.health import HealthTracker
from tools.edunova.agents.orchestration.quota import QuotaTracker
from tools.edunova.agents.orchestration.registry import ProviderRegistry
from tools.edunova.agents.orchestration.router import AgentRouter
from tools.edunova.agents.orchestration.service import AgentOrchestrationService
from tools.edunova.agents.provider import AgentProvider
from tools.edunova.agents.result import AgentResult
from tools.edunova.agents.role import AgentRole


class FakeAdapter:
    def __init__(self, result):
        self._result = result

    def generate(self, provider, task):
        return AgentResult(
            agent=provider.name,
            role=AgentRole.BUILDER,
            success=self._result["success"],
            message=self._result["message"],
            provider=provider.name,
            model="test-model",
            error=self._result.get("error"),
        )


class FakeFactory:
    def __init__(self, result):
        self._result = result

    def create(self, config):
        return FakeAdapter(self._result)


def test_four_provider_fallback_reaches_mistral():
    provider_registry = ProviderRegistry()
    factory_registry = ProviderFactoryRegistry()

    providers = [
        ("groq", 1),
        ("openrouter", 2),
        ("qwen", 3),
        ("mistral", 4),
    ]

    for name, priority in providers:
        provider_registry.register(
            AgentProvider(name=name)
        )

        provider_registry.register_config(
            ProviderConfig(
                name=name,
                enabled=True,
                priority=priority,
                model=f"{name}-model",
                timeout=60,
            )
        )

    factory_registry.register(
        "groq",
        FakeFactory(
            {
                "success": False,
                "message": "Groq unavailable",
                "error": "connection_error",
            }
        ),
    )

    factory_registry.register(
        "openrouter",
        FakeFactory(
            {
                "success": False,
                "message": "OpenRouter unavailable",
                "error": "timeout",
            }
        ),
    )

    factory_registry.register(
        "qwen",
        FakeFactory(
            {
                "success": False,
                "message": "Qwen unavailable",
                "error": "rate_limit",
            }
        ),
    )

    factory_registry.register(
        "mistral",
        FakeFactory(
            {
                "success": True,
                "message": "MISTRAL_FINAL_OK",
            }
        ),
    )

    health = HealthTracker()
    quota = QuotaTracker()

    router = AgentRouter(
        registry=provider_registry,
        health=health,
        quota=quota,
    )

    service = AgentOrchestrationService(
        provider_registry=provider_registry,
        factory_registry=factory_registry,
        router=router,
        health=health,
        quota=quota,
    )

    result = service.run("test fallback 4 providers")

    assert result.success is True
    assert result.provider == "mistral"
    assert result.message == "MISTRAL_FINAL_OK"

    assert quota.is_available("qwen") is False
    assert health.is_available("groq") is False
    assert health.is_available("openrouter") is False


def test_four_provider_router_respects_priority():
    provider_registry = ProviderRegistry()
    health = HealthTracker()
    quota = QuotaTracker()

    for name, priority in [
        ("groq", 1),
        ("openrouter", 2),
        ("qwen", 3),
        ("mistral", 4),
    ]:
        provider_registry.register(
            AgentProvider(name=name)
        )

        provider_registry.register_config(
            ProviderConfig(
                name=name,
                enabled=True,
                priority=priority,
            )
        )

    router = AgentRouter(
        registry=provider_registry,
        health=health,
        quota=quota,
    )

    assert router.select().name == "groq"
    assert router.select(excluded={"groq"}).name == "openrouter"
    assert router.select(
        excluded={"groq", "openrouter"}
    ).name == "qwen"
    assert router.select(
        excluded={"groq", "openrouter", "qwen"}
    ).name == "mistral"

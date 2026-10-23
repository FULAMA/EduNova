from tools.edunova.agents.orchestration.config import ProviderConfig
from tools.edunova.agents.orchestration.factory_registry import (
    ProviderFactoryRegistry,
)
from tools.edunova.agents.orchestration.health import HealthTracker
from tools.edunova.agents.orchestration.quota import QuotaTracker
from tools.edunova.agents.orchestration.registry import ProviderRegistry
from tools.edunova.agents.orchestration.router import AgentRouter
from tools.edunova.agents.orchestration.service import (
    AgentOrchestrationService,
)
from tools.edunova.agents.provider import AgentProvider
from tools.edunova.agents.result import AgentResult
from tools.edunova.agents.role import AgentRole


class FakeGroqAdapter:
    def generate(self, provider, task):
        return AgentResult(
            agent=provider.name,
            role=AgentRole.BUILDER,
            success=False,
            message="Groq simulated failure.",
            provider=provider.name,
            model="openai/gpt-oss-20b",
            error="connection_error",
        )


class FakeOpenRouterAdapter:
    def generate(self, provider, task):
        return AgentResult(
            agent=provider.name,
            role=AgentRole.BUILDER,
            success=True,
            message="OpenRouter simulated success.",
            provider=provider.name,
            model="openrouter/free",
        )


class FakeGroqFactory:
    def create(self, config):
        assert config.name == "groq"
        return FakeGroqAdapter()


class FakeOpenRouterFactory:
    def create(self, config):
        assert config.name == "openrouter"
        return FakeOpenRouterAdapter()


def test_groq_failure_falls_back_to_openrouter():
    provider_registry = ProviderRegistry()

    provider_registry.register(
        AgentProvider(name="groq")
    )
    provider_registry.register(
        AgentProvider(name="openrouter")
    )

    provider_registry.register_config(
        ProviderConfig(
            name="groq",
            priority=1,
            model="openai/gpt-oss-20b",
        )
    )
    provider_registry.register_config(
        ProviderConfig(
            name="openrouter",
            priority=2,
            model="openrouter/free",
        )
    )

    factory_registry = ProviderFactoryRegistry()

    factory_registry.register(
        "groq",
        FakeGroqFactory(),
    )
    factory_registry.register(
        "openrouter",
        FakeOpenRouterFactory(),
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

    result = service.run(
        "Analyse le module academic-records."
    )

    assert result.success is True
    assert result.agent == "openrouter"
    assert result.provider == "openrouter"
    assert result.model == "openrouter/free"
    assert result.message == "OpenRouter simulated success."

    assert health.is_available("groq") is False
    assert health.is_available("openrouter") is True


def test_groq_is_selected_before_openrouter():
    provider_registry = ProviderRegistry()

    provider_registry.register(
        AgentProvider(name="groq")
    )
    provider_registry.register(
        AgentProvider(name="openrouter")
    )

    provider_registry.register_config(
        ProviderConfig(
            name="groq",
            priority=1,
            model="openai/gpt-oss-20b",
        )
    )
    provider_registry.register_config(
        ProviderConfig(
            name="openrouter",
            priority=2,
            model="openrouter/free",
        )
    )

    health = HealthTracker()
    quota = QuotaTracker()

    router = AgentRouter(
        registry=provider_registry,
        health=health,
        quota=quota,
    )

    selected = router.select()

    assert selected.name == "groq"

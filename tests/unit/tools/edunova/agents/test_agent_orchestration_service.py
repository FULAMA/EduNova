from tools.edunova.agents.orchestration.config import ProviderConfig
from tools.edunova.agents.orchestration.factory_registry import (
    ProviderFactoryRegistry,
)
from tools.edunova.agents.orchestration.health import HealthTracker
from tools.edunova.agents.orchestration.quota import QuotaTracker
from tools.edunova.agents.orchestration.registry import ProviderRegistry
from tools.edunova.agents.orchestration.router import AgentRouter
from tools.edunova.agents.result import AgentResult
from tools.edunova.agents.role import AgentRole


class FakeProvider:
    name = "groq"


class FakeAdapter:
    def generate(self, provider, task):
        return AgentResult(
            agent=provider.name,
            role=AgentRole.BUILDER,
            success=True,
            message=f"Analyse: {task}",
        )


class FakeFactory:
    def create(self, config):
        return FakeAdapter()


def test_agent_orchestrator_runs_selected_provider():
    from tools.edunova.agents.orchestration.service import (
        AgentOrchestrationService,
    )

    providers = ProviderRegistry()
    providers.register(FakeProvider())
    providers.register_config(
        ProviderConfig(
            name="groq",
            model="test-model",
            timeout=30,
            priority=1,
        )
    )

    factories = ProviderFactoryRegistry()
    factories.register("groq", FakeFactory())

    service = AgentOrchestrationService(
        provider_registry=providers,
        factory_registry=factories,
        router=AgentRouter(
            registry=providers,
            health=HealthTracker(),
            quota=QuotaTracker(),
        ),
    )

    result = service.run("Analyse academic-records.")

    assert result.success is True
    assert result.agent == "groq"
    assert result.role == AgentRole.BUILDER
    assert result.message == "Analyse: Analyse academic-records."


def test_agent_orchestrator_rejects_empty_task():
    from tools.edunova.agents.orchestration.service import (
        AgentOrchestrationService,
    )

    providers = ProviderRegistry()
    factories = ProviderFactoryRegistry()

    service = AgentOrchestrationService(
        provider_registry=providers,
        factory_registry=factories,
        router=AgentRouter(
            registry=providers,
            health=HealthTracker(),
            quota=QuotaTracker(),
        ),
    )

    try:
        service.run("   ")
    except ValueError as exc:
        assert "task" in str(exc).lower()
    else:
        raise AssertionError("Expected ValueError")


class FailingFactory:
    def create(self, config):
        raise ValueError("OPENROUTER_API_KEY is required.")


class SuccessfulAdapter:
    def generate(self, provider, task):
        from tools.edunova.agents.result import AgentResult
        from tools.edunova.agents.role import AgentRole

        return AgentResult(
            agent=provider.name,
            role=AgentRole.BUILDER,
            success=True,
            message="Fallback provider succeeded.",
            provider=provider.name,
            model="fallback-model",
        )


class SuccessfulFactory:
    def create(self, config):
        return SuccessfulAdapter()


def test_orchestration_falls_back_when_provider_factory_fails():
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

    provider_registry = ProviderRegistry()
    provider_registry.register(AgentProvider(name="openrouter"))
    provider_registry.register(AgentProvider(name="fallback"))

    provider_registry.register_config(
        ProviderConfig(
            name="openrouter",
            model="openrouter/free",
            priority=1,
        )
    )
    provider_registry.register_config(
        ProviderConfig(
            name="fallback",
            model="fallback-model",
            priority=2,
        )
    )

    factory_registry = ProviderFactoryRegistry()
    factory_registry.register("openrouter", FailingFactory())
    factory_registry.register("fallback", SuccessfulFactory())

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

    result = service.run("Test fallback.")

    assert result.success is True
    assert result.agent == "fallback"
    assert result.message == "Fallback provider succeeded."
    assert health.is_available("openrouter") is False

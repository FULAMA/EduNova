from tools.edunova.agents.orchestration.config import ProviderConfig
from tools.edunova.agents.orchestration.factory_registry import ProviderFactoryRegistry
from tools.edunova.agents.orchestration.health import HealthTracker
from tools.edunova.agents.orchestration.quota import QuotaTracker
from tools.edunova.agents.orchestration.registry import ProviderRegistry
from tools.edunova.agents.orchestration.router import AgentRouter
from tools.edunova.agents.orchestration.service import AgentOrchestrationService
from tools.edunova.agents.provider import AgentProvider
from tools.edunova.agents.result import AgentResult
from tools.edunova.agents.role import AgentRole


class RaisingAdapter:
    def generate(self, provider, task):
        raise RuntimeError("Unexpected simulated provider failure")


class SuccessfulAdapter:
    def generate(self, provider, task):
        return AgentResult(
            agent=provider.name,
            role=AgentRole.BUILDER,
            success=True,
            message="Fallback succeeded.",
            provider=provider.name,
            model="fallback-model",
        )


class AdapterFactory:
    def __init__(self, adapter):
        self._adapter = adapter

    def create(self, config):
        return self._adapter


def test_unexpected_provider_exception_triggers_fallback():
    providers = ProviderRegistry()

    providers.register(AgentProvider(name="groq"))
    providers.register(AgentProvider(name="fallback"))

    providers.register_config(
        ProviderConfig(name="groq", model="test-model", priority=1)
    )
    providers.register_config(
        ProviderConfig(name="fallback", model="fallback-model", priority=2)
    )

    factories = ProviderFactoryRegistry()
    factories.register("groq", AdapterFactory(RaisingAdapter()))
    factories.register("fallback", AdapterFactory(SuccessfulAdapter()))

    health = HealthTracker()
    quota = QuotaTracker()
    router = AgentRouter(
        registry=providers,
        health=health,
        quota=quota,
    )

    service = AgentOrchestrationService(
        provider_registry=providers,
        factory_registry=factories,
        router=router,
        health=health,
        quota=quota,
    )

    result = service.run("Test unexpected exception fallback.")

    assert result.success is True
    assert result.agent == "fallback"
    assert result.message == "Fallback succeeded."
    assert health.is_available("groq") is False

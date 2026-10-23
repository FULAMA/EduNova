from tools.edunova.agents.orchestration.config import ProviderConfig
from tools.edunova.agents.orchestration.factory_registry import (
    ProviderFactoryRegistry,
)
from tools.edunova.agents.orchestration.health import HealthTracker
from tools.edunova.agents.orchestration.quota import QuotaTracker
from tools.edunova.agents.orchestration.registry import ProviderRegistry
from tools.edunova.agents.orchestration.router import AgentRouter
from tools.edunova.agents.orchestration.service import AgentOrchestrationService
from tools.edunova.agents.result import AgentResult
from tools.edunova.agents.role import AgentRole


class FakeProvider:
    def __init__(self, name: str) -> None:
        self.name = name


class FakeAdapter:
    def __init__(self, result: AgentResult) -> None:
        self._result = result

    def generate(self, provider, task):
        return self._result


class FakeFactory:
    def __init__(self, results: dict[str, AgentResult]) -> None:
        self._results = results

    def create(self, config):
        return FakeAdapter(self._results[config.name])


def create_service(results: dict[str, AgentResult]):
    providers = ProviderRegistry()

    for name in results:
        providers.register(FakeProvider(name))
        providers.register_config(
            ProviderConfig(
                name=name,
                model=f"{name}-model",
                priority=1 if name == "groq" else 2,
            )
        )

    factories = ProviderFactoryRegistry()

    for name in results:
        factories.register(
            name,
            FakeFactory(results),
        )

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

    return service, health, quota


def result(
    agent: str,
    success: bool,
    message: str,
    error: str | None = None,
) -> AgentResult:
    return AgentResult(
        agent=agent,
        role=AgentRole.BUILDER,
        success=success,
        message=message,
        provider=agent,
        model=f"{agent}-model",
        error=error,
    )


def test_orchestrator_falls_back_after_rate_limit():
    service, _, quota = create_service(
        {
            "groq": result(
                "groq",
                False,
                "Groq rate limit reached.",
                "rate_limit",
            ),
            "fallback": result(
                "fallback",
                True,
                "Fallback succeeded.",
            ),
        }
    )

    response = service.run("Analyse EduNova.")

    assert response.success is True
    assert response.agent == "fallback"
    assert response.message == "Fallback succeeded."
    assert quota.is_available("groq") is False


def test_orchestrator_falls_back_after_connection_error():
    service, health, _ = create_service(
        {
            "groq": result(
                "groq",
                False,
                "Groq connection failed.",
                "connection_error",
            ),
            "fallback": result(
                "fallback",
                True,
                "Fallback succeeded.",
            ),
        }
    )

    response = service.run("Analyse EduNova.")

    assert response.success is True
    assert response.agent == "fallback"
    assert health.is_available("groq") is False


def test_orchestrator_returns_last_failure_when_all_providers_fail():
    service, _, _ = create_service(
        {
            "groq": result(
                "groq",
                False,
                "Groq rate limit reached.",
                "rate_limit",
            ),
            "fallback": result(
                "fallback",
                False,
                "Fallback connection failed.",
                "connection_error",
            ),
        }
    )

    response = service.run("Analyse EduNova.")

    assert response.success is False
    assert response.agent == "fallback"
    assert response.error == "connection_error"

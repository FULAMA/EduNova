from tools.edunova.agents.orchestration.factory_registry import ProviderFactoryRegistry
from tools.edunova.agents.orchestration.health import HealthTracker
from tools.edunova.agents.orchestration.quota import QuotaTracker
from tools.edunova.agents.orchestration.registry import ProviderRegistry
from tools.edunova.agents.orchestration.router import AgentRouter
from tools.edunova.agents.result import AgentResult
from tools.edunova.agents.role import AgentRole


class AgentOrchestrationService:
    def __init__(
        self,
        provider_registry: ProviderRegistry,
        factory_registry: ProviderFactoryRegistry,
        router: AgentRouter,
        health: HealthTracker | None = None,
        quota: QuotaTracker | None = None,
    ) -> None:
        self._provider_registry = provider_registry
        self._factory_registry = factory_registry
        self._router = router
        self._health = health
        self._quota = quota

    def run(self, task: str) -> AgentResult:
        if not task.strip():
            raise ValueError("Agent task cannot be empty.")

        excluded: set[str] = set()
        last_result: AgentResult | None = None

        while True:
            provider = self._router.select(excluded=excluded)
            excluded.add(provider.name)

            config = self._provider_registry.get_config(provider.name)
            factory = self._factory_registry.get(provider.name)

            try:
                adapter = factory.create(config)
            except ValueError as exc:
                last_result = AgentResult(
                    agent=provider.name,
                    role=AgentRole.BUILDER,
                    success=False,
                    message=str(exc),
                    provider=provider.name,
                    model=config.model,
                    error="configuration_error",
                )

                if self._health is not None:
                    self._health.mark_unavailable(provider.name)

                try:
                    self._router.select(excluded=excluded)
                except RuntimeError:
                    return last_result

                continue

            try:
                result = adapter.generate(provider, task)
            except Exception as exc:
                result = AgentResult(
                    agent=provider.name,
                    role=AgentRole.BUILDER,
                    success=False,
                    message=(
                        f"Provider '{provider.name}' raised an unexpected "
                        f"exception ({type(exc).__name__})."
                    ),
                    provider=provider.name,
                    model=config.model,
                    error="provider_exception",
                )

            if result.success:
                if self._health is not None:
                    self._health.mark_available(provider.name)

                return result

            last_result = result

            if result.error == "rate_limit":
                if self._quota is not None:
                    self._quota.mark_exhausted(provider.name)

            elif result.error in {
                "authentication_error",
                "connection_error",
                "timeout",
                "provider_exception",
            }:
                if self._health is not None:
                    self._health.mark_unavailable(provider.name)

            try:
                self._router.select(excluded=excluded)
            except RuntimeError:
                return last_result

from collections.abc import Collection

from tools.edunova.agents.orchestration.health import HealthTracker
from tools.edunova.agents.orchestration.quota import QuotaTracker
from tools.edunova.agents.orchestration.registry import ProviderRegistry
from tools.edunova.agents.provider import AgentProvider


class AgentRouter:
    def __init__(
        self,
        registry: ProviderRegistry,
        health: HealthTracker,
        quota: QuotaTracker,
    ) -> None:
        self._registry = registry
        self._health = health
        self._quota = quota

    def select(
        self,
        excluded: Collection[str] = (),
    ) -> AgentProvider:
        excluded_names = set(excluded)
        candidates = []

        for index, name in enumerate(self._registry.names()):
            if name in excluded_names:
                continue

            if not self._health.is_available(name):
                continue

            if not self._quota.is_available(name):
                continue

            if self._registry.has_config(name):
                config = self._registry.get_config(name)

                if not config.enabled:
                    continue

                priority = config.priority
            else:
                priority = 1

            candidates.append((priority, index, name))

        if not candidates:
            raise RuntimeError("No available provider.")

        _, _, selected_name = min(candidates)

        return self._registry.get(selected_name)

from typing import Protocol

from tools.edunova.agents.orchestration.config import ProviderConfig


class ProviderFactory(Protocol):
    def create(self, config: ProviderConfig):
        ...


class ProviderFactoryRegistry:
    def __init__(self) -> None:
        self._factories: dict[str, ProviderFactory] = {}

    def register(
        self,
        provider_name: str,
        factory: ProviderFactory,
    ) -> None:
        if not provider_name.strip():
            raise ValueError("Provider name cannot be empty.")

        if provider_name in self._factories:
            raise ValueError(
                f"Provider '{provider_name}' is already registered."
            )

        self._factories[provider_name] = factory

    def get(self, provider_name: str) -> ProviderFactory:
        return self._factories[provider_name]

    def has(self, provider_name: str) -> bool:
        return provider_name in self._factories

    def names(self) -> tuple[str, ...]:
        return tuple(self._factories)

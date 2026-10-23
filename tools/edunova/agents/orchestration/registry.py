from tools.edunova.agents.orchestration.config import ProviderConfig
from tools.edunova.agents.provider import AgentProvider


class ProviderRegistry:
    def __init__(self) -> None:
        self._providers: dict[str, AgentProvider] = {}
        self._configs: dict[str, ProviderConfig] = {}

    def register(self, provider: AgentProvider) -> None:
        if provider.name in self._providers:
            raise ValueError(
                f"Provider '{provider.name}' is already registered."
            )
        self._providers[provider.name] = provider

    def get(self, name: str) -> AgentProvider:
        return self._providers[name]

    def has(self, name: str) -> bool:
        return name in self._providers

    def names(self) -> tuple[str, ...]:
        return tuple(self._providers)

    def register_config(self, config: ProviderConfig) -> None:
        if config.name in self._configs:
            raise ValueError(
                f"Provider '{config.name}' is already registered."
            )
        self._configs[config.name] = config

    def get_config(self, name: str) -> ProviderConfig:
        return self._configs[name]

    def has_config(self, name: str) -> bool:
        return name in self._configs

    def config_names(self) -> tuple[str, ...]:
        return tuple(self._configs)

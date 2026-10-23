from tools.edunova.agents.orchestration.config import ProviderConfig
from tools.edunova.agents.orchestration.health import HealthTracker
from tools.edunova.agents.orchestration.quota import QuotaTracker
from tools.edunova.agents.orchestration.registry import ProviderRegistry
from tools.edunova.agents.orchestration.router import AgentRouter
from tools.edunova.agents.provider import AgentProvider


def test_router_selects_highest_priority_config() -> None:
    registry = ProviderRegistry()

    registry.register(AgentProvider("openrouter"))
    registry.register(AgentProvider("gemini"))
    registry.register(AgentProvider("ollama"))

    registry.register_config(
        ProviderConfig(name="openrouter", priority=3)
    )
    registry.register_config(
        ProviderConfig(name="gemini", priority=1)
    )
    registry.register_config(
        ProviderConfig(name="ollama", priority=2)
    )

    router = AgentRouter(
        registry,
        HealthTracker(),
        QuotaTracker(),
    )

    provider = router.select()

    assert provider.name == "gemini"


def test_router_ignores_disabled_config() -> None:
    registry = ProviderRegistry()

    registry.register(AgentProvider("gemini"))
    registry.register(AgentProvider("openrouter"))

    registry.register_config(
        ProviderConfig(
            name="gemini",
            enabled=False,
            priority=1,
        )
    )
    registry.register_config(
        ProviderConfig(
            name="openrouter",
            priority=2,
        )
    )

    router = AgentRouter(
        registry,
        HealthTracker(),
        QuotaTracker(),
    )

    provider = router.select()

    assert provider.name == "openrouter"

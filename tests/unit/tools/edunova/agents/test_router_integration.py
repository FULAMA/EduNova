from tools.edunova.agents.orchestration.health import HealthTracker
from tools.edunova.agents.orchestration.quota import QuotaTracker
from tools.edunova.agents.orchestration.router import AgentRouter
from tools.edunova.agents.orchestration.registry import ProviderRegistry
from tools.edunova.agents.provider import AgentProvider


def test_router_selects_provider_with_highest_priority() -> None:
    registry = ProviderRegistry()

    gemini = AgentProvider(name="gemini")
    openrouter = AgentProvider(name="openrouter")

    registry.register(gemini)
    registry.register(openrouter)

    registry.register_config(
        registry_config(
            name="gemini",
            priority=2,
        )
    )
    registry.register_config(
        registry_config(
            name="openrouter",
            priority=1,
        )
    )

    router = AgentRouter(
        registry=registry,
        health=HealthTracker(),
        quota=QuotaTracker(),
    )

    selected = router.select()

    assert selected.name == "openrouter"


def test_router_ignores_disabled_provider() -> None:
    registry = ProviderRegistry()

    gemini = AgentProvider(name="gemini")
    openrouter = AgentProvider(name="openrouter")

    registry.register(gemini)
    registry.register(openrouter)

    registry.register_config(
        registry_config(
            name="gemini",
            priority=1,
            enabled=False,
        )
    )
    registry.register_config(
        registry_config(
            name="openrouter",
            priority=2,
        )
    )

    router = AgentRouter(
        registry=registry,
        health=HealthTracker(),
        quota=QuotaTracker(),
    )

    selected = router.select()

    assert selected.name == "openrouter"


def registry_config(
    name: str,
    priority: int,
    enabled: bool = True,
):
    from tools.edunova.agents.orchestration.config import ProviderConfig

    return ProviderConfig(
        name=name,
        priority=priority,
        enabled=enabled,
    )

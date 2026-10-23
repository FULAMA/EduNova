from tools.edunova.agents.orchestration.health import HealthTracker
from tools.edunova.agents.orchestration.quota import QuotaTracker
from tools.edunova.agents.orchestration.registry import ProviderRegistry
from tools.edunova.agents.orchestration.router import AgentRouter
from tools.edunova.agents.provider import AgentProvider


def make_registry() -> ProviderRegistry:
    registry = ProviderRegistry()
    registry.register(AgentProvider("gemini"))
    registry.register(AgentProvider("openrouter"))
    registry.register(AgentProvider("local"))
    return registry


def make_router(
    registry: ProviderRegistry,
    health: HealthTracker,
    quota: QuotaTracker,
) -> AgentRouter:
    return AgentRouter(registry, health, quota)


def test_router_selects_first_available_provider() -> None:
    registry = make_registry()
    health = HealthTracker()
    quota = QuotaTracker()

    router = make_router(registry, health, quota)

    selected = router.select()

    assert selected.name == "gemini"


def test_router_skips_unavailable_provider() -> None:
    registry = make_registry()
    health = HealthTracker()
    quota = QuotaTracker()

    health.mark_unavailable("gemini")

    router = make_router(registry, health, quota)

    selected = router.select()

    assert selected.name == "openrouter"


def test_router_skips_provider_in_cooldown() -> None:
    registry = make_registry()
    health = HealthTracker()
    quota = QuotaTracker()

    health.mark_cooldown("gemini")
    health.mark_cooldown("openrouter")

    router = make_router(registry, health, quota)

    selected = router.select()

    assert selected.name == "local"


def test_router_skips_provider_with_exhausted_quota() -> None:
    registry = make_registry()
    health = HealthTracker()
    quota = QuotaTracker()

    quota.mark_exhausted("gemini")

    router = make_router(registry, health, quota)

    selected = router.select()

    assert selected.name == "openrouter"


def test_router_combines_health_and_quota() -> None:
    registry = make_registry()
    health = HealthTracker()
    quota = QuotaTracker()

    health.mark_unavailable("gemini")
    quota.mark_exhausted("openrouter")

    router = make_router(registry, health, quota)

    selected = router.select()

    assert selected.name == "local"


def test_router_raises_when_all_providers_are_unavailable() -> None:
    registry = make_registry()
    health = HealthTracker()
    quota = QuotaTracker()

    health.mark_unavailable("gemini")
    quota.mark_exhausted("openrouter")
    health.mark_unavailable("local")

    router = make_router(registry, health, quota)

    try:
        router.select()
    except RuntimeError as exc:
        assert "available" in str(exc).lower()
    else:
        raise AssertionError("Expected RuntimeError")


def test_router_uses_registry_as_source_of_truth() -> None:
    registry = make_registry()
    health = HealthTracker()
    quota = QuotaTracker()

    router = make_router(registry, health, quota)

    assert router.select() == registry.get("gemini")


def test_router_reflects_health_changes_without_recreation() -> None:
    registry = make_registry()
    health = HealthTracker()
    quota = QuotaTracker()

    router = make_router(registry, health, quota)

    assert router.select().name == "gemini"

    health.mark_unavailable("gemini")

    assert router.select().name == "openrouter"


def test_router_reflects_quota_changes_without_recreation() -> None:
    registry = make_registry()
    health = HealthTracker()
    quota = QuotaTracker()

    router = make_router(registry, health, quota)

    assert router.select().name == "gemini"

    quota.mark_exhausted("gemini")

    assert router.select().name == "openrouter"

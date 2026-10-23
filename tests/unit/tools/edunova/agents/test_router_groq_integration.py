from tools.edunova.agents.orchestration.config import ProviderConfig
from tools.edunova.agents.orchestration.health import HealthTracker
from tools.edunova.agents.orchestration.quota import QuotaTracker
from tools.edunova.agents.orchestration.registry import ProviderRegistry
from tools.edunova.agents.orchestration.router import AgentRouter
from tools.edunova.agents.providers.groq import GroqProviderFactory


class FakeClient:
    pass


class FakeClientFactory:
    def create(self, config):
        return FakeClient()


def test_router_selected_provider_can_be_built_from_config():
    registry = ProviderRegistry()

    provider = type(
        "FakeProvider",
        (),
        {"name": "groq"},
    )()

    registry.register(provider)

    registry.register_config(
        ProviderConfig(
            name="groq",
            model="openai/gpt-oss-20b",
            timeout=45,
            priority=1,
        )
    )

    router = AgentRouter(
        registry=registry,
        health=HealthTracker(),
        quota=QuotaTracker(),
    )

    selected = router.select()

    factory = GroqProviderFactory(FakeClientFactory())
    adapter = factory.create(registry.get_config(selected.name))

    assert selected.name == "groq"
    assert adapter._model == "openai/gpt-oss-20b"
    assert adapter._timeout == 45

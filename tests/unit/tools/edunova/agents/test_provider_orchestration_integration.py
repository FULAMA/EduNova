from tools.edunova.agents.orchestration.config import ProviderConfig
from tools.edunova.agents.orchestration.factory_registry import (
    ProviderFactoryRegistry,
)
from tools.edunova.agents.orchestration.health import HealthTracker
from tools.edunova.agents.orchestration.quota import QuotaTracker
from tools.edunova.agents.orchestration.registry import ProviderRegistry
from tools.edunova.agents.orchestration.router import AgentRouter
from tools.edunova.agents.providers.groq import GroqAdapter


class FakeClient:
    pass


class FakeClientFactory:
    def create(self, config):
        return FakeClient()


class FakeGroqFactory:
    def create(self, config):
        return GroqAdapter(
            client=FakeClient(),
            model=config.model,
            timeout=config.timeout,
        )


def test_selected_provider_is_resolved_through_factory_registry():
    providers = ProviderRegistry()

    provider = type(
        "FakeProvider",
        (),
        {"name": "groq"},
    )()

    providers.register(provider)

    providers.register_config(
        ProviderConfig(
            name="groq",
            model="openai/gpt-oss-20b",
            timeout=45,
            priority=1,
        )
    )

    router = AgentRouter(
        registry=providers,
        health=HealthTracker(),
        quota=QuotaTracker(),
    )

    selected = router.select()

    factories = ProviderFactoryRegistry()
    factories.register("groq", FakeGroqFactory())

    factory = factories.get(selected.name)
    adapter = factory.create(providers.get_config(selected.name))

    assert selected.name == "groq"
    assert isinstance(adapter, GroqAdapter)
    assert adapter._model == "openai/gpt-oss-20b"
    assert adapter._timeout == 45

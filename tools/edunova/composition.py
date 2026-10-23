from tools.edunova.agents.orchestration.config import ProviderConfig
from tools.edunova.agents.orchestration.factory_registry import (
    ProviderFactoryRegistry,
)
from tools.edunova.agents.orchestration.health import HealthTracker
from tools.edunova.agents.orchestration.quota import QuotaTracker
from tools.edunova.agents.orchestration.registry import ProviderRegistry
from tools.edunova.agents.orchestration.router import AgentRouter
from tools.edunova.agents.orchestration.service import (
    AgentOrchestrationService,
)
from tools.edunova.agents.provider import AgentProvider
from tools.edunova.agents.providers.groq import (
    GroqClientFactory,
    GroqProviderFactory,
)
from tools.edunova.agents.providers.openrouter import (
    OpenRouterClientFactory,
    OpenRouterProviderFactory,
)
from tools.edunova.agents.providers.qwen import (
    QwenClientFactory,
    QwenProviderFactory,
)
from tools.edunova.agents.providers.mistral import (
    MistralClientFactory,
    MistralProviderFactory,
)
from tools.edunova.bootstrap import CliBootstrap
from tools.edunova.infrastructure.process_runner import ProcessRunner


def create_agent_service() -> AgentOrchestrationService:
    provider_registry = ProviderRegistry()

    provider_registry.register(
        AgentProvider(name="groq")
    )

    provider_registry.register(
        AgentProvider(name="openrouter")
    )

    provider_registry.register(
        AgentProvider(name="qwen")
    )

    provider_registry.register(
        AgentProvider(name="mistral")
    )

    provider_registry.register_config(
        ProviderConfig(
            name="groq",
            enabled=True,
            priority=1,
            model="openai/gpt-oss-20b",
            timeout=60,
        )
    )

    provider_registry.register_config(
        ProviderConfig(
            name="openrouter",
            enabled=True,
            priority=2,
            model="openrouter/free",
            timeout=60,
        )
    )

    provider_registry.register_config(
        ProviderConfig(
            name="qwen",
            enabled=True,
            priority=3,
            model="qwen-plus",
            timeout=60,
        )
    )

    provider_registry.register_config(
        ProviderConfig(
            name="mistral",
            enabled=True,
            priority=4,
            model="mistral-small-latest",
            timeout=60,
        )
    )

    factory_registry = ProviderFactoryRegistry()

    factory_registry.register(
        "groq",
        GroqProviderFactory(
            GroqClientFactory()
        ),
    )

    factory_registry.register(
        "openrouter",
        OpenRouterProviderFactory(
            OpenRouterClientFactory()
        ),
    )

    factory_registry.register(
        "qwen",
        QwenProviderFactory(
            QwenClientFactory()
        ),
    )

    factory_registry.register(
        "mistral",
        MistralProviderFactory(
            MistralClientFactory()
        ),
    )

    health = HealthTracker()
    quota = QuotaTracker()

    router = AgentRouter(
        registry=provider_registry,
        health=health,
        quota=quota,
    )

    return AgentOrchestrationService(
        provider_registry=provider_registry,
        factory_registry=factory_registry,
        router=router,
        health=health,
        quota=quota,
    )


def create_cli_bootstrap(
    process_runner: ProcessRunner | None = None,
) -> CliBootstrap:
    return CliBootstrap(
        process_runner=process_runner,
        agent_service=create_agent_service(),
    )


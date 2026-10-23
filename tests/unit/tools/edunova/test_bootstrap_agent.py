from tools.edunova.agents.orchestration.service import (
    AgentOrchestrationService,
)
from tools.edunova.commands.agent import OrchestratedAgentCommand
from tools.edunova.bootstrap import CliBootstrap


class FakeAgentService:
    pass


def test_bootstrap_registers_orchestrated_agent_when_service_is_provided():
    service = FakeAgentService()

    bootstrap = CliBootstrap(
        agent_service=service,
    )

    assert bootstrap.registry.has("agent-orchestrated") is True

    command = bootstrap.registry.get("agent-orchestrated")

    assert isinstance(command, OrchestratedAgentCommand)
    assert command._service is service

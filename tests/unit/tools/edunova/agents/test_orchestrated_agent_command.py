from tools.edunova.agents.result import AgentResult
from tools.edunova.agents.role import AgentRole
from tools.edunova.commands.agent import OrchestratedAgentCommand
from tools.edunova.core.result import Status


class FakeOrchestrationService:
    def __init__(self, result):
        self.result = result
        self.received_task = None

    def run(self, task):
        self.received_task = task
        return self.result


def test_orchestrated_agent_command_returns_safe_on_success():
    service = FakeOrchestrationService(
        AgentResult(
            agent="groq",
            role=AgentRole.BUILDER,
            success=True,
            message="Analyse terminée.",
        )
    )

    command = OrchestratedAgentCommand(
        service=service,
        task="Analyse academic-records.",
    )

    result = command.execute()

    assert result.status == Status.SAFE
    assert result.exit_code == 0
    assert result.message == "Analyse terminée."
    assert service.received_task == "Analyse academic-records."


def test_orchestrated_agent_command_returns_fail_on_agent_failure():
    service = FakeOrchestrationService(
        AgentResult(
            agent="groq",
            role=AgentRole.BUILDER,
            success=False,
            message="Provider unavailable.",
        )
    )

    command = OrchestratedAgentCommand(
        service=service,
        task="Analyse academic-records.",
    )

    result = command.execute()

    assert result.status == Status.FAIL
    assert result.exit_code == 1
    assert result.message == "Provider unavailable."


def test_orchestrated_agent_command_rejects_empty_task():
    service = FakeOrchestrationService(
        AgentResult(
            agent="groq",
            role=AgentRole.BUILDER,
            success=True,
            message="Should not run.",
        )
    )

    command = OrchestratedAgentCommand(
        service=service,
        task="   ",
    )

    result = command.execute()

    assert result.status == Status.FAIL
    assert result.exit_code == 1
    assert "empty" in result.message.lower()
    assert service.received_task is None

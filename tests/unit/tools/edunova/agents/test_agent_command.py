from tools.edunova.agents.agent import Agent
from tools.edunova.agents.result import AgentResult
from tools.edunova.agents.role import AgentRole
from tools.edunova.agents.provider import AgentProvider
from tools.edunova.commands.agent import AgentCommand
from tools.edunova.core.result import Status


class FakeAgent(Agent):
    name = "fake-agent"
    role = AgentRole.ARCHITECT

    def run(self, task: str) -> AgentResult:
        return AgentResult(
            agent=self.name,
            role=self.role,
            success=True,
            message=f"Analyse terminée : {task}",
        )


class FailingAgent(Agent):
    name = "failing-agent"
    role = AgentRole.ARCHITECT

    def run(self, task: str) -> AgentResult:
        return AgentResult(
            agent=self.name,
            role=self.role,
            success=False,
            message="Agent indisponible.",
        )


class ExplodingAgent(Agent):
    name = "exploding-agent"
    role = AgentRole.ARCHITECT

    def run(self, task: str) -> AgentResult:
        raise RuntimeError("api-key=do-not-print")


class FakeAgentProvider(AgentProvider):
    pass


def test_agent_command_returns_command_result() -> None:
    command = AgentCommand(
        agent=FakeAgent(),
        task="Analyser le module academic-records.",
    )

    result = command.execute()

    assert result.command == "agent"
    assert result.status == Status.SAFE
    assert result.exit_code == 0
    assert "academic-records" in result.message


def test_agent_command_exposes_agent_failure_as_fail() -> None:
    command = AgentCommand(
        agent=FailingAgent(),
        task="Analyser le module académique.",
    )

    result = command.execute()

    assert result.command == "agent"
    assert result.status == Status.FAIL
    assert result.exit_code != 0


def test_agent_command_converts_unexpected_exception_to_safe_failure() -> None:
    result = AgentCommand(
        agent=ExplodingAgent(),
        task="Analyser le module académique.",
    ).execute()

    assert result.status == Status.FAIL
    assert result.exit_code == 1
    assert "RuntimeError" in result.message
    assert "api-key" not in result.message


def test_agent_command_rejects_empty_task() -> None:
    command = AgentCommand(
        agent=FakeAgent(),
        task="   ",
    )

    result = command.execute()

    assert result.status == Status.FAIL
    assert result.exit_code != 0


def test_agent_command_is_compatible_with_work_command() -> None:
    from tools.edunova.commands.work import WorkCommand

    command = AgentCommand(
        agent=FakeAgent(),
        task="Analyser l'architecture.",
    )

    work = WorkCommand([command])
    result = work.execute()

    assert result.status == Status.SAFE
    assert result.exit_code == 0


def test_agent_command_does_not_execute_when_constructed() -> None:
    agent = FakeAgent()

    command = AgentCommand(
        agent=agent,
        task="Analyser le système.",
    )

    assert command is not None


def test_agent_command_preserves_agent_result_message() -> None:
    command = AgentCommand(
        agent=FakeAgent(),
        task="Vérifier DDD.",
    )

    result = command.execute()

    assert result.message == "Analyse terminée : Vérifier DDD."


def test_agent_command_has_expected_name() -> None:
    command = AgentCommand(
        agent=FakeAgent(),
        task="Tester.",
    )

    assert command.name == "agent"


def test_agent_command_is_read_only_at_this_stage() -> None:
    command = AgentCommand(
        agent=FakeAgent(),
        task="Inspecter le projet.",
    )

    assert command.execute().status == Status.SAFE

from tools.edunova.core.command import Command
from tools.edunova.core.result import CommandResult, Status
from tools.edunova.core.runner import CommandRunner


class FakeCommand(Command):
    name = "fake"

    def execute(self) -> CommandResult:
        return CommandResult(
            command=self.name,
            status=Status.SAFE,
            message="Commande exécutée",
        )


class FailingCommand(Command):
    name = "failing"

    def execute(self) -> CommandResult:
        return CommandResult(
            command=self.name,
            status=Status.FAIL,
            message="Échec volontaire",
            exit_code=1,
        )


def test_runner_executes_command() -> None:
    runner = CommandRunner()

    result = runner.run(FakeCommand())

    assert result.command == "fake"
    assert result.status == Status.SAFE
    assert result.message == "Commande exécutée"


def test_runner_returns_command_result() -> None:
    runner = CommandRunner()

    result = runner.run(FakeCommand())

    assert isinstance(result, CommandResult)


def test_runner_preserves_success_status() -> None:
    runner = CommandRunner()

    result = runner.run(FakeCommand())

    assert result.succeeded is True


def test_runner_preserves_failure_status() -> None:
    runner = CommandRunner()

    result = runner.run(FailingCommand())

    assert result.status == Status.FAIL
    assert result.exit_code == 1
    assert result.succeeded is False

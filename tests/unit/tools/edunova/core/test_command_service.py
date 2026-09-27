import pytest

from tools.edunova.core.command import Command
from tools.edunova.core.command_registry import CommandRegistry
from tools.edunova.core.command_service import CommandService
from tools.edunova.core.result import CommandResult, Status
from tools.edunova.core.runner import CommandRunner


class FakeCommand(Command):
    name = "fake"

    def execute(self) -> CommandResult:
        return CommandResult(
            command=self.name,
            status=Status.SAFE,
            message="Commande executee",
        )


class FailingCommand(Command):
    name = "failing"

    def execute(self) -> CommandResult:
        return CommandResult(
            command=self.name,
            status=Status.FAIL,
            message="Echec volontaire",
            exit_code=1,
        )


def create_service() -> tuple[CommandService, CommandRegistry]:
    registry = CommandRegistry()
    runner = CommandRunner()

    service = CommandService(
        registry=registry,
        runner=runner,
    )

    return service, registry


def test_service_executes_command_by_name() -> None:
    service, registry = create_service()
    registry.register(FakeCommand())

    result = service.execute("fake")

    assert result.command == "fake"
    assert result.status == Status.SAFE


def test_service_returns_command_result() -> None:
    service, registry = create_service()
    registry.register(FakeCommand())

    result = service.execute("fake")

    assert isinstance(result, CommandResult)


def test_service_propagates_command_failure() -> None:
    service, registry = create_service()
    registry.register(FailingCommand())

    result = service.execute("failing")

    assert result.status == Status.FAIL
    assert result.exit_code == 1
    assert result.succeeded is False


def test_service_rejects_unknown_command() -> None:
    service, _ = create_service()

    with pytest.raises(KeyError):
        service.execute("unknown")

def test_service_raises_clear_error_for_unknown_command() -> None:
    registry = CommandRegistry()
    runner = CommandRunner()
    service = CommandService(
        registry=registry,
        runner=runner,
    )

    with pytest.raises(
        KeyError,
        match="Unknown command: missing",
    ):
        service.execute("missing")

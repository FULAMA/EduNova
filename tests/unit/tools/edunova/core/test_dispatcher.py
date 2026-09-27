import pytest

from tools.edunova.core.command_registry import CommandRegistry
from tools.edunova.core.command_service import CommandService
from tools.edunova.core.dispatcher import CommandDispatcher
from tools.edunova.core.result import CommandResult, Status
from tools.edunova.core.runner import CommandRunner


class FakeService(CommandService):
    def __init__(self) -> None:
        self.executed_commands: list[str] = []

    def execute(self, name: str) -> CommandResult:
        self.executed_commands.append(name)

        return CommandResult(
            command=name,
            status=Status.SAFE,
            message="ok",
        )


def test_dispatcher_executes_command() -> None:
    service = FakeService()
    dispatcher = CommandDispatcher(service)

    result = dispatcher.dispatch("run_tests")

    assert service.executed_commands == ["run_tests"]
    assert result.command == "run_tests"
    assert result.status == Status.SAFE


def test_dispatcher_propagates_unknown_command_error() -> None:
    registry = CommandRegistry()
    service = CommandService(
        registry=registry,
        runner=CommandRunner(),
    )
    dispatcher = CommandDispatcher(service)

    with pytest.raises(
        KeyError,
        match="Unknown command: missing",
    ):
        dispatcher.dispatch("missing")

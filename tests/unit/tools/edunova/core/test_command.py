import pytest

from tools.edunova.core.command import Command
from tools.edunova.core.result import CommandResult, Status


class ConcreteCommand(Command):
    name = "concrete"

    def execute(self) -> CommandResult:
        return CommandResult(
            command=self.name,
            status=Status.SAFE,
            message="ok",
        )


def test_command_bind_returns_same_instance() -> None:
    command = ConcreteCommand()

    bound = command.bind(["--example", "value"])

    assert bound is command


def test_command_execute_returns_command_result() -> None:
    command = ConcreteCommand()

    result = command.execute()

    assert isinstance(result, CommandResult)
    assert result.command == "concrete"
    assert result.status == Status.SAFE


def test_command_requires_execute_implementation() -> None:
    class IncompleteCommand(Command):
        name = "incomplete"

    with pytest.raises(TypeError):
        IncompleteCommand()

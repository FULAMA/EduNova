from dataclasses import dataclass

import pytest

from tools.edunova.core.command import Command
from tools.edunova.core.command_registry import CommandRegistry
from tools.edunova.core.result import CommandResult, Status


@dataclass
class FakeCommand(Command):
    name: str = "fake"

    def execute(self) -> CommandResult:
        return CommandResult(
            command=self.name,
            status=Status.SAFE,
            message="ok",
        )


def test_registry_registers_command() -> None:
    registry = CommandRegistry()
    command = FakeCommand()

    registry.register(command)

    assert registry.has("fake")


def test_registry_returns_registered_command() -> None:
    registry = CommandRegistry()
    command = FakeCommand()

    registry.register(command)

    assert registry.get("fake") is command


def test_registry_raises_for_duplicate_command() -> None:
    registry = CommandRegistry()

    registry.register(FakeCommand())

    with pytest.raises(
        ValueError,
        match="Command already registered: fake",
    ):
        registry.register(FakeCommand())


def test_registry_can_register_multiple_commands() -> None:
    registry = CommandRegistry()

    first = FakeCommand("first")
    second = FakeCommand("second")

    registry.register(first)
    registry.register(second)

    assert registry.get("first") is first
    assert registry.get("second") is second


def test_registry_returns_registered_command_names() -> None:
    registry = CommandRegistry()

    registry.register(FakeCommand("alpha"))
    registry.register(FakeCommand("beta"))

    assert registry.names() == ("alpha", "beta")


def test_registry_raises_clear_error_for_unknown_command() -> None:
    registry = CommandRegistry()

    with pytest.raises(
        KeyError,
        match="Unknown command: missing",
    ):
        registry.get("missing")

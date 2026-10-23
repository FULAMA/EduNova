import pytest

from tools.edunova.core.command import Command
from tools.edunova.core.command_registry import CommandRegistry
from tools.edunova.core.command_service import CommandService
from tools.edunova.core.result import CommandResult, Status
from tools.edunova.core.runner import CommandRunner
from tools.edunova.extensions.fulama_workflow import FulamaWorkflow


class FakeCommand(Command):
    def __init__(
        self,
        name: str,
        status: Status,
        calls: list[str],
    ) -> None:
        self.name = name
        self._status = status
        self._calls = calls

    def execute(self) -> CommandResult:
        self._calls.append(self.name)
        return CommandResult(
            command=self.name,
            status=self._status,
            message=f"{self.name} completed",
            exit_code=1 if self._status is Status.FAIL else 0,
        )


def test_fulama_workflow_can_register_and_dispatch_in_an_existing_cli() -> None:
    calls: list[str] = []
    registry = CommandRegistry()
    workflow = FulamaWorkflow.register(
        registry,
        [
            FakeCommand("inspect", Status.SAFE, calls),
            FakeCommand("verify", Status.SAFE, calls),
        ],
    )
    dispatcher = CommandService(registry, CommandRunner())

    result = dispatcher.execute(workflow.name)

    assert registry.get("fulama-workflow") is workflow
    assert calls == ["inspect", "verify"]
    assert result.command == "fulama-workflow"
    assert result.status is Status.SAFE
    assert result.exit_code == 0


def test_fulama_workflow_stops_after_a_failed_step() -> None:
    calls: list[str] = []
    workflow = FulamaWorkflow(
        [
            FakeCommand("inspect", Status.SAFE, calls),
            FakeCommand("verify", Status.FAIL, calls),
            FakeCommand("publish", Status.SAFE, calls),
        ]
    )

    result = workflow.execute()

    assert calls == ["inspect", "verify"]
    assert result.status is Status.FAIL
    assert result.exit_code != 0


def test_fulama_workflow_rejects_empty_steps() -> None:
    with pytest.raises(ValueError, match="at least one step"):
        FulamaWorkflow([])

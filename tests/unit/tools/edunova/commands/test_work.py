from tools.edunova.commands.work import WorkCommand
from tools.edunova.core.command import Command
from tools.edunova.core.result import CommandResult, Status


class FakeCommand(Command):
    def __init__(
        self,
        name: str,
        status: Status,
        execution_log: list[str],
    ) -> None:
        self.name = name
        self._status = status
        self._execution_log = execution_log

    def execute(self) -> CommandResult:
        self._execution_log.append(self.name)

        return CommandResult(
            command=self.name,
            status=self._status,
            message=f"Result of {self.name}",
            exit_code=1 if self._status == Status.FAIL else 0,
        )


def test_work_executes_commands_in_order() -> None:
    execution_log: list[str] = []

    work = WorkCommand(
        [
            FakeCommand("first", Status.SAFE, execution_log),
            FakeCommand("second", Status.SAFE, execution_log),
            FakeCommand("third", Status.SAFE, execution_log),
        ]
    )

    result = work.execute()

    assert execution_log == ["first", "second", "third"]
    assert result.status == Status.SAFE
    assert result.exit_code == 0


def test_work_stops_after_first_failure() -> None:
    execution_log: list[str] = []

    work = WorkCommand(
        [
            FakeCommand("first", Status.SAFE, execution_log),
            FakeCommand("second", Status.FAIL, execution_log),
            FakeCommand("third", Status.SAFE, execution_log),
        ]
    )

    result = work.execute()

    assert execution_log == ["first", "second"]
    assert result.status == Status.FAIL
    assert result.exit_code == 1


def test_work_returns_warn_when_no_command_fails() -> None:
    execution_log: list[str] = []

    work = WorkCommand(
        [
            FakeCommand("first", Status.SAFE, execution_log),
            FakeCommand("second", Status.WARN, execution_log),
        ]
    )

    result = work.execute()

    assert result.status == Status.WARN
    assert result.exit_code == 0


def test_work_returns_review_when_no_command_fails() -> None:
    execution_log: list[str] = []

    work = WorkCommand(
        [
            FakeCommand("first", Status.SAFE, execution_log),
            FakeCommand("second", Status.REVIEW, execution_log),
        ]
    )

    result = work.execute()

    assert result.status == Status.REVIEW
    assert result.exit_code == 0


def test_work_returns_safe_for_empty_workflow() -> None:
    work = WorkCommand([])

    result = work.execute()

    assert result.status == Status.SAFE
    assert result.exit_code == 0


def test_work_returns_workflow_summary() -> None:
    execution_log: list[str] = []

    work = WorkCommand(
        [
            FakeCommand("first", Status.SAFE, execution_log),
            FakeCommand("second", Status.WARN, execution_log),
        ]
    )

    result = work.execute()

    assert result.command == "work"
    assert "Workflow completed" in result.message
    assert "2 command(s)" in result.message

import subprocess

from tools.edunova.commands.run_tests import RunTestsCommand
from tools.edunova.core.result import Status
from tools.edunova.infrastructure.process_runner import ProcessRunner


class FakeProcessRunner(ProcessRunner):
    def __init__(self, result: subprocess.CompletedProcess[str]) -> None:
        self._result = result
        self.commands: list[list[str]] = []

    def run(
        self,
        command: list[str],
    ) -> subprocess.CompletedProcess[str]:
        self.commands.append(command)
        return self._result


def test_test_command_executes_pytest() -> None:
    runner = FakeProcessRunner(
        subprocess.CompletedProcess(
            args=["pytest"],
            returncode=0,
            stdout="4 passed",
            stderr="",
        )
    )

    command = RunTestsCommand(runner)

    result = command.execute()

    assert runner.commands == [["pytest"]]
    assert result.status == Status.SAFE
    assert result.exit_code == 0


def test_test_command_returns_fail_when_pytest_fails() -> None:
    runner = FakeProcessRunner(
        subprocess.CompletedProcess(
            args=["pytest"],
            returncode=1,
            stdout="",
            stderr="test failed",
        )
    )

    command = RunTestsCommand(runner)

    result = command.execute()

    assert result.status == Status.FAIL
    assert result.exit_code == 1


def test_test_command_includes_process_output() -> None:
    runner = FakeProcessRunner(
        subprocess.CompletedProcess(
            args=["pytest"],
            returncode=0,
            stdout="4 passed",
            stderr="",
        )
    )

    command = RunTestsCommand(runner)

    result = command.execute()

    assert "4 passed" in result.message

from pathlib import Path

from tools.edunova.commands.quality import QualityCommand
from tools.edunova.infrastructure.process_runner import ProcessRunner
from tools.edunova.infrastructure.tool_command import tool_command
import sys


class FakeResult:
    def __init__(
        self,
        returncode: int = 0,
        stdout: str = "",
        stderr: str = "",
    ) -> None:
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


class FakeProcessRunner(ProcessRunner):
    def __init__(self, results: list[FakeResult]) -> None:
        self.results = results
        self.commands: list[list[str]] = []
        self.working_directories: list[Path | None] = []

    def run(self, command: list[str], cwd: Path | None = None) -> FakeResult:
        self.commands.append(command)
        self.working_directories.append(cwd)
        return self.results[len(self.commands) - 1]


def expected_pytest_command() -> list[str]:
    base_temp = Path.cwd() / ".pytest-work"
    return [
        sys.executable,
        "-m",
        "pytest",
        "--basetemp",
        str(base_temp),
        "tests",
    ]


def test_quality_command_has_correct_name() -> None:
    runner = FakeProcessRunner(
        [
            FakeResult(),
            FakeResult(),
            FakeResult(),
        ]
    )

    command = QualityCommand(runner)

    assert command.name == "quality"


def test_quality_command_runs_all_quality_checks() -> None:
    runner = FakeProcessRunner(
        [
            FakeResult(),
            FakeResult(),
            FakeResult(),
        ]
    )

    command = QualityCommand(runner)

    result = command.execute()

    assert result.command == "quality"
    assert result.status.value == "SAFE"
    assert result.exit_code == 0

    assert runner.commands == [
        tool_command("ruff", ["check", "src"]),
        [sys.executable, "-m", "mypy", "src"],
        expected_pytest_command(),
    ]
    assert runner.working_directories == [Path.cwd()] * 3


def test_quality_command_stops_on_failed_check() -> None:
    runner = FakeProcessRunner(
        [
            FakeResult(
                returncode=1,
                stdout="ruff found an error",
            ),
        ]
    )

    command = QualityCommand(runner)

    result = command.execute()

    assert result.command == "quality"
    assert result.status.value == "FAIL"
    assert result.exit_code == 1
    assert result.message == "ruff found an error"

    assert runner.commands == [
        tool_command("ruff", ["check", "src"]),
    ]


def test_quality_command_uses_stderr_when_stdout_is_empty() -> None:
    runner = FakeProcessRunner(
        [
            FakeResult(
                returncode=1,
                stderr="quality tool failed",
            ),
        ]
    )

    command = QualityCommand(runner)

    result = command.execute()

    assert result.status.value == "FAIL"
    assert result.message == "quality tool failed"

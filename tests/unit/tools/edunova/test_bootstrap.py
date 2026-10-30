from pathlib import Path

from tools.edunova.bootstrap import CliBootstrap
from tools.edunova.infrastructure.process_runner import ProcessRunner
from tools.edunova.infrastructure.tool_command import tool_command
import sys


class FakeProcessRunner(ProcessRunner):
    def __init__(self) -> None:
        self.commands: list[list[str]] = []

    def run(self, command: list[str], cwd=None):
        self.commands.append(command)

        class FakeResult:
            returncode = 0
            stdout = "fake tests passed"
            stderr = ""

        return FakeResult()


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


def test_bootstrap_creates_registry() -> None:
    bootstrap = CliBootstrap()

    assert bootstrap.registry is not None


def test_bootstrap_registers_run_tests_command() -> None:
    bootstrap = CliBootstrap()

    assert bootstrap.registry.has("run_tests")


def test_bootstrap_registers_work_command() -> None:
    bootstrap = CliBootstrap()

    assert bootstrap.registry.has("work")


def test_bootstrap_registers_fulama_workflow_extension() -> None:
    bootstrap = CliBootstrap()

    assert bootstrap.registry.has("fulama-workflow")


def test_bootstrap_registers_unified_diagnostic() -> None:
    bootstrap = CliBootstrap()

    assert bootstrap.registry.has("diagnose")


def test_bootstrap_creates_command_service() -> None:
    bootstrap = CliBootstrap()

    assert bootstrap.service is not None


def test_bootstrap_uses_command_runner() -> None:
    bootstrap = CliBootstrap()

    assert bootstrap.runner is not None


def test_bootstrap_creates_command_dispatcher() -> None:
    bootstrap = CliBootstrap()

    assert bootstrap.dispatcher is not None


def test_bootstrap_dispatcher_can_execute_run_tests() -> None:
    process_runner = FakeProcessRunner()
    bootstrap = CliBootstrap(process_runner=process_runner)

    result = bootstrap.dispatcher.dispatch("run_tests")

    assert result.command == "run_tests"
    assert process_runner.commands == [expected_pytest_command()]


def test_bootstrap_work_runs_quality_then_security() -> None:
    process_runner = FakeProcessRunner()
    bootstrap = CliBootstrap(process_runner=process_runner)

    result = bootstrap.dispatcher.dispatch("work")

    assert result.command == "work"
    assert result.status.value == "SAFE"
    assert process_runner.commands == [
        tool_command("ruff", ["check", "src"]),
        [sys.executable, "-m", "mypy", "src"],
        expected_pytest_command(),
        tool_command("bandit", ["-r", "src", "tools", "-ll"]),
    ]


def test_bootstrap_accepts_process_runner() -> None:
    process_runner = ProcessRunner()

    bootstrap = CliBootstrap(process_runner=process_runner)

    assert bootstrap is not None


def test_bootstrap_uses_injected_process_runner() -> None:
    process_runner = FakeProcessRunner()
    bootstrap = CliBootstrap(process_runner=process_runner)

    result = bootstrap.dispatcher.dispatch("run_tests")

    assert process_runner.commands == [expected_pytest_command()]
    assert result.status.value == "SAFE"

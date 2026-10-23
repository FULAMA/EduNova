from pathlib import Path

from tools.edunova.__main__ import main as module_main
from tools.edunova.cli import main
from tools.edunova.infrastructure.process_runner import ProcessRunner
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


def test_cli_main_returns_zero_for_run_tests() -> None:
    process_runner = FakeProcessRunner()

    exit_code = main(
        ["run_tests"],
        process_runner=process_runner,
    )

    assert exit_code == 0


def test_module_entrypoint_forwards_arguments_to_cli() -> None:
    process_runner = FakeProcessRunner()

    exit_code = module_main(
        ["run_tests"],
        process_runner=process_runner,
    )

    assert exit_code == 0
    assert process_runner.commands == [expected_pytest_command()]


def test_cli_main_without_arguments_prints_help(
    capsys,
) -> None:
    exit_code = main([])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "EduNova CLI" in captured.out
    assert "edunova <command> [arguments]" in captured.out
    assert "run_tests" in captured.out
    assert "quality" in captured.out
    assert "fulama-workflow" in captured.out


def test_cli_main_help_option_prints_help(
    capsys,
) -> None:
    exit_code = main(["--help"])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "EduNova CLI" in captured.out
    assert "Usage:" in captured.out


def test_cli_command_help_does_not_execute_workflow(capsys) -> None:
    class FailingRunner:
        def run(self, *args, **kwargs):
            raise AssertionError("command runner must not be called for help")

    exit_code = main(["work", "--help"], process_runner=FailingRunner())
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Usage: edunova work" in captured.out


def test_cli_reports_missing_executable_without_traceback(
    capsys,
) -> None:
    class MissingExecutableRunner(FakeProcessRunner):
        def run(self, command: list[str], cwd=None):
            raise FileNotFoundError(2, "tool unavailable", command[0])

    exit_code = main(
        ["run_tests"],
        process_runner=MissingExecutableRunner(),
    )

    captured = capsys.readouterr()

    assert exit_code == 127
    assert "was not found" in captured.out
    assert "Traceback" not in captured.out


def test_cli_reports_value_error_without_traceback(
    capsys,
) -> None:
    class InvalidCommandRunner(FakeProcessRunner):
        def run(self, command: list[str], cwd=None):
            raise ValueError("invalid invocation")

    exit_code = main(
        ["run_tests"],
        process_runner=InvalidCommandRunner(),
    )

    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Command could not run: invalid invocation" in captured.out
    assert "Traceback" not in captured.out


def test_cli_reports_unexpected_error_without_details(
    capsys,
) -> None:
    class UnexpectedRunner(FakeProcessRunner):
        def run(self, command: list[str], cwd=None):
            raise RuntimeError("secret-token=do-not-print")

    exit_code = main(
        ["run_tests"],
        process_runner=UnexpectedRunner(),
    )

    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Command failed unexpectedly (RuntimeError)." in captured.out
    assert "secret-token" not in captured.out
    assert "Traceback" not in captured.out


def test_cli_redacts_secret_from_process_stdout(capsys) -> None:
    class LeakingRunner(FakeProcessRunner):
        def run(self, command: list[str], cwd=None):
            class FakeResult:
                returncode = 1
                stdout = "pytest failed: Bearer stdout-secret-token"
                stderr = ""

            return FakeResult()

    exit_code = main(["run_tests"], process_runner=LeakingRunner())
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "stdout-secret-token" not in captured.out
    assert "[REDACTED]" in captured.out


def test_cli_redacts_secret_from_process_stderr(capsys) -> None:
    class LeakingRunner(FakeProcessRunner):
        def run(self, command: list[str], cwd=None):
            class FakeResult:
                returncode = 1
                stdout = ""
                stderr = "pytest failed: password=stderr-secret-value"

            return FakeResult()

    exit_code = main(["run_tests"], process_runner=LeakingRunner())
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "stderr-secret-value" not in captured.out
    assert "[REDACTED]" in captured.out


def test_cli_reports_invalid_project_configuration(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[tool.edunova]\nunknown_option = true\n',
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)

    exit_code = main(["--help"])
    captured = capsys.readouterr()

    assert exit_code == 2
    assert "Invalid [tool.edunova] configuration" in captured.out
    assert "unknown_option" in captured.out


def test_cli_reports_interruption_with_shell_exit_code(
    capsys,
) -> None:
    class InterruptedRunner(FakeProcessRunner):
        def run(self, command: list[str], cwd=None):
            raise KeyboardInterrupt

    exit_code = main(
        ["run_tests"],
        process_runner=InterruptedRunner(),
    )

    captured = capsys.readouterr()

    assert exit_code == 130
    assert "Command interrupted." in captured.out


def test_cli_main_short_help_option_prints_help(
    capsys,
) -> None:
    exit_code = main(["-h"])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "EduNova CLI" in captured.out
    assert "Commands:" in captured.out


def test_cli_main_unknown_command_returns_clean_error(
    capsys,
) -> None:
    exit_code = main(["commande_inexistante"])

    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Unknown command: commande_inexistante" in captured.out
    assert "Use --help to list available commands." in captured.out


def test_cli_diagnose_prints_step_statuses_and_returns_summary_code(
    capsys,
) -> None:
    class DiagnosticRunner(FakeProcessRunner):
        def run(self, command: list[str], cwd=None):
            self.commands.append(command)

            class FakeResult:
                returncode = 0
                stdout = "" if command[0] == "git" else "passed"
                stderr = ""

            return FakeResult()

    runner = DiagnosticRunner()
    exit_code = main(["diagnose"], process_runner=runner)

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Tests: SUCCEEDED" in captured.out
    assert "Quality (Ruff + Mypy): SUCCEEDED" in captured.out
    assert "Bandit security scan: SUCCEEDED" in captured.out
    assert "Git working tree: SUCCEEDED" in captured.out
    assert "Overall: SUCCEEDED" in captured.out


def test_module_entrypoint_agent_without_task_returns_clean_error(
    monkeypatch,
    capsys,
) -> None:
    def fail_if_service_created():
        raise AssertionError(
            "The agent service must not be created without a task."
        )

    monkeypatch.setitem(
        module_main.__globals__,
        "_create_agent_service",
        fail_if_service_created,
    )

    exit_code = module_main(["agent"])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Agent task is required." in captured.out
    assert "Traceback" not in captured.out


def test_module_entrypoint_orchestrated_agent_without_task_returns_clean_error(
    monkeypatch,
    capsys,
) -> None:
    def fail_if_service_created():
        raise AssertionError(
            "The agent service must not be created without a task."
        )

    monkeypatch.setitem(
        module_main.__globals__,
        "_create_agent_service",
        fail_if_service_created,
    )

    exit_code = module_main(["agent-orchestrated"])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Agent task is required." in captured.out
    assert "Traceback" not in captured.out


def test_module_entrypoint_reports_missing_agent_dependencies(
    monkeypatch,
    capsys,
) -> None:
    def fail_if_service_created():
        raise ImportError("provider SDK unavailable")

    monkeypatch.setitem(
        module_main.__globals__,
        "_create_agent_service",
        fail_if_service_created,
    )

    exit_code = module_main(["agent", "review this change"])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "optional 'agents' dependencies" in captured.out
    assert "Traceback" not in captured.out

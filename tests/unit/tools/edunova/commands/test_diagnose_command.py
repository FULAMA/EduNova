from pathlib import Path
import subprocess

import pytest

from tools.edunova.commands.diagnose import (
    DiagnoseCommand,
)
from tools.edunova.core.command import Command
from tools.edunova.core.result import CommandResult, Status
from tools.edunova.infrastructure.process_runner import ProcessRunner
from tools.edunova.project_config import ProjectConfig


class FakeProcessRunner(ProcessRunner):
    def __init__(self, returncodes: dict[str, int] | None = None) -> None:
        self.returncodes = returncodes or {}
        self.commands: list[list[str]] = []

    def run(self, command, cwd=None):
        self.commands.append(list(command))
        if command[0] == "git":
            return subprocess.CompletedProcess(
                command,
                self.returncodes.get("git", 0),
                stdout=" M src/example.py\n?? notes.txt\n",
                stderr="git unavailable" if self.returncodes.get("git") else "",
            )
        name = Path(command[0]).name
        if name.startswith("ruff"):
            key = "ruff"
        elif name.startswith("bandit"):
            key = "bandit"
        elif "pytest" in command:
            key = "pytest"
        elif "mypy" in command:
            key = "mypy"
        else:
            key = name
        code = self.returncodes.get(key, 0)
        return subprocess.CompletedProcess(
            command,
            code,
            stdout=f"{key} output" if code else f"{key} passed",
            stderr="",
        )


def make_project(root: Path) -> ProjectConfig:
    (root / "src").mkdir(exist_ok=True)
    (root / "tests").mkdir(exist_ok=True)
    return ProjectConfig(project_root=root)


def test_diagnose_runs_existing_checks_once_and_reports_git_status(
    tmp_path: Path,
) -> None:
    runner = FakeProcessRunner()
    command = DiagnoseCommand(runner, make_project(tmp_path))

    result = command.execute()

    assert result.status is Status.SAFE
    assert result.exit_code == 0
    assert "Tests: SUCCEEDED (exit 0)" in result.message
    assert "Quality (Ruff + Mypy): SUCCEEDED" in result.message
    assert "Bandit security scan: SUCCEEDED" in result.message
    assert "2 changed path(s)" in result.message
    assert "  M src/example.py" in result.message
    assert "  ?? notes.txt" in result.message
    assert sum("pytest" in call for call in runner.commands) == 1
    assert runner.commands[-1] == [
        "git",
        "status",
        "--short",
        "--untracked-files=all",
    ]


def test_diagnose_preserves_all_failed_stage_codes_and_continues(
    tmp_path: Path,
) -> None:
    runner = FakeProcessRunner({"pytest": 4, "ruff": 3, "bandit": 5})
    result = DiagnoseCommand(runner, make_project(tmp_path)).execute()

    assert result.status is Status.FAIL
    assert result.exit_code == 4
    assert "Tests: FAILED (exit 4)" in result.message
    assert "Quality (Ruff + Mypy): FAILED (exit 3)" in result.message
    assert "Bandit security scan: FAILED (exit 5)" in result.message
    assert "Overall: FAILED (exit 4)" in result.message
    assert any("git" in call[0] for call in runner.commands)


def test_invalid_test_path_is_a_failed_stage_without_hiding_other_checks(
    tmp_path: Path,
) -> None:
    (tmp_path / "src").mkdir()
    runner = FakeProcessRunner()
    config = ProjectConfig(project_root=tmp_path, test_paths=("missing",))

    result = DiagnoseCommand(runner, config).execute()

    assert result.status is Status.FAIL
    assert "Tests: FAILED (exit 2)" in result.message
    assert "Configured test path does not exist: missing" in result.message
    assert "Quality (Ruff + Mypy): SUCCEEDED" in result.message
    assert "Bandit security scan: SUCCEEDED" in result.message


def test_missing_cli_tool_is_reported_and_later_steps_still_run(
    tmp_path: Path,
) -> None:
    class MissingRuffRunner(FakeProcessRunner):
        def run(self, command, cwd=None):
            if Path(command[0]).name.startswith("ruff"):
                raise FileNotFoundError(2, "not found", command[0])
            return super().run(command, cwd)

    runner = MissingRuffRunner()
    result = DiagnoseCommand(runner, make_project(tmp_path)).execute()

    assert result.exit_code == 127
    assert "Quality (Ruff + Mypy): FAILED (exit 127)" in result.message
    assert "Required executable was not found" in result.message
    assert "Bandit security scan: SUCCEEDED" in result.message


def test_quality_timeout_is_reported_and_later_steps_still_run(
    tmp_path: Path,
) -> None:
    class TimedOutRuffRunner(FakeProcessRunner):
        def run(self, command, cwd=None):
            if Path(command[0]).name.startswith("ruff"):
                raise subprocess.TimeoutExpired(command, timeout=15)
            return super().run(command, cwd)

    result = DiagnoseCommand(
        TimedOutRuffRunner(), make_project(tmp_path)
    ).execute()

    assert result.exit_code == 124
    assert "Quality (Ruff + Mypy): FAILED (exit 124)" in result.message
    assert "Timed out:" in result.message
    assert "Bandit security scan: SUCCEEDED" in result.message


def test_git_unavailable_requires_review_and_produces_nonzero_exit(
    tmp_path: Path,
) -> None:
    runner = FakeProcessRunner({"git": 128})
    result = DiagnoseCommand(runner, make_project(tmp_path)).execute()

    assert result.status is Status.REVIEW
    assert result.exit_code == 2
    assert "Git working tree: REVIEW REQUIRED (exit 128)" in result.message
    assert "Overall: REVIEW REQUIRED (exit 2)" in result.message


def test_missing_git_executable_requires_review_without_claiming_a_snapshot(
    tmp_path: Path,
) -> None:
    class MissingGitRunner(FakeProcessRunner):
        def run(self, command, cwd=None):
            if command[0] == "git":
                raise FileNotFoundError(2, "not found", "git")
            return super().run(command, cwd)

    result = DiagnoseCommand(
        MissingGitRunner(), make_project(tmp_path)
    ).execute()

    assert result.status is Status.REVIEW
    assert result.exit_code == 2
    assert "Git working tree: REVIEW REQUIRED (exit 127)" in result.message
    assert "Git summary unavailable" in result.message


def test_interrupt_marks_remaining_stages_skipped() -> None:
    class InterruptingCommand(Command):
        name = "interrupt"

        def execute(self) -> CommandResult:
            raise KeyboardInterrupt

    class MustNotRunCommand(Command):
        name = "must-not-run"

        def execute(self) -> CommandResult:
            raise AssertionError("Skipped command was executed")

    command = DiagnoseCommand(
        ProcessRunner(),
        ProjectConfig(project_root=Path.cwd()),
        commands=(
            ("Tests", InterruptingCommand()),
            ("Quality", MustNotRunCommand()),
        ),
    )

    result = command.execute()

    assert result.exit_code == 130
    assert "Tests: FAILED (exit 130)" in result.message
    assert "Quality: SKIPPED (exit 130)" in result.message
    assert "Overall: FAILED (exit 130)" in result.message


@pytest.mark.parametrize("code", [1, 2, 127])
def test_diagnostic_nonzero_child_exit_is_never_reported_as_success(
    tmp_path: Path,
    code: int,
) -> None:
    runner = FakeProcessRunner({"pytest": code})
    result = DiagnoseCommand(runner, make_project(tmp_path)).execute()

    assert result.status is Status.FAIL
    assert result.exit_code == code
    assert f"Tests: FAILED (exit {code})" in result.message

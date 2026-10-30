from pathlib import Path

import pytest

from tools.edunova.agents.context_scanner import ContextScanner
from tools.edunova.infrastructure.process_runner import ProcessRunner


class FakeProcessRunner(ProcessRunner):
    def __init__(self, responses: dict[tuple[str, ...], object]) -> None:
        self.responses = responses
        self.commands: list[tuple[str, ...]] = []
        self.working_directories: list[Path | None] = []

    def run(self, command, cwd=None):
        normalized = tuple(command)
        self.commands.append(normalized)
        self.working_directories.append(cwd)
        return self.responses[normalized]


class FakeCompletedProcess:
    def __init__(
        self,
        returncode: int,
        stdout: str = "",
        stderr: str = "",
    ) -> None:
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def test_scanner_collects_git_branch() -> None:
    runner = FakeProcessRunner(
        {
            ("git", "branch", "--show-current"): FakeCompletedProcess(
                0,
                stdout="main\n",
            ),
            ("git", "status", "--short"): FakeCompletedProcess(
                0,
                stdout="",
            ),
        }
    )

    scanner = ContextScanner(
        project_root=Path.cwd(),
        scope="academic-records",
        process_runner=runner,
    )

    context = scanner.scan()

    assert context.git_branch == "main"


def test_scanner_collects_git_status() -> None:
    runner = FakeProcessRunner(
        {
            ("git", "branch", "--show-current"): FakeCompletedProcess(
                0,
                stdout="main\n",
            ),
            ("git", "status", "--short"): FakeCompletedProcess(
                0,
                stdout=" M src/example.py\n?? new_file.py\n",
            ),
        }
    )

    scanner = ContextScanner(
        project_root=Path.cwd(),
        scope="academic-records",
        process_runner=runner,
    )

    context = scanner.scan()

    assert context.git_status == (
        " M src/example.py",
        "?? new_file.py",
    )


def test_scanner_extracts_changed_files() -> None:
    runner = FakeProcessRunner(
        {
            ("git", "branch", "--show-current"): FakeCompletedProcess(
                0,
                stdout="main\n",
            ),
            ("git", "status", "--short"): FakeCompletedProcess(
                0,
                stdout=(
                    " M src/example.py\n"
                    "A  src/new.py\n"
                    "?? frontend/\n"
                ),
            ),
        }
    )

    scanner = ContextScanner(
        project_root=Path.cwd(),
        scope="academic-records",
        process_runner=runner,
    )

    context = scanner.scan()

    assert context.changed_files == (
        "src/example.py",
        "src/new.py",
        "frontend/",
    )


def test_scanner_uses_project_root_for_git_commands() -> None:
    runner = FakeProcessRunner(
        {
            ("git", "branch", "--show-current"): FakeCompletedProcess(
                0,
                stdout="main\n",
            ),
            ("git", "status", "--short"): FakeCompletedProcess(
                0,
                stdout="",
            ),
        }
    )

    scanner = ContextScanner(
        project_root=Path.cwd(),
        scope="agent-kernel",
        process_runner=runner,
    )

    scanner.scan()

    assert runner.commands == [
        ("git", "branch", "--show-current"),
        ("git", "status", "--short"),
    ]
    assert runner.working_directories == [
        Path.cwd(),
        Path.cwd(),
    ]


def test_scanner_does_not_execute_destructive_git_commands() -> None:
    runner = FakeProcessRunner(
        {
            ("git", "branch", "--show-current"): FakeCompletedProcess(
                0,
                stdout="main\n",
            ),
            ("git", "status", "--short"): FakeCompletedProcess(
                0,
                stdout="",
            ),
        }
    )

    scanner = ContextScanner(
        project_root=Path.cwd(),
        scope="agent-kernel",
        process_runner=runner,
    )

    scanner.scan()

    forbidden = {
        "add",
        "commit",
        "reset",
        "restore",
        "checkout",
        "clean",
        "push",
        "pull",
        "merge",
        "rebase",
    }

    for command in runner.commands:
        assert not any(part in forbidden for part in command)


def test_scanner_reports_git_failure_as_risk() -> None:
    runner = FakeProcessRunner(
        {
            ("git", "branch", "--show-current"): FakeCompletedProcess(
                128,
                stderr="fatal: not a git repository\n",
            ),
            ("git", "status", "--short"): FakeCompletedProcess(
                128,
                stderr="fatal: not a git repository\n",
            ),
        }
    )

    scanner = ContextScanner(
        project_root=Path.cwd(),
        scope="agent-kernel",
        process_runner=runner,
    )

    context = scanner.scan()

    assert context.git_branch == ""
    assert context.git_status == ()
    assert context.changed_files == ()
    assert context.risks
    assert any("git" in risk.lower() for risk in context.risks)


def test_scanner_preserves_project_scope() -> None:
    runner = FakeProcessRunner(
        {
            ("git", "branch", "--show-current"): FakeCompletedProcess(
                0,
                stdout="main\n",
            ),
            ("git", "status", "--short"): FakeCompletedProcess(
                0,
                stdout="",
            ),
        }
    )

    scanner = ContextScanner(
        project_root=Path.cwd(),
        scope="academic-records",
        process_runner=runner,
    )

    context = scanner.scan()

    assert context.project_root == Path.cwd()
    assert context.scope == "academic-records"

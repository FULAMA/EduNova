from pathlib import Path

from tools.edunova.agents.context_scanner import ContextScanner
from tools.edunova.infrastructure.process_runner import ProcessRunner


class FakeProcessRunner(ProcessRunner):
    def __init__(self, responses: dict[tuple[str, ...], object]) -> None:
        self.responses = responses

    def run(self, command, cwd=None):
        return self.responses[tuple(command)]


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


def make_runner() -> FakeProcessRunner:
    return FakeProcessRunner(
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


def test_scanner_discovers_architecture_areas() -> None:
    scanner = ContextScanner(
        project_root=Path.cwd(),
        scope="agent-kernel",
        process_runner=make_runner(),
    )

    context = scanner.scan()

    assert "src/academic" in context.architecture
    assert "src/identity" in context.architecture
    assert "src/tenancy" in context.architecture
    assert "src/infrastructure" in context.architecture
    assert "src/presentation" in context.architecture
    assert "tools/edunova/agents" in context.architecture


def test_scanner_discovers_test_areas() -> None:
    scanner = ContextScanner(
        project_root=Path.cwd(),
        scope="agent-kernel",
        process_runner=make_runner(),
    )

    context = scanner.scan()

    assert "tests/unit" in context.tests
    assert "tests/integration" in context.tests


def test_scanner_excludes_python_cache_directories() -> None:
    scanner = ContextScanner(
        project_root=Path.cwd(),
        scope="agent-kernel",
        process_runner=make_runner(),
    )

    context = scanner.scan()

    assert all(
        "__pycache__" not in path
        for path in context.architecture
    )
    assert all(
        "__pycache__" not in path
        for path in context.tests
    )
from tools.edunova.agents.context import GitChange  # noqa: E402


def test_parse_git_changes_preserves_status_and_path():
    result = ContextScanner._parse_git_changes(
        (
            " M src/example.py",
            "?? new_file.py",
            "A  added.py",
        )
    )

    assert result == (
        GitChange(status=" M", path="src/example.py"),
        GitChange(status="??", path="new_file.py"),
        GitChange(status="A ", path="added.py"),
    )


def test_parse_git_changes_ignores_invalid_entries():
    result = ContextScanner._parse_git_changes(
        (
            "",
            "x",
            "  ",
        )
    )

    assert result == ()

from pathlib import Path
import sys

import pytest

from tools.edunova.commands.quality import QualityCommand
from tools.edunova.commands.run_tests import RunTestsCommand
from tools.edunova.bootstrap import CliBootstrap
from tools.edunova.core.result import Status
from tools.edunova.infrastructure.process_runner import ProcessRunner
from tools.edunova.infrastructure.tool_command import tool_command
from tools.edunova.project_config import ProjectConfig, ProjectConfigError


class FakeResult:
    def __init__(self, returncode: int = 0) -> None:
        self.returncode = returncode
        self.stdout = ""
        self.stderr = ""


class FakeProcessRunner(ProcessRunner):
    def __init__(self, returncodes: tuple[int, ...] = ()) -> None:
        self.returncodes = returncodes
        self.calls: list[tuple[list[str], Path | None]] = []

    def run(self, command, cwd=None):
        self.calls.append((list(command), cwd))
        index = len(self.calls) - 1
        return FakeResult(self.returncodes[index] if self.returncodes else 0)


def make_project(root: Path, content: str | None) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / "app").mkdir(exist_ok=True)
    (root / "checks").mkdir(exist_ok=True)
    if content is not None:
        (root / "pyproject.toml").write_text(content, encoding="utf-8")


def test_missing_config_uses_defaults(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\nname='demo'\n")
    config = ProjectConfig.load(tmp_path)

    assert config.project_root == tmp_path.resolve()
    assert config.source_paths == ("src",)
    assert config.test_paths == ("tests",)
    assert config.timeout_seconds == 600


def test_configured_paths_and_arguments_are_loaded(tmp_path: Path) -> None:
    make_project(
        tmp_path,
        """
[tool.edunova]
source_paths = ["app"]
test_paths = ["checks"]
timeout_seconds = 42

[tool.edunova.commands]
ruff_args = ["check", "--select", "E,F"]
mypy_args = ["--strict"]
pytest_args = ["-q"]
bandit_args = ["-ll", "-q"]
""",
    )

    config = ProjectConfig.load(tmp_path)

    assert config.source_paths == ("app",)
    assert config.test_paths == ("checks",)
    assert config.ruff_args == ("check", "--select", "E,F")
    assert config.mypy_args == ("--strict",)
    assert config.pytest_args == ("-q",)
    assert config.bandit_args == ("-ll", "-q")
    assert config.timeout_seconds == 42


def test_configured_audit_path_is_resolved_under_project_root(tmp_path: Path) -> None:
    make_project(
        tmp_path,
        """
[tool.edunova]
audit_path = ".state/audit.sqlite3"
""",
    )

    config = ProjectConfig.load(tmp_path)

    assert config.audit_database_path() == (
        tmp_path / ".state" / "audit.sqlite3"
    ).resolve()


@pytest.mark.parametrize("audit_path", ["C:/outside.sqlite3", "../audit.sqlite3"])
def test_audit_path_cannot_escape_project_root(
    tmp_path: Path,
    audit_path: str,
) -> None:
    make_project(
        tmp_path,
        f"[tool.edunova]\naudit_path = {audit_path!r}\n",
    )

    with pytest.raises(ProjectConfigError, match="audit_path"):
        ProjectConfig.load(tmp_path)


def test_toml_utf8_bom_is_rejected_as_invalid_toml(tmp_path: Path) -> None:
    make_project(
        tmp_path,
        '\ufeff[tool.edunova]\nsource_paths = ["app"]\n',
    )

    with pytest.raises(ProjectConfigError, match="Cannot read"):
        ProjectConfig.load(tmp_path)


def test_nested_start_directory_resolves_paths_from_project_root(
    tmp_path: Path,
) -> None:
    make_project(
        tmp_path,
        '[tool.edunova]\nsource_paths = ["app"]\ntest_paths = ["checks"]\n',
    )
    nested = tmp_path / "nested" / "working"
    nested.mkdir(parents=True)

    config = ProjectConfig.load(nested)
    runner = FakeProcessRunner()
    result = QualityCommand(runner, config).execute()

    assert result.status is Status.SAFE
    assert runner.calls[0][0] == tool_command("ruff", ["check", "app"])
    assert all(call[1] == tmp_path.resolve() for call in runner.calls)
    assert runner.calls[1][0] == [
        sys.executable,
        "-m",
        "mypy",
        "app",
    ]
    assert runner.calls[2][0][-1] == "checks"


def test_custom_tool_arguments_are_used_by_quality_and_workflow(
    tmp_path: Path,
) -> None:
    make_project(
        tmp_path,
        """
[tool.edunova]
source_paths = ["app"]
test_paths = ["checks"]

[tool.edunova.commands]
ruff_args = ["check", "--select", "E,F"]
mypy_args = ["--strict"]
pytest_args = ["-q"]
bandit_args = ["-ll"]
""",
    )
    config = ProjectConfig.load(tmp_path)
    runner = FakeProcessRunner()
    bootstrap = CliBootstrap(process_runner=runner, project_config=config)

    result = bootstrap.dispatcher.dispatch("work")

    assert result.status is Status.SAFE
    assert [call[0] for call in runner.calls] == [
        tool_command("ruff", ["check", "--select", "E,F", "app"]),
        [sys.executable, "-m", "mypy", "app", "--strict"],
        [
            sys.executable,
            "-m",
            "pytest",
            "--basetemp",
            str(tmp_path / ".pytest-work"),
            "checks",
            "-q",
        ],
        tool_command("bandit", ["-r", "app", "-ll"]),
    ]
    assert all(call[1] == tmp_path.resolve() for call in runner.calls)


def test_missing_configured_test_directory_fails_before_process_execution(
    tmp_path: Path,
) -> None:
    make_project(
        tmp_path,
        '[tool.edunova]\ntest_paths = ["missing-checks"]\n',
    )
    runner = FakeProcessRunner()

    result = RunTestsCommand(runner, ProjectConfig.load(tmp_path)).execute()

    assert result.status is Status.FAIL
    assert result.exit_code == 2
    assert "test path does not exist: missing-checks" in result.message
    assert runner.calls == []


@pytest.mark.parametrize(
    "content, expected",
    [
        ('[tool.edunova]\nsource_path = "app"\n', "Unknown"),
        ('[tool.edunova]\ntimeout_seconds = 0\n', "positive number"),
        ('[tool.edunova]\ntest_paths = ["../outside"]\n', "relative"),
        (
            '[tool.edunova.commands]\npytest_args = ["--basetemp=/tmp"]\n',
            "cannot override --basetemp",
        ),
        ('[tool.edunova]\nsource_paths = "app"\n', "list of non-empty strings"),
    ],
)
def test_invalid_configuration_is_rejected(
    tmp_path: Path,
    content: str,
    expected: str,
) -> None:
    make_project(tmp_path, content)

    with pytest.raises(ProjectConfigError, match=expected):
        ProjectConfig.load(tmp_path)


def test_invalid_toml_is_rejected(tmp_path: Path) -> None:
    make_project(tmp_path, "[tool.edunova\n")

    with pytest.raises(ProjectConfigError, match="Cannot read"):
        ProjectConfig.load(tmp_path)


def test_test_command_propagates_process_exit_code(tmp_path: Path) -> None:
    (tmp_path / "checks").mkdir()
    config = ProjectConfig(project_root=tmp_path, test_paths=("checks",))
    runner = FakeProcessRunner((7,))

    result = RunTestsCommand(runner, config).execute()

    assert result.status is Status.FAIL
    assert result.exit_code == 7
    assert runner.calls[0][1] == tmp_path

import subprocess

from tools.edunova.commands.security import SecurityCommand
from tools.edunova.core.result import Status
from tools.edunova.infrastructure.process_runner import ProcessRunner
from tools.edunova.infrastructure.tool_command import tool_command


class FakeProcessRunner(ProcessRunner):
    def __init__(self, returncode: int = 0, output: str = "") -> None:
        self.returncode = returncode
        self.output = output
        self.commands: list[list[str]] = []
        self.calls: list[tuple[list[str], object]] = []

    def run(
        self,
        command: list[str],
        cwd=None,
    ) -> subprocess.CompletedProcess[str]:
        self.commands.append(command)
        self.calls.append((command, cwd))
        return subprocess.CompletedProcess(
            args=command,
            returncode=self.returncode,
            stdout=self.output,
            stderr="",
        )


def test_security_runs_bandit_on_available_source_roots(
    tmp_path,
    monkeypatch,
) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\nname='demo'\n")
    (tmp_path / "src").mkdir()
    (tmp_path / "tools").mkdir()
    monkeypatch.chdir(tmp_path)
    runner = FakeProcessRunner()

    result = SecurityCommand(runner).execute()

    assert runner.commands == [
        tool_command("bandit", ["-r", "src", "tools", "-ll"])
    ]
    assert runner.calls[0][1] == tmp_path.resolve()
    assert result.status is Status.SAFE
    assert "not assessed" in result.message


def test_security_returns_failure_and_preserves_tool_output(
    tmp_path,
    monkeypatch,
) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\nname='demo'\n")
    (tmp_path / "src").mkdir()
    monkeypatch.chdir(tmp_path)
    runner = FakeProcessRunner(returncode=1, output="Bandit finding")

    result = SecurityCommand(runner).execute()

    assert result.status is Status.FAIL
    assert result.exit_code == 1
    assert result.message == "Bandit finding"


def test_security_fails_clearly_when_no_source_root_exists(
    tmp_path,
    monkeypatch,
) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\nname='demo'\n")
    monkeypatch.chdir(tmp_path)
    runner = FakeProcessRunner()

    result = SecurityCommand(runner).execute()

    assert runner.commands == []
    assert result.status is Status.FAIL
    assert result.exit_code != 0
    assert "Configured source path does not exist: src" in result.message

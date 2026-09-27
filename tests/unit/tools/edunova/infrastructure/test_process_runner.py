import subprocess

import pytest

from tools.edunova.infrastructure.process_runner import ProcessRunner


def test_process_runner_returns_completed_process() -> None:
    runner = ProcessRunner()

    result = runner.run(
        [
            "python",
            "-c",
            "print('hello')",
        ]
    )

    assert isinstance(result, subprocess.CompletedProcess)
    assert result.returncode == 0
    assert "hello" in result.stdout


def test_process_runner_captures_stderr() -> None:
    runner = ProcessRunner()

    result = runner.run(
        [
            "python",
            "-c",
            "import sys; print('error', file=sys.stderr)",
        ]
    )

    assert result.returncode == 0
    assert "error" in result.stderr


def test_process_runner_preserves_failure_exit_code() -> None:
    runner = ProcessRunner()

    result = runner.run(
        [
            "python",
            "-c",
            "raise SystemExit(7)",
        ]
    )

    assert result.returncode == 7


def test_process_runner_raises_for_missing_executable() -> None:
    runner = ProcessRunner()

    with pytest.raises(FileNotFoundError):
        runner.run(["executable-that-does-not-exist"])

def test_process_runner_raises_os_error_for_unlaunchable_process() -> None:
    runner = ProcessRunner()

    with pytest.raises(OSError):
        runner.run(["executable-that-does-not-exist"])

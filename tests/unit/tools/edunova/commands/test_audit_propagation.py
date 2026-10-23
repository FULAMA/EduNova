import subprocess

from tools.edunova.commands.run_tests import RunTestsCommand
from tools.edunova.core.result import Status
from tools.edunova.cli import main
from tools.edunova.execution.decision import (
    ExecutionDecision,
    ExecutionDecisionType,
)
from tools.edunova.execution.service import AuditStatus, ExecutionResult
from tools.edunova.infrastructure.process_runner import ProcessRunner
from tools.edunova.project_config import ProjectConfig


def allowed_decision() -> ExecutionDecision:
    return ExecutionDecision(
        ExecutionDecisionType.ALLOW,
        "allowed",
        "test",
        False,
    )


def test_command_reports_review_when_process_succeeds_but_audit_fails(
    monkeypatch,
    tmp_path,
) -> None:
    (tmp_path / "tests").mkdir()
    execution = ExecutionResult(
        decision=allowed_decision(),
        executed=True,
        process=subprocess.CompletedProcess(
            ["pytest"],
            0,
            stdout="tests passed",
            stderr="",
        ),
        task_id="pytest.run",
        audit_status=AuditStatus.FAILED,
        audit_error="Audit sink failed (RuntimeError).",
    )
    monkeypatch.setattr(
        "tools.edunova.commands.run_tests.run_cli_task",
        lambda *args, **kwargs: execution,
    )

    result = RunTestsCommand(
        ProcessRunner(),
        ProjectConfig(project_root=tmp_path),
    ).execute()

    assert result.status is Status.REVIEW
    assert result.exit_code == 2
    assert "audit" in result.message.lower()
    assert "RuntimeError" not in result.message


def test_cli_propagates_audit_review_without_hiding_process_result(
    monkeypatch,
    capsys,
) -> None:
    execution = ExecutionResult(
        decision=allowed_decision(),
        executed=True,
        process=subprocess.CompletedProcess(
            ["pytest"],
            0,
            stdout="tests passed",
            stderr="",
        ),
        task_id="pytest.run",
        audit_status=AuditStatus.FAILED,
        audit_error="Audit sink failed (RuntimeError).",
    )
    monkeypatch.setattr(
        "tools.edunova.commands.run_tests.run_cli_task",
        lambda *args, **kwargs: execution,
    )

    exit_code = main(["run_tests"])
    captured = capsys.readouterr()

    assert exit_code == 2
    assert "audit" in captured.out.lower()
    assert "RuntimeError" not in captured.out

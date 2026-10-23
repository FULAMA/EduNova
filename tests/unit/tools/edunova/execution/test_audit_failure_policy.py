from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from tools.edunova.execution.action import ExecutionAction
from tools.edunova.execution.audit import ExecutionAuditRecord
from tools.edunova.execution.audit_sink import ExecutionAuditSink
from tools.edunova.execution.capability import ExecutionCapability
from tools.edunova.execution.default_policy import DefaultExecutionPolicy
from tools.edunova.execution.decision import (
    ExecutionDecision,
    ExecutionDecisionType,
)
from tools.edunova.execution.request import ExecutionRequest
from tools.edunova.execution.risk import ExecutionRisk
from tools.edunova.execution.scope import ExecutionScope
from tools.edunova.execution.service import AuditStatus, ExecutionService
from tools.edunova.execution.sqlite_audit_sink import SqliteExecutionAuditSink


class RecordingRunner:
    def __init__(self, returncode: int = 0) -> None:
        self.calls = 0
        self.returncode = returncode

    def run(self, command, cwd=None):
        self.calls += 1
        return subprocess.CompletedProcess(command, self.returncode, "out", "")


class RaisingRunner:
    def __init__(self, error: BaseException) -> None:
        self.error = error
        self.calls = 0

    def run(self, command, cwd=None):
        self.calls += 1
        raise self.error


class FailingSink(ExecutionAuditSink):
    def __init__(self, fail_on_call: int = 1) -> None:
        self.calls = 0
        self.fail_on_call = fail_on_call
        self.records: list[ExecutionAuditRecord] = []

    def record(self, audit: ExecutionAuditRecord) -> None:
        self.calls += 1
        if self.calls == self.fail_on_call:
            raise RuntimeError("api_key=must-not-leak")
        self.records.append(audit)


class DenyPolicy:
    def evaluate(self, request: ExecutionRequest) -> ExecutionDecision:
        return ExecutionDecision(
            ExecutionDecisionType.DENY,
            "policy denied",
            "test",
            False,
        )


def make_request() -> ExecutionRequest:
    root = Path.cwd()
    return ExecutionRequest(
        action=ExecutionAction.TEST,
        target=str(root),
        scope=ExecutionScope.TEST_SUITE,
        actor="test",
        risk=ExecutionRisk.MEDIUM,
        requested_capabilities=frozenset(
            {
                ExecutionCapability.FILESYSTEM_READ,
                ExecutionCapability.PROCESS_EXECUTE,
            }
        ),
        evidence=("audit failure test",),
        project_root=root,
    )


def make_service(runner, sink, policy=None) -> ExecutionService:
    return ExecutionService(
        policy=policy or DefaultExecutionPolicy(),
        runner=runner,
        audit_sink=sink,
    )


def execute(service: ExecutionService):
    return service.execute(
        make_request(),
        "pytest.run",
        {"paths": ["tests"], "options": []},
    )


def test_intent_audit_failure_blocks_runner_without_leaking_sink_error() -> None:
    runner = RecordingRunner()
    result = execute(make_service(runner, FailingSink()))

    assert runner.calls == 0
    assert result.executed is False
    assert result.audit_status is AuditStatus.FAILED
    assert result.decision.decision is ExecutionDecisionType.DENY
    assert result.audit_error == "Audit sink failed (RuntimeError)."
    assert "must-not-leak" not in result.audit_error


def test_result_audit_failure_preserves_process_result_and_code() -> None:
    runner = RecordingRunner(returncode=7)
    result = execute(make_service(runner, FailingSink(fail_on_call=2)))

    assert runner.calls == 1
    assert result.executed is True
    assert result.process is not None
    assert result.process.returncode == 7
    assert result.audit_status is AuditStatus.FAILED
    assert result.audit_error == "Audit sink failed (RuntimeError)."


def test_success_records_intent_and_result_without_bypassing_policy() -> None:
    runner = RecordingRunner()
    sink = FailingSink(fail_on_call=3)
    result = execute(make_service(runner, sink))

    assert runner.calls == 1
    assert result.executed is True
    assert result.audit_status is AuditStatus.RECORDED
    assert len(sink.records) == 2
    assert sink.records[0].executed is False
    assert sink.records[1].executed is True


def test_sqlite_sink_persists_intent_and_result(tmp_path: Path) -> None:
    sink = SqliteExecutionAuditSink(tmp_path / "audit.sqlite3")
    result = execute(make_service(RecordingRunner(), sink))

    reopened = SqliteExecutionAuditSink(tmp_path / "audit.sqlite3")
    assert result.executed is True
    assert tuple(record.executed for record in reopened.records) == (False, True)


def test_policy_denial_does_not_start_process() -> None:
    runner = RecordingRunner()
    sink = FailingSink(fail_on_call=3)
    result = execute(make_service(runner, sink, policy=DenyPolicy()))

    assert runner.calls == 0
    assert result.executed is False
    assert result.decision.decision is ExecutionDecisionType.DENY
    assert result.audit_status is AuditStatus.RECORDED
    assert len(sink.records) == 1


@pytest.mark.parametrize(
    "error",
    [
        subprocess.TimeoutExpired(["pytest"], timeout=1),
        FileNotFoundError(2, "missing", "pytest"),
        KeyboardInterrupt(),
    ],
)
def test_runner_error_is_not_masked_by_result_audit_failure(error) -> None:
    runner = RaisingRunner(error)
    sink = FailingSink(fail_on_call=2)

    with pytest.raises(type(error)):
        execute(make_service(runner, sink))

    assert runner.calls == 1


def test_runner_exception_is_redacted_before_audit_storage() -> None:
    runner = RaisingRunner(RuntimeError("Bearer super-secret-token"))
    sink = FailingSink(fail_on_call=99)

    with pytest.raises(RuntimeError):
        execute(make_service(runner, sink))

    assert len(sink.records) == 2
    assert sink.records[1].failure is not None
    assert "super-secret-token" not in sink.records[1].failure
    assert "[REDACTED]" in sink.records[1].failure

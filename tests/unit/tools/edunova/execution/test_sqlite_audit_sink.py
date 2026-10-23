from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from tools.edunova.execution.action import ExecutionAction
from tools.edunova.execution.audit import ExecutionAuditRecord
from tools.edunova.execution.capability import ExecutionCapability
from tools.edunova.execution.decision import ExecutionDecisionType
from tools.edunova.execution.risk import ExecutionRisk
from tools.edunova.execution.scope import ExecutionScope
from tools.edunova.execution.sqlite_audit_sink import (
    AuditStorageError,
    SqliteExecutionAuditSink,
)


def make_audit(index: int = 0) -> ExecutionAuditRecord:
    return ExecutionAuditRecord(
        action=ExecutionAction.TEST,
        target="project",
        scope=ExecutionScope.TEST_SUITE,
        actor="test",
        risk=ExecutionRisk.MEDIUM,
        requested_capabilities=frozenset(
            {
                ExecutionCapability.FILESYSTEM_READ,
                ExecutionCapability.PROCESS_EXECUTE,
            }
        ),
        evidence=(f"event-{index}",),
        decision=ExecutionDecisionType.ALLOW,
        reason="allowed",
        policy="default",
        required_approval=False,
        executed=index % 2 == 1,
        exit_code=0 if index % 2 == 1 else None,
        attempted=index % 2 == 1,
        task_id="pytest.run",
        parameter_digest=f"{index:064x}",
    )


def test_sqlite_sink_survives_reopen(tmp_path: Path) -> None:
    path = tmp_path / "audit.sqlite3"
    sink = SqliteExecutionAuditSink(path)
    audit = make_audit(1)

    sink.record(audit)

    reopened = SqliteExecutionAuditSink(path)
    assert reopened.records == (audit,)


def test_sqlite_sink_redacts_persisted_text(tmp_path: Path) -> None:
    path = tmp_path / "audit.sqlite3"
    sink = SqliteExecutionAuditSink(path)
    audit = make_audit()
    audit = ExecutionAuditRecord(
        **{
            **audit.__dict__,
            "target": "https://user:password@example.test",
            "evidence": ("Authorization: Bearer secret-token",),
            "reason": "api_key=secret-value",
            "failure": "password=secret-value",
            "attempted": True,
        }
    )

    sink.record(audit)

    raw = path.read_bytes()
    assert b"secret-token" not in raw
    assert b"secret-value" not in raw
    assert b"password@example.test" not in raw


def test_sqlite_sink_rejects_corrupt_storage(tmp_path: Path) -> None:
    path = tmp_path / "audit.sqlite3"
    SqliteExecutionAuditSink(path)
    path.write_bytes(b"not a sqlite database")

    with pytest.raises(AuditStorageError, match="unavailable"):
        SqliteExecutionAuditSink(path)


def test_sqlite_sink_reports_write_failure(tmp_path: Path) -> None:
    path = tmp_path / "audit.sqlite3"
    sink = SqliteExecutionAuditSink(path)
    path.unlink()
    path.mkdir()

    with pytest.raises(AuditStorageError, match="unavailable"):
        sink.record(make_audit())


def test_sqlite_sink_serializes_concurrent_writes(tmp_path: Path) -> None:
    sink = SqliteExecutionAuditSink(tmp_path / "audit.sqlite3")

    with ThreadPoolExecutor(max_workers=4) as executor:
        list(executor.map(sink.record, (make_audit(index) for index in range(20))))

    assert len(sink.records) == 20


def test_sqlite_sink_applies_retention_limit(tmp_path: Path) -> None:
    sink = SqliteExecutionAuditSink(
        tmp_path / "audit.sqlite3",
        retention_limit=2,
    )

    for index in range(4):
        sink.record(make_audit(index))

    assert tuple(audit.evidence[0] for audit in sink.records) == (
        "event-2",
        "event-3",
    )

from __future__ import annotations

from tools.edunova.execution.action import ExecutionAction
from tools.edunova.execution.audit import ExecutionAuditRecord
from tools.edunova.execution.capability import ExecutionCapability
from tools.edunova.execution.decision import ExecutionDecisionType
from tools.edunova.execution.memory_audit_sink import (
    InMemoryExecutionAuditSink,
)
from tools.edunova.execution.risk import ExecutionRisk
from tools.edunova.execution.scope import ExecutionScope


def make_audit() -> ExecutionAuditRecord:
    return ExecutionAuditRecord(
        action=ExecutionAction.READ,
        target="src/example.py",
        scope=ExecutionScope.FILE,
        actor="test",
        risk=ExecutionRisk.LOW,
        requested_capabilities=frozenset(
            {ExecutionCapability.FILESYSTEM_READ}
        ),
        evidence=("observed",),
        decision=ExecutionDecisionType.ALLOW,
        reason="allowed",
        policy="default",
        required_approval=False,
        executed=False,
    )


def test_memory_sink_records_audit() -> None:
    sink = InMemoryExecutionAuditSink()

    audit = make_audit()

    sink.record(audit)

    assert sink.records == (audit,)


def test_memory_sink_returns_snapshot() -> None:
    sink = InMemoryExecutionAuditSink()

    sink.record(make_audit())

    records = sink.records

    assert isinstance(records, tuple)
    assert len(records) == 1

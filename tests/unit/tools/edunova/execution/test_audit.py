from __future__ import annotations

import pytest

from tools.edunova.execution.action import ExecutionAction
from tools.edunova.execution.audit import ExecutionAuditRecord
from tools.edunova.execution.capability import ExecutionCapability
from tools.edunova.execution.decision import ExecutionDecisionType
from tools.edunova.execution.risk import ExecutionRisk
from tools.edunova.execution.scope import ExecutionScope


def make_audit(
    *,
    decision: ExecutionDecisionType = ExecutionDecisionType.ALLOW,
    executed: bool = False,
    exit_code: int | None = None,
    attempted: bool | None = None,
    failure: str | None = None,
) -> ExecutionAuditRecord:
    if attempted is None:
        attempted = executed

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
        decision=decision,
        reason="test decision",
        policy="default",
        required_approval=(
            decision is ExecutionDecisionType.REVIEW
        ),
        executed=executed,
        exit_code=exit_code,
        attempted=attempted,
        failure=failure,
    )


def test_audit_record_is_immutable() -> None:
    audit = make_audit()

    with pytest.raises(AttributeError):
        audit.target = "changed"  # type: ignore[misc]


def test_executed_record_requires_exit_code() -> None:
    with pytest.raises(
        ValueError,
        match="exit code",
    ):
        make_audit(executed=True)


def test_non_executed_record_cannot_have_exit_code() -> None:
    with pytest.raises(
        ValueError,
        match="exit code",
    ):
        make_audit(
            executed=False,
            exit_code=0,
        )


def test_review_requires_approval() -> None:
    with pytest.raises(
        ValueError,
        match="human approval",
    ):
        ExecutionAuditRecord(
            action=ExecutionAction.MODIFY,
            target="src/example.py",
            scope=ExecutionScope.FILE,
            actor="test",
            risk=ExecutionRisk.HIGH,
            requested_capabilities=frozenset(
                {
                    ExecutionCapability.FILESYSTEM_READ,
                    ExecutionCapability.FILESYSTEM_WRITE,
                }
            ),
            evidence=("observed",),
            decision=ExecutionDecisionType.REVIEW,
            reason="review required",
            policy="default",
            required_approval=False,
            executed=False,
        )


def test_allow_cannot_require_approval() -> None:
    with pytest.raises(
        ValueError,
        match="cannot require approval",
    ):
        ExecutionAuditRecord(
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
            required_approval=True,
            executed=False,
        )


def test_executed_record_requires_attempted_execution() -> None:
    with pytest.raises(ValueError, match="execution attempt"):
        make_audit(executed=True, attempted=False, exit_code=0)


def test_failed_attempt_requires_failure_description() -> None:
    with pytest.raises(ValueError, match="failure description"):
        make_audit(attempted=True)


def test_failure_requires_attempted_non_executed_command() -> None:
    with pytest.raises(ValueError, match="attempted, non-executed"):
        make_audit(failure="RuntimeError: runner failed")


def test_failure_description_cannot_be_blank() -> None:
    with pytest.raises(ValueError, match="failure cannot be empty"):
        make_audit(attempted=True, failure=" ")

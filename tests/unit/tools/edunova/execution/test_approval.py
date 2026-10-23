from __future__ import annotations

import pytest

from tools.edunova.execution.action import ExecutionAction
from tools.edunova.execution.approval import (
    ApprovalStatus,
    ExecutionApproval,
)
from tools.edunova.execution.capability import ExecutionCapability
from tools.edunova.execution.decision import (
    ExecutionDecision,
    ExecutionDecisionType,
)
from tools.edunova.execution.request import ExecutionRequest
from tools.edunova.execution.risk import ExecutionRisk
from tools.edunova.execution.scope import ExecutionScope


def make_request() -> ExecutionRequest:
    return ExecutionRequest(
        action=ExecutionAction.MODIFY,
        target="src/example.py",
        scope=ExecutionScope.FILE,
        actor="agent",
        risk=ExecutionRisk.HIGH,
        requested_capabilities=frozenset(
            {ExecutionCapability.FILESYSTEM_WRITE}
        ),
        evidence=("src/example.py",),
    )


def make_review() -> ExecutionDecision:
    return ExecutionDecision(
        decision=ExecutionDecisionType.REVIEW,
        reason="File modification requires human approval.",
        policy="default-execution-policy",
        required_approval=True,
        evidence=("src/example.py",),
    )


def test_approval_requires_non_empty_target() -> None:
    with pytest.raises(ValueError, match="target"):
        ExecutionApproval(
            action=ExecutionAction.MODIFY,
            target=" ",
            scope=ExecutionScope.FILE,
            actor="agent",
            risk=ExecutionRisk.HIGH,
            requested_capabilities=frozenset(),
            decision=ExecutionDecisionType.REVIEW,
            command=("python", "-m", "pytest"),
            approver="human",
            status=ApprovalStatus.APPROVED,
            reason="Approved.",
        )


def test_approval_requires_approver() -> None:
    with pytest.raises(ValueError, match="approver"):
        ExecutionApproval(
            action=ExecutionAction.MODIFY,
            target="src/example.py",
            scope=ExecutionScope.FILE,
            actor="agent",
            risk=ExecutionRisk.HIGH,
            requested_capabilities=frozenset(),
            decision=ExecutionDecisionType.REVIEW,
            command=("python", "-m", "pytest"),
            approver=" ",
            status=ApprovalStatus.APPROVED,
            reason="Approved.",
        )


def test_approval_requires_reason() -> None:
    with pytest.raises(ValueError, match="reason"):
        ExecutionApproval(
            action=ExecutionAction.MODIFY,
            target="src/example.py",
            scope=ExecutionScope.FILE,
            actor="agent",
            risk=ExecutionRisk.HIGH,
            requested_capabilities=frozenset(),
            decision=ExecutionDecisionType.REVIEW,
            command=("python", "-m", "pytest"),
            approver="human",
            status=ApprovalStatus.APPROVED,
            reason=" ",
        )


def test_approval_only_accepts_review_decision() -> None:
    with pytest.raises(ValueError, match="REVIEW"):
        ExecutionApproval(
            action=ExecutionAction.READ,
            target="src/example.py",
            scope=ExecutionScope.FILE,
            actor="agent",
            risk=ExecutionRisk.LOW,
            requested_capabilities=frozenset(
                {ExecutionCapability.FILESYSTEM_READ}
            ),
            decision=ExecutionDecisionType.ALLOW,
            command=("python", "-m", "pytest"),
            approver="human",
            status=ApprovalStatus.APPROVED,
            reason="Approved.",
        )


def test_approval_is_bound_to_request() -> None:
    request = make_request()
    decision = make_review()

    approval = ExecutionApproval(
        action=request.action,
        target=request.target,
        scope=request.scope,
        actor=request.actor,
        risk=request.risk,
        requested_capabilities=request.requested_capabilities,
        decision=decision.decision,
            command=("python", "-m", "pytest"),
        approver="human",
        status=ApprovalStatus.APPROVED,
        reason="Reviewed and approved.",
        evidence=request.evidence,
    )

    assert approval.action is request.action
    assert approval.target == request.target
    assert approval.scope is request.scope
    assert approval.actor == request.actor
    assert approval.risk is request.risk
    assert approval.requested_capabilities == request.requested_capabilities
    assert approval.decision is ExecutionDecisionType.REVIEW
    assert approval.status is ApprovalStatus.APPROVED


def test_rejected_approval_is_immutable_contract() -> None:
    request = make_request()
    decision = make_review()

    approval = ExecutionApproval(
        action=request.action,
        target=request.target,
        scope=request.scope,
        actor=request.actor,
        risk=request.risk,
        requested_capabilities=request.requested_capabilities,
        decision=decision.decision,
            command=("python", "-m", "pytest"),
        approver="human",
        status=ApprovalStatus.REJECTED,
        reason="Modification rejected.",
        evidence=request.evidence,
    )

    assert approval.status is ApprovalStatus.REJECTED


def test_allow_cannot_be_approved() -> None:
    request = make_request()

    decision = ExecutionDecision(
        decision=ExecutionDecisionType.ALLOW,
        reason="Safe operation.",
        policy="default-execution-policy",
        required_approval=False,
    )

    with pytest.raises(ValueError, match="REVIEW"):
        ExecutionApproval(
            action=request.action,
            target=request.target,
            scope=request.scope,
            actor=request.actor,
            risk=request.risk,
            requested_capabilities=request.requested_capabilities,
            decision=decision.decision,
            command=("python", "-m", "pytest"),
            approver="human",
            status=ApprovalStatus.APPROVED,
            reason="Approved.",
        )

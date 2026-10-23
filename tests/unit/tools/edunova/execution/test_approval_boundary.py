from __future__ import annotations

import pytest

from tools.edunova.execution.approval import ApprovalStatus
from tools.edunova.execution.decision import (
    ExecutionDecision,
    ExecutionDecisionType,
)
from tools.edunova.execution.memory_approval_boundary import (
    InMemoryApprovalBoundary,
)
from tools.edunova.execution.request import ExecutionRequest
from tools.edunova.execution.action import ExecutionAction
from tools.edunova.execution.capability import ExecutionCapability
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
        reason="Modification requires human approval.",
        policy="default-execution-policy",
        required_approval=True,
        evidence=("src/example.py",),
    )


def test_boundary_approves_review() -> None:
    boundary = InMemoryApprovalBoundary()

    approval = boundary.approve(
        make_request(),
        make_review(),
        ("python", "-m", "pytest"),
        "human",
        "Reviewed and approved.",
    )

    assert approval.status is ApprovalStatus.APPROVED
    assert approval.approver == "human"
    assert len(boundary.approvals) == 1


def test_boundary_rejects_review() -> None:
    boundary = InMemoryApprovalBoundary()

    approval = boundary.reject(
        make_request(),
        make_review(),
        ("python", "-m", "pytest"),
        "human",
        "Insufficient justification.",
    )

    assert approval.status is ApprovalStatus.REJECTED
    assert len(boundary.approvals) == 1


def test_boundary_rejects_allow_decision() -> None:
    boundary = InMemoryApprovalBoundary()

    decision = ExecutionDecision(
        decision=ExecutionDecisionType.ALLOW,
        reason="Safe.",
        policy="default-execution-policy",
        required_approval=False,
    )

    with pytest.raises(ValueError, match="REVIEW"):
        boundary.approve(
            make_request(),
            decision,
            ("python", "-m", "pytest"),
            "human",
            "Approved.",
        )


def test_boundary_rejects_deny_decision() -> None:
    boundary = InMemoryApprovalBoundary()

    decision = ExecutionDecision(
        decision=ExecutionDecisionType.DENY,
        reason="Unauthorized.",
        policy="default-execution-policy",
        required_approval=False,
    )

    with pytest.raises(ValueError, match="REVIEW"):
        boundary.reject(
            make_request(),
            decision,
            ("python", "-m", "pytest"),
            "human",
            "Rejected.",
        )


def test_boundary_preserves_request_evidence() -> None:
    boundary = InMemoryApprovalBoundary()

    request = make_request()
    approval = boundary.approve(
        request,
        make_review(),
        ("python", "-m", "pytest"),
        "human",
        "Evidence verified.",
    )

    assert approval.evidence == request.evidence

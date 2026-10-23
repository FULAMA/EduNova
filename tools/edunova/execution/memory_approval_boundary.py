from __future__ import annotations

from collections.abc import Sequence

from tools.edunova.execution.approval import (
    ApprovalStatus,
    ExecutionApproval,
)
from tools.edunova.execution.approval_boundary import ApprovalBoundary
from tools.edunova.execution.decision import (
    ExecutionDecision,
    ExecutionDecisionType,
)
from tools.edunova.execution.request import ExecutionRequest


class InMemoryApprovalBoundary(ApprovalBoundary):
    def __init__(self) -> None:
        self._approvals: list[ExecutionApproval] = []
        self._consumed: set[ExecutionApproval] = set()

    def approve(
        self,
        request: ExecutionRequest,
        decision: ExecutionDecision,
        command: Sequence[str],
        approver: str,
        reason: str,
    ) -> ExecutionApproval:
        self._validate_review(decision)

        approval = ExecutionApproval(
            action=request.action,
            target=request.target,
            scope=request.scope,
            actor=request.actor,
            risk=request.risk,
            requested_capabilities=request.requested_capabilities,
            decision=decision.decision,
            command=tuple(command),
            approver=approver,
            status=ApprovalStatus.APPROVED,
            reason=reason,
            evidence=request.evidence,
        )

        self._approvals.append(approval)
        return approval

    def reject(
        self,
        request: ExecutionRequest,
        decision: ExecutionDecision,
        command: Sequence[str],
        approver: str,
        reason: str,
    ) -> ExecutionApproval:
        self._validate_review(decision)

        approval = ExecutionApproval(
            action=request.action,
            target=request.target,
            scope=request.scope,
            actor=request.actor,
            risk=request.risk,
            requested_capabilities=request.requested_capabilities,
            decision=decision.decision,
            command=tuple(command),
            approver=approver,
            status=ApprovalStatus.REJECTED,
            reason=reason,
            evidence=request.evidence,
        )

        self._approvals.append(approval)
        return approval

    def consume(
        self,
        approval: ExecutionApproval,
    ) -> None:
        if approval.status is not ApprovalStatus.APPROVED:
            raise ValueError(
                "Only approved executions can be consumed."
            )

        if approval not in self._approvals:
            raise ValueError(
                "Approval does not belong to this boundary."
            )

        if approval in self._consumed:
            raise ValueError(
                "Approval has already been consumed."
            )

        self._consumed.add(approval)

    @property
    def approvals(self) -> tuple[ExecutionApproval, ...]:
        return tuple(self._approvals)

    @staticmethod
    def _validate_review(
        decision: ExecutionDecision,
    ) -> None:
        if decision.decision is not ExecutionDecisionType.REVIEW:
            raise ValueError(
                "Approval requires a REVIEW execution decision."
            )

        if not decision.required_approval:
            raise ValueError(
                "REVIEW approval requires human approval."
            )

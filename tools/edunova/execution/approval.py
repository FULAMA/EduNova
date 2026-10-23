from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from tools.edunova.execution.action import ExecutionAction
from tools.edunova.execution.capability import ExecutionCapability
from tools.edunova.execution.decision import ExecutionDecisionType
from tools.edunova.execution.risk import ExecutionRisk
from tools.edunova.execution.scope import ExecutionScope


class ApprovalStatus(str, Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


@dataclass(frozen=True)
class ExecutionApproval:
    action: ExecutionAction
    target: str
    scope: ExecutionScope
    actor: str
    risk: ExecutionRisk
    requested_capabilities: frozenset[ExecutionCapability]
    decision: ExecutionDecisionType
    command: tuple[str, ...]
    approver: str
    status: ApprovalStatus
    reason: str
    evidence: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.command or any(not part.strip() for part in self.command):
            raise ValueError("Approval command cannot be empty or contain empty arguments.")

        if not self.target.strip():
            raise ValueError("Approval target cannot be empty.")

        if not self.actor.strip():
            raise ValueError("Approval actor cannot be empty.")

        if not self.approver.strip():
            raise ValueError("Approval approver cannot be empty.")

        if not self.reason.strip():
            raise ValueError("Approval reason cannot be empty.")

        if self.decision is not ExecutionDecisionType.REVIEW:
            raise ValueError(
                "Approvals are only valid for REVIEW decisions."
            )

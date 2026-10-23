from __future__ import annotations

from dataclasses import dataclass

from tools.edunova.execution.action import ExecutionAction
from tools.edunova.execution.capability import ExecutionCapability
from tools.edunova.execution.decision import ExecutionDecisionType
from tools.edunova.execution.risk import ExecutionRisk
from tools.edunova.execution.scope import ExecutionScope


@dataclass(frozen=True)
class ExecutionAuditRecord:
    action: ExecutionAction
    target: str
    scope: ExecutionScope
    actor: str
    risk: ExecutionRisk
    requested_capabilities: frozenset[ExecutionCapability]
    evidence: tuple[str, ...]
    decision: ExecutionDecisionType
    reason: str
    policy: str
    required_approval: bool
    executed: bool
    exit_code: int | None = None
    attempted: bool = False
    failure: str | None = None
    task_id: str | None = None
    parameter_digest: str | None = None

    def __post_init__(self) -> None:
        if not self.target.strip():
            raise ValueError("Audit target cannot be empty.")

        if not self.actor.strip():
            raise ValueError("Audit actor cannot be empty.")

        if not self.reason.strip():
            raise ValueError("Audit reason cannot be empty.")

        if not self.policy.strip():
            raise ValueError("Audit policy cannot be empty.")

        if self.executed and not self.attempted:
            raise ValueError(
                "Executed audit records require an execution attempt."
            )

        if self.executed and self.exit_code is None:
            raise ValueError(
                "Executed audit records require an exit code."
            )

        if not self.executed and self.exit_code is not None:
            raise ValueError(
                "Non-executed audit records cannot have an exit code."
            )

        if self.failure is not None and not self.failure.strip():
            raise ValueError("Audit failure cannot be empty.")

        if self.failure is not None and (
            not self.attempted or self.executed
        ):
            raise ValueError(
                "Audit failure requires an attempted, non-executed command."
            )

        if self.attempted and not self.executed and self.failure is None:
            raise ValueError(
                "Failed execution attempts require a failure description."
            )

        if (
            self.decision is ExecutionDecisionType.REVIEW
            and not self.required_approval
        ):
            raise ValueError(
                "REVIEW audit records require human approval."
            )

        if self.decision is ExecutionDecisionType.ALLOW:
            if self.required_approval:
                raise ValueError(
                    "ALLOW audit records cannot require approval."
                )

        if self.decision is ExecutionDecisionType.DENY:
            if self.required_approval:
                raise ValueError(
                    "DENY audit records cannot require approval."
                )

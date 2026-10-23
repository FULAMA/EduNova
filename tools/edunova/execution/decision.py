from dataclasses import dataclass
from enum import Enum


class ExecutionDecisionType(str, Enum):
    ALLOW = "ALLOW"
    REVIEW = "REVIEW"
    DENY = "DENY"


@dataclass(frozen=True)
class ExecutionDecision:
    decision: ExecutionDecisionType
    reason: str
    policy: str
    required_approval: bool
    evidence: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.reason.strip():
            raise ValueError("Execution decision reason cannot be empty.")

        if not self.policy.strip():
            raise ValueError("Execution decision policy cannot be empty.")

        if self.decision is ExecutionDecisionType.REVIEW:
            if not self.required_approval:
                raise ValueError(
                    "REVIEW decisions require human approval."
                )

        elif self.decision is ExecutionDecisionType.ALLOW:
            if self.required_approval:
                raise ValueError(
                    "ALLOW decisions cannot require human approval."
                )

        elif self.decision is ExecutionDecisionType.DENY:
            if self.required_approval:
                raise ValueError(
                    "DENY decisions cannot require human approval."
                )

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from tools.edunova.execution.approval import ExecutionApproval
from tools.edunova.execution.decision import ExecutionDecision
from tools.edunova.execution.request import ExecutionRequest


class ApprovalBoundary(ABC):
    @abstractmethod
    def approve(
        self,
        request: ExecutionRequest,
        decision: ExecutionDecision,
        command: Sequence[str],
        approver: str,
        reason: str,
    ) -> ExecutionApproval:
        raise NotImplementedError

    @abstractmethod
    def reject(
        self,
        request: ExecutionRequest,
        decision: ExecutionDecision,
        command: Sequence[str],
        approver: str,
        reason: str,
    ) -> ExecutionApproval:
        raise NotImplementedError

    @abstractmethod
    def consume(
        self,
        approval: ExecutionApproval,
    ) -> None:
        raise NotImplementedError

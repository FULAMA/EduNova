from __future__ import annotations

from abc import ABC, abstractmethod

from tools.edunova.execution.audit import ExecutionAuditRecord


class ExecutionAuditSink(ABC):
    @abstractmethod
    def record(
        self,
        audit: ExecutionAuditRecord,
    ) -> None:
        raise NotImplementedError

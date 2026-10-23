from __future__ import annotations

from tools.edunova.execution.audit import ExecutionAuditRecord
from tools.edunova.execution.audit_sink import ExecutionAuditSink


class InMemoryExecutionAuditSink(ExecutionAuditSink):
    def __init__(self) -> None:
        self._records: list[ExecutionAuditRecord] = []

    def record(
        self,
        audit: ExecutionAuditRecord,
    ) -> None:
        self._records.append(audit)

    @property
    def records(self) -> tuple[ExecutionAuditRecord, ...]:
        return tuple(self._records)

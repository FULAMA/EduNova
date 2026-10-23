from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from tools.edunova.execution.action import ExecutionAction
from tools.edunova.execution.risk import ExecutionRisk
from tools.edunova.execution.scope import ExecutionScope


@dataclass(frozen=True)
class LocalOperationSummary:
    action: ExecutionAction
    task_id: str
    parameters: Mapping[str, Any]
    project_root: Path
    scope: ExecutionScope
    risk: ExecutionRisk
    expected_effects: str


class LocalApprovalConfirmation(Protocol):
    """Local user confirmation, explicitly not identity authentication."""

    def confirm(self, operation: LocalOperationSummary) -> bool: ...


class ConsoleApprovalConfirmation:
    """Ask the interactive terminal user to approve this exact operation."""

    def __init__(
        self,
        input_fn: Callable[[str], str] = input,
        output_fn: Callable[[str], None] = print,
    ) -> None:
        self._input = input_fn
        self._output = output_fn

    def confirm(self, operation: LocalOperationSummary) -> bool:
        self._output("Sensitive EduNova operation requires local confirmation")
        self._output(f"Action: {operation.action.value}")
        self._output(f"Task: {operation.task_id}")
        self._output(f"Parameters: {dict(operation.parameters)!r}")
        self._output(f"Project: {operation.project_root}")
        self._output(f"Scope: {operation.scope.value}")
        self._output(f"Risk: {operation.risk.name}")
        self._output(f"Expected effects: {operation.expected_effects}")
        self._output("This confirms this operation only; it does not authenticate identity.")
        try:
            response = self._input("Type YES to approve; any other response refuses: ")
        except (EOFError, KeyboardInterrupt, OSError):
            return False
        return response.strip() == "YES"

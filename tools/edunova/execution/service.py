from __future__ import annotations

import subprocess
from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from tools.edunova.execution.local_confirmation import (
    LocalApprovalConfirmation,
    LocalOperationSummary,
)
from tools.edunova.execution.action_constraints import constraints_for
from tools.edunova.execution.audit import ExecutionAuditRecord
from tools.edunova.execution.audit_sink import ExecutionAuditSink
from tools.edunova.execution.capability_matrix import allowed_capabilities
from tools.edunova.execution.decision import ExecutionDecision, ExecutionDecisionType
from tools.edunova.execution.policy import ExecutionPolicy
from tools.edunova.execution.request import ExecutionRequest
from tools.edunova.execution.task_registry import (
    ExecutionTaskRegistry,
    ResolvedTask,
    TaskValidationError,
)
from tools.edunova.infrastructure.process_runner import ProcessRunner
from tools.edunova.security import redact_text


class AuditStatus(str, Enum):
    NOT_ATTEMPTED = "NOT_ATTEMPTED"
    RECORDED = "RECORDED"
    FAILED = "FAILED"


@dataclass(frozen=True)
class ExecutionResult:
    decision: ExecutionDecision
    executed: bool
    process: subprocess.CompletedProcess[str] | None = None
    task_id: str | None = None
    audit_status: AuditStatus = AuditStatus.NOT_ATTEMPTED
    audit_error: str | None = None

    def __post_init__(self) -> None:
        if self.executed != (self.process is not None):
            raise ValueError(
                "Execution result must match executed state and process presence."
            )

        if self.audit_status is AuditStatus.FAILED and self.audit_error is None:
            raise ValueError("Failed audit results must include an audit error.")

        if self.audit_status is not AuditStatus.FAILED and self.audit_error is not None:
            raise ValueError(
                "Only failed audit results may include an audit error."
            )

        if self.executed and self.audit_status is AuditStatus.NOT_ATTEMPTED:
            raise ValueError("Executed results must record an audit outcome.")


class ExecutionService:
    """Policy and task registry gate for every managed process execution."""

    def __init__(
        self,
        policy: ExecutionPolicy,
        runner: ProcessRunner,
        audit_sink: ExecutionAuditSink,
        task_registry: ExecutionTaskRegistry | None = None,
        local_confirmation: LocalApprovalConfirmation | None = None,
    ) -> None:
        self._policy = policy
        self._runner = runner
        self._audit_sink = audit_sink
        self._task_registry = task_registry or ExecutionTaskRegistry()
        self._local_confirmation = local_confirmation

    def execute(
        self,
        request: ExecutionRequest,
        task_id: str,
        parameters: Mapping[str, Any] | None = None,
    ) -> ExecutionResult:
        supplied: Mapping[str, Any] = {} if parameters is None else parameters
        resolved: ResolvedTask | None = None
        try:
            if not isinstance(supplied, Mapping):
                raise TaskValidationError("Task parameters must be a mapping.")
            task = self._task_registry.get(task_id)
            resolved = self._task_registry.resolve(
                task_id,
                supplied,
                request.project_root,
            )
            if Path(request.target).resolve() != resolved.project_root:
                raise TaskValidationError(
                    "Execution target must match the registered task's project root."
                )
            if task.action is not request.action:
                raise TaskValidationError(
                    f"Task {task_id} is incompatible with action {request.action.value}."
                )
            if request.scope not in task.scopes:
                raise TaskValidationError(
                    f"Task {task_id} is not permitted for scope {request.scope.value}."
                )
            if request.risk is not task.risk:
                raise TaskValidationError(
                    f"Task {task_id} requires risk {task.risk.name}."
                )
            if not task.capabilities <= request.requested_capabilities:
                raise TaskValidationError(
                    f"Task {task_id} is missing required capabilities."
                )
            if (
                request.scope not in constraints_for(request.action).scopes
                or request.risk > constraints_for(request.action).max_risk
                or not request.requested_capabilities
                <= allowed_capabilities(request.action)
            ):
                raise TaskValidationError(
                    "Execution request exceeds the action's allowed contract."
                )
        except (TaskValidationError, OSError, ValueError) as error:
            decision = self._denial(str(error), "task-registry")
            audit_error = self._try_record_audit(
                request, decision, False, None, task_id=task_id
            )
            return self._result(
                decision,
                False,
                task_id=task_id,
                audit_error=audit_error,
            )

        try:
            decision = self._policy.evaluate(request)
        except Exception as error:
            decision = self._denial(
                f"Execution policy failed closed ({type(error).__name__}).",
                "policy-error",
            )
            audit_error = self._try_record_audit(
                request,
                decision,
                False,
                None,
                task_id=task_id,
                parameter_digest=resolved.parameter_digest,
            )
            return self._result(
                decision,
                False,
                task_id=task_id,
                audit_error=audit_error,
            )

        if decision.decision is ExecutionDecisionType.DENY:
            audit_error = self._try_record_audit(
                request,
                decision,
                False,
                None,
                task_id=task_id,
                parameter_digest=resolved.parameter_digest,
            )
            return self._result(
                decision,
                False,
                task_id=task_id,
                audit_error=audit_error,
            )

        if task.approval_required and decision.decision is ExecutionDecisionType.ALLOW:
            decision = ExecutionDecision(
                ExecutionDecisionType.REVIEW,
                "The registered task requires local confirmation.",
                decision.policy,
                True,
                decision.evidence,
            )

        if decision.decision is ExecutionDecisionType.REVIEW:
            if self._local_confirmation is None:
                denied = self._denial(
                    "No trusted local confirmation interface is available.",
                    decision.policy,
                )
                audit_error = self._try_record_audit(
                    request,
                    denied,
                    False,
                    None,
                    task_id=task_id,
                    parameter_digest=resolved.parameter_digest,
                )
                return self._result(
                    denied,
                    False,
                    task_id=task_id,
                    audit_error=audit_error,
                )
            operation = LocalOperationSummary(
                action=task.action,
                task_id=task.task_id,
                parameters=resolved.parameters,
                project_root=resolved.project_root,
                scope=request.scope,
                risk=request.risk,
                expected_effects=task.expected_effects,
            )
            try:
                approved = self._local_confirmation.confirm(operation)
            except Exception:
                approved = False
            if not approved:
                denied = self._denial(
                    "Local confirmation was declined or unavailable.",
                    decision.policy,
                )
                audit_error = self._try_record_audit(
                    request,
                    denied,
                    False,
                    None,
                    task_id=task_id,
                    parameter_digest=resolved.parameter_digest,
                )
                return self._result(
                    denied,
                    False,
                    task_id=task_id,
                    audit_error=audit_error,
                )

        intent_error = self._try_record_audit(
            request,
            decision,
            False,
            None,
            task_id=task_id,
            parameter_digest=resolved.parameter_digest,
        )
        if intent_error is not None:
            denied = self._denial(
                "Execution audit unavailable; process was not started.",
                "audit",
            )
            return self._result(
                denied,
                False,
                task_id=task_id,
                audit_error=intent_error,
            )

        try:
            process = self._runner.run(list(resolved.command), cwd=resolved.project_root)
        except KeyboardInterrupt as error:
            self._try_record_audit(
                request,
                decision,
                False,
                None,
                attempted=True,
                failure=f"{type(error).__name__}: interrupted",
                task_id=task_id,
                parameter_digest=resolved.parameter_digest,
            )
            raise
        except Exception as error:
            self._try_record_audit(
                request,
                decision,
                False,
                None,
                attempted=True,
                failure=f"{type(error).__name__}: {redact_text(str(error))}",
                task_id=task_id,
                parameter_digest=resolved.parameter_digest,
            )
            raise

        audit_error = self._try_record_audit(
            request,
            decision,
            True,
            process.returncode,
            attempted=True,
            task_id=task_id,
            parameter_digest=resolved.parameter_digest,
        )
        return self._result(
            decision,
            True,
            process,
            task_id,
            audit_error=audit_error,
        )

    @staticmethod
    def _result(
        decision: ExecutionDecision,
        executed: bool,
        process: subprocess.CompletedProcess[str] | None = None,
        task_id: str | None = None,
        *,
        audit_error: str | None = None,
    ) -> ExecutionResult:
        return ExecutionResult(
            decision=decision,
            executed=executed,
            process=process,
            task_id=task_id,
            audit_status=(
                AuditStatus.FAILED
                if audit_error is not None
                else AuditStatus.RECORDED
            ),
            audit_error=audit_error,
        )

    def _try_record_audit(self, *args, **kwargs) -> str | None:
        try:
            self._record_audit(*args, **kwargs)
        except Exception as error:
            return f"Audit sink failed ({type(error).__name__})."
        return None

    @staticmethod
    def _denial(reason: str, policy: str) -> ExecutionDecision:
        return ExecutionDecision(
            decision=ExecutionDecisionType.DENY,
            reason=reason,
            policy=policy,
            required_approval=False,
        )

    def _record_audit(
        self,
        request: ExecutionRequest,
        decision: ExecutionDecision,
        executed: bool,
        exit_code: int | None,
        *,
        attempted: bool = False,
        failure: str | None = None,
        task_id: str | None = None,
        parameter_digest: str | None = None,
    ) -> None:
        self._audit_sink.record(
            ExecutionAuditRecord(
                action=request.action,
                target=request.target,
                scope=request.scope,
                actor=request.actor,
                risk=request.risk,
                requested_capabilities=request.requested_capabilities,
                evidence=request.evidence,
                decision=decision.decision,
                reason=decision.reason,
                policy=decision.policy,
                required_approval=decision.required_approval,
                executed=executed,
                exit_code=exit_code,
                attempted=attempted,
                failure=failure,
                task_id=task_id,
                parameter_digest=parameter_digest,
            )
        )

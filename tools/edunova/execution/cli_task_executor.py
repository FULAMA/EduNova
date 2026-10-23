from pathlib import Path
from typing import Any

from tools.edunova.execution.audit_sink import ExecutionAuditSink
from tools.edunova.execution.default_policy import DefaultExecutionPolicy
from tools.edunova.execution.memory_audit_sink import InMemoryExecutionAuditSink
from tools.edunova.execution.request import ExecutionRequest
from tools.edunova.execution.scope import ExecutionScope
from tools.edunova.execution.service import ExecutionResult, ExecutionService
from tools.edunova.execution.task_registry import ExecutionTaskRegistry
from tools.edunova.infrastructure.process_runner import ProcessRunner


_TASK_SCOPE = {
    "pytest.run": ExecutionScope.TEST_SUITE,
    "ruff.check": ExecutionScope.PROJECT,
    "mypy.check": ExecutionScope.PROJECT,
    "bandit.scan": ExecutionScope.PROJECT,
    "git.status": ExecutionScope.GIT,
    "git.branch": ExecutionScope.GIT,
}


def run_cli_task(
    process_runner: ProcessRunner,
    task_id: str,
    parameters: dict[str, Any],
    project_root: Path,
    *,
    actor: str = "local-cli",
    audit_sink: ExecutionAuditSink | None = None,
) -> ExecutionResult:
    registry = ExecutionTaskRegistry()
    task = registry.get(task_id)
    request = ExecutionRequest(
        action=task.action,
        target=str(project_root.resolve()),
        scope=_TASK_SCOPE[task_id],
        actor=actor,
        risk=task.risk,
        requested_capabilities=task.capabilities,
        evidence=("Explicitly registered CLI task",),
        project_root=project_root,
    )
    service = ExecutionService(
        policy=DefaultExecutionPolicy(),
        runner=process_runner,
        audit_sink=audit_sink or InMemoryExecutionAuditSink(),
        task_registry=registry,
    )
    result = service.execute(request, task_id, parameters)
    return result

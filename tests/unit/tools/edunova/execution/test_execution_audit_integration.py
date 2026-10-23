from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock

from tools.edunova.execution.action import ExecutionAction
from tools.edunova.execution.capability import ExecutionCapability
from tools.edunova.execution.default_policy import DefaultExecutionPolicy
from tools.edunova.execution.decision import ExecutionDecisionType
from tools.edunova.execution.memory_audit_sink import InMemoryExecutionAuditSink
from tools.edunova.execution.request import ExecutionRequest
from tools.edunova.execution.risk import ExecutionRisk
from tools.edunova.execution.scope import ExecutionScope
from tools.edunova.execution.service import ExecutionService


def test_policy_denial_is_audited_and_no_process_starts() -> None:
    runner = Mock()
    sink = InMemoryExecutionAuditSink()
    service = ExecutionService(DefaultExecutionPolicy(), runner, sink)
    request = ExecutionRequest(
        action=ExecutionAction.READ,
        target="database",
        scope=ExecutionScope.DATABASE,
        actor="test",
        risk=ExecutionRisk.LOW,
        requested_capabilities=frozenset({ExecutionCapability.FILESYSTEM_READ}),
    )
    result = service.execute(request, "pytest.run", {"paths": ["tests"], "options": []})
    assert result.executed is False
    assert result.decision.decision is ExecutionDecisionType.DENY
    runner.run.assert_not_called()
    assert sink.records[0].decision is ExecutionDecisionType.DENY
    assert sink.records[0].executed is False


def test_reviewed_operation_is_not_executable_without_local_confirmation_ui() -> None:
    runner = Mock()
    sink = InMemoryExecutionAuditSink()

    class ReviewPolicy:
        def evaluate(self, request: ExecutionRequest):
            from tools.edunova.execution.decision import ExecutionDecision

            return ExecutionDecision(
                ExecutionDecisionType.REVIEW,
                "explicit review required",
                "test",
                True,
            )

    service = ExecutionService(ReviewPolicy(), runner, sink)
    request = ExecutionRequest(
        action=ExecutionAction.TEST,
        target=str(Path.cwd()),
        scope=ExecutionScope.TEST_SUITE,
        actor="test",
        risk=ExecutionRisk.MEDIUM,
        requested_capabilities=frozenset({
            ExecutionCapability.FILESYSTEM_READ,
            ExecutionCapability.PROCESS_EXECUTE,
        }),
        project_root=Path.cwd(),
    )
    result = service.execute(
        request,
        "pytest.run",
        {"paths": ["tests"], "options": []},
    )
    assert result.executed is False
    assert "confirmation" in result.decision.reason
    runner.run.assert_not_called()
    assert sink.records[0].decision is ExecutionDecisionType.DENY
    assert sink.records[0].executed is False

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from tools.edunova.execution.action import ExecutionAction
from tools.edunova.execution.audit import ExecutionAuditRecord
from tools.edunova.execution.audit_sink import ExecutionAuditSink
from tools.edunova.execution.capability import ExecutionCapability
from tools.edunova.execution.decision import ExecutionDecision, ExecutionDecisionType
from tools.edunova.execution.request import ExecutionRequest
from tools.edunova.execution.risk import ExecutionRisk
from tools.edunova.execution.scope import ExecutionScope
from tools.edunova.execution.service import ExecutionService
from tools.edunova.execution.task_registry import ExecutionTaskRegistry


class FakePolicy:
    def __init__(self, decision: ExecutionDecision | None = None, error: Exception | None = None) -> None:
        self.decision = decision or ExecutionDecision(
            ExecutionDecisionType.ALLOW, "policy permits", "test", False
        )
        self.error = error

    def evaluate(self, request: ExecutionRequest) -> ExecutionDecision:
        if self.error:
            raise self.error
        return self.decision


class FakeRunner:
    def __init__(self, returncode: int = 0) -> None:
        self.calls: list[tuple[tuple[str, ...], Path | None]] = []
        self.returncode = returncode

    def run(self, command: tuple[str, ...], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        self.calls.append((tuple(command), cwd))
        return subprocess.CompletedProcess(command, self.returncode, "out", "")


class FakeAuditSink(ExecutionAuditSink):
    def __init__(self) -> None:
        self.records: list[ExecutionAuditRecord] = []

    def record(self, audit: ExecutionAuditRecord) -> None:
        self.records.append(audit)


def make_request(
    action: ExecutionAction = ExecutionAction.TEST,
    *,
    scope: ExecutionScope = ExecutionScope.TEST_SUITE,
    risk: ExecutionRisk = ExecutionRisk.MEDIUM,
    capabilities: frozenset[ExecutionCapability] | None = None,
    root: Path | None = None,
) -> ExecutionRequest:
    if capabilities is None:
        capabilities = frozenset({
            ExecutionCapability.FILESYSTEM_READ,
            ExecutionCapability.PROCESS_EXECUTE,
        })
    return ExecutionRequest(
        action=action,
        target=str(root or Path.cwd()),
        scope=scope,
        actor="test",
        risk=risk,
        requested_capabilities=capabilities,
        evidence=("registered task test",),
        project_root=root or Path.cwd(),
    )


def make_service(
    *,
    policy: FakePolicy | None = None,
    runner: FakeRunner | None = None,
    registry: ExecutionTaskRegistry | None = None,
    confirmation=None,
) -> tuple[ExecutionService, FakeRunner, FakeAuditSink]:
    actual_runner = runner or FakeRunner()
    audit = FakeAuditSink()
    service = ExecutionService(
        policy=policy or FakePolicy(),
        runner=actual_runner,
        audit_sink=audit,
        task_registry=registry,
        local_confirmation=confirmation,
    )
    return service, actual_runner, audit


def test_registered_pytest_task_builds_argv_and_audits_result() -> None:
    service, runner, audit = make_service()

    result = service.execute(
        make_request(),
        "pytest.run",
        {"paths": ["tests"], "options": ["-q"]},
    )

    assert result.executed is True
    assert result.task_id == "pytest.run"
    assert len(runner.calls) == 1
    assert runner.calls[0][1] == Path.cwd()
    argv = runner.calls[0][0]
    assert argv[:3] == (sys.executable, "-m", "pytest")
    assert "--basetemp" in argv
    assert argv[-2:] == ("tests", "-q")
    assert audit.records[0].executed is False
    record = audit.records[1]
    assert record.task_id == "pytest.run"
    assert len(record.parameter_digest or "") == 64
    assert record.executed is True
    assert record.exit_code == 0


def test_unknown_task_is_denied_audited_and_never_runs() -> None:
    service, runner, audit = make_service()
    result = service.execute(make_request(), "python.run", {"code": "print(1)"})
    assert result.executed is False
    assert result.decision.decision is ExecutionDecisionType.DENY
    assert runner.calls == []
    assert audit.records[0].task_id == "python.run"
    assert audit.records[0].executed is False


def test_legacy_raw_argv_is_not_a_registered_task() -> None:
    service, runner, audit = make_service()
    result = service.execute(make_request(), ["python", "-c", "raise SystemExit(9)"])
    assert result.executed is False
    assert runner.calls == []
    assert audit.records[0].decision is ExecutionDecisionType.DENY


def test_read_action_cannot_execute_registered_process_task() -> None:
    service, runner, audit = make_service()
    request = make_request(
        ExecutionAction.READ,
        scope=ExecutionScope.FILE,
        risk=ExecutionRisk.LOW,
        capabilities=frozenset({ExecutionCapability.FILESYSTEM_READ}),
    )
    result = service.execute(request, "pytest.run", {"paths": ["tests"], "options": []})
    assert result.executed is False
    assert runner.calls == []
    assert audit.records[0].decision is ExecutionDecisionType.DENY


def test_task_with_incompatible_action_is_denied_before_policy() -> None:
    service, runner, audit = make_service()
    request = make_request(ExecutionAction.QUALITY, scope=ExecutionScope.PROJECT)
    result = service.execute(request, "pytest.run", {"paths": ["tests"], "options": []})
    assert result.executed is False
    assert runner.calls == []
    assert audit.records[0].policy == "task-registry"


def test_allow_policy_cannot_bypass_invalid_arguments_or_scope() -> None:
    service, runner, audit = make_service()
    result = service.execute(
        make_request(), "pytest.run",
        {"paths": ["tests"], "options": ["--basetemp", "C:/outside"]},
    )
    assert result.decision.decision is ExecutionDecisionType.DENY
    assert runner.calls == []
    assert audit.records[0].executed is False


def test_paths_outside_root_and_missing_paths_are_denied() -> None:
    service, runner, audit = make_service()
    for path in ("../outside", "missing-tests"):
        result = service.execute(
            make_request(), "pytest.run", {"paths": [path], "options": []}
        )
        assert result.executed is False
    assert runner.calls == []
    assert len(audit.records) == 2


def test_missing_required_capability_is_denied() -> None:
    service, runner, audit = make_service()
    request = make_request(capabilities=frozenset({ExecutionCapability.FILESYSTEM_READ}))
    result = service.execute(request, "pytest.run", {"paths": ["tests"], "options": []})
    assert result.executed is False
    assert runner.calls == []
    assert "capabilities" in audit.records[0].reason


def test_policy_denial_is_audited_without_running() -> None:
    denial = ExecutionDecision(ExecutionDecisionType.DENY, "policy denied", "test", False)
    service, runner, audit = make_service(policy=FakePolicy(denial))
    result = service.execute(make_request(), "pytest.run", {"paths": ["tests"], "options": []})
    assert result.executed is False
    assert result.decision is denial
    assert runner.calls == []
    assert audit.records[0].decision is ExecutionDecisionType.DENY


def test_policy_exception_fails_closed_and_is_audited() -> None:
    service, runner, audit = make_service(policy=FakePolicy(error=RuntimeError("policy down")))
    result = service.execute(make_request(), "pytest.run", {"paths": ["tests"], "options": []})
    assert result.executed is False
    assert result.decision.decision is ExecutionDecisionType.DENY
    assert "failed closed" in result.decision.reason
    assert runner.calls == []
    assert audit.records[0].policy == "policy-error"


def test_review_decision_is_refused_without_local_confirmation() -> None:
    review = ExecutionDecision(ExecutionDecisionType.REVIEW, "review", "test", True)
    service, runner, audit = make_service(policy=FakePolicy(review))
    result = service.execute(make_request(), "pytest.run", {"paths": ["tests"], "options": []})
    assert result.executed is False
    assert result.decision.decision is ExecutionDecisionType.DENY
    assert runner.calls == []
    assert audit.records[0].executed is False


def test_process_exit_code_is_preserved_and_recorded() -> None:
    service, runner, audit = make_service(runner=FakeRunner(returncode=7))
    result = service.execute(make_request(), "pytest.run", {"paths": ["tests"], "options": []})
    assert result.process is not None and result.process.returncode == 7
    assert runner.calls
    assert audit.records[0].executed is False
    assert audit.records[1].exit_code == 7
    assert audit.records[1].task_id == "pytest.run"


class ConfirmOperation:
    def __init__(self, approve: bool) -> None:
        self.approve = approve
        self.operations = []

    def confirm(self, operation) -> bool:
        self.operations.append(operation)
        return self.approve


def test_local_confirmation_is_bound_to_resolved_task_details() -> None:
    from tools.edunova.execution.local_confirmation import LocalOperationSummary

    review = ExecutionDecision(ExecutionDecisionType.REVIEW, "review", "test", True)
    confirmation = ConfirmOperation(True)
    runner = FakeRunner()
    audit = FakeAuditSink()
    service = ExecutionService(
        policy=FakePolicy(review),
        runner=runner,
        audit_sink=audit,
        local_confirmation=confirmation,
    )

    result = service.execute(
        make_request(), "pytest.run", {"paths": ["tests"], "options": []}
    )

    assert result.executed is True
    assert len(confirmation.operations) == 1
    operation = confirmation.operations[0]
    assert isinstance(operation, LocalOperationSummary)
    assert operation.task_id == "pytest.run"
    assert operation.project_root == Path.cwd()
    assert operation.parameters == {"paths": ("tests",), "options": ()}
    assert audit.records[0].decision is ExecutionDecisionType.REVIEW
    assert audit.records[0].required_approval is True


def test_declined_local_confirmation_is_audited_without_process() -> None:
    review = ExecutionDecision(ExecutionDecisionType.REVIEW, "review", "test", True)
    confirmation = ConfirmOperation(False)
    service, runner, audit = make_service(
        policy=FakePolicy(review),
        confirmation=confirmation,
    )
    result = service.execute(
        make_request(), "pytest.run", {"paths": ["tests"], "options": []}
    )
    assert result.executed is False
    assert runner.calls == []
    assert audit.records[0].decision is ExecutionDecisionType.DENY

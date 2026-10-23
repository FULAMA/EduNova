from __future__ import annotations

import pytest

from tools.edunova.execution.action import ExecutionAction
from tools.edunova.execution.action_constraints import constraints_for
from tools.edunova.execution.capability import ExecutionCapability
from tools.edunova.execution.capability_matrix import allowed_capabilities
from tools.edunova.execution.default_policy import DefaultExecutionPolicy
from tools.edunova.execution.decision import ExecutionDecisionType
from tools.edunova.execution.request import ExecutionRequest
from tools.edunova.execution.risk import ExecutionRisk
from tools.edunova.execution.scope import ExecutionScope


def make_request(
    action: ExecutionAction,
    capabilities: frozenset[ExecutionCapability] | None = None,
) -> ExecutionRequest:
    if capabilities is None:
        capabilities = allowed_capabilities(action)

    scope = next(iter(constraints_for(action).scopes))

    return ExecutionRequest(
        action=action,
        target="tests/",
        scope=scope,
        actor="test",
        risk=constraints_for(action).max_risk,
        requested_capabilities=capabilities,
        evidence=("observed",),
    )


@pytest.mark.parametrize(
    "action",
    [
        ExecutionAction.READ,
        ExecutionAction.SCAN,
        ExecutionAction.ANALYZE,
        ExecutionAction.PLAN,
        ExecutionAction.TEST,
        ExecutionAction.QUALITY,
        ExecutionAction.SECURITY,
        ExecutionAction.GENERATE,
    ],
)
def test_safe_actions_are_allowed(action: ExecutionAction) -> None:
    policy = DefaultExecutionPolicy()

    decision = policy.evaluate(make_request(action))

    assert decision.decision is ExecutionDecisionType.ALLOW
    assert decision.required_approval is False


@pytest.mark.parametrize(
    "action",
    [
        ExecutionAction.MODIFY,
        ExecutionAction.DELETE,
        ExecutionAction.INSTALL,
        ExecutionAction.MIGRATE,
        ExecutionAction.GIT_COMMIT,
        ExecutionAction.GIT_PUSH,
        ExecutionAction.SHELL,
    ],
)
def test_sensitive_actions_require_review(
    action: ExecutionAction,
) -> None:
    policy = DefaultExecutionPolicy()

    decision = policy.evaluate(make_request(action))

    assert decision.decision is ExecutionDecisionType.REVIEW
    assert decision.required_approval is True


def test_evidence_is_preserved() -> None:
    policy = DefaultExecutionPolicy()

    decision = policy.evaluate(
        make_request(ExecutionAction.TEST)
    )

    assert decision.evidence == ("observed",)


def test_test_action_with_process_capability_is_allowed() -> None:
    policy = DefaultExecutionPolicy()

    request = make_request(
        ExecutionAction.TEST,
        frozenset(
            {
                ExecutionCapability.FILESYSTEM_READ,
                ExecutionCapability.PROCESS_EXECUTE,
            }
        ),
    )

    decision = policy.evaluate(request)

    assert decision.decision is ExecutionDecisionType.ALLOW


def test_test_action_with_write_capability_is_denied() -> None:
    policy = DefaultExecutionPolicy()

    request = make_request(
        ExecutionAction.TEST,
        frozenset(
            {
                ExecutionCapability.FILESYSTEM_READ,
                ExecutionCapability.PROCESS_EXECUTE,
                ExecutionCapability.FILESYSTEM_WRITE,
            }
        ),
    )

    decision = policy.evaluate(request)

    assert decision.decision is ExecutionDecisionType.DENY
    assert decision.required_approval is False
    assert "filesystem.write" in decision.reason


def test_read_action_with_database_write_is_denied() -> None:
    policy = DefaultExecutionPolicy()

    request = make_request(
        ExecutionAction.READ,
        frozenset(
            {ExecutionCapability.DATABASE_WRITE}
        ),
    )

    decision = policy.evaluate(request)

    assert decision.decision is ExecutionDecisionType.DENY
    assert "database.write" in decision.reason


def test_invalid_scope_is_denied() -> None:
    policy = DefaultExecutionPolicy()

    request = ExecutionRequest(
        action=ExecutionAction.READ,
        target="database",
        scope=ExecutionScope.DATABASE,
        actor="test",
        risk=ExecutionRisk.LOW,
        requested_capabilities=frozenset(
            {ExecutionCapability.FILESYSTEM_READ}
        ),
        evidence=("observed",),
    )

    decision = policy.evaluate(request)

    assert decision.decision is ExecutionDecisionType.DENY
    assert "scope" in decision.reason


def test_excessive_risk_is_denied() -> None:
    policy = DefaultExecutionPolicy()

    request = ExecutionRequest(
        action=ExecutionAction.READ,
        target="project",
        scope=ExecutionScope.PROJECT,
        actor="test",
        risk=ExecutionRisk.HIGH,
        requested_capabilities=frozenset(
            {ExecutionCapability.FILESYSTEM_READ}
        ),
        evidence=("observed",),
    )

    decision = policy.evaluate(request)

    assert decision.decision is ExecutionDecisionType.DENY
    assert "risk" in decision.reason.lower()


def test_review_action_with_valid_high_risk_remains_review() -> None:
    policy = DefaultExecutionPolicy()

    request = ExecutionRequest(
        action=ExecutionAction.MODIFY,
        target="src/example.py",
        scope=ExecutionScope.FILE,
        actor="test",
        risk=ExecutionRisk.HIGH,
        requested_capabilities=frozenset(
            {
                ExecutionCapability.FILESYSTEM_READ,
                ExecutionCapability.FILESYSTEM_WRITE,
            }
        ),
        evidence=("observed",),
    )

    decision = policy.evaluate(request)

    assert decision.decision is ExecutionDecisionType.REVIEW
    assert decision.required_approval is True

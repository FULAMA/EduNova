import pytest

from tools.edunova.execution.action import ExecutionAction
from tools.edunova.execution.capability import ExecutionCapability
from tools.edunova.execution.decision import (
    ExecutionDecision,
    ExecutionDecisionType,
)
from tools.edunova.execution.request import ExecutionRequest
from tools.edunova.execution.risk import ExecutionRisk
from tools.edunova.execution.scope import ExecutionScope


def make_request() -> ExecutionRequest:
    return ExecutionRequest(
        action=ExecutionAction.TEST,
        target="pytest",
        scope=ExecutionScope.TEST_SUITE,
        actor="cli",
        risk=ExecutionRisk.LOW,
        requested_capabilities=frozenset(
            {
                ExecutionCapability.PROCESS_EXECUTE,
            }
        ),
    )


def test_execution_request_is_valid() -> None:
    request = make_request()

    assert request.action is ExecutionAction.TEST
    assert request.target == "pytest"
    assert request.scope is ExecutionScope.TEST_SUITE
    assert request.actor == "cli"
    assert request.risk is ExecutionRisk.LOW


def test_execution_request_rejects_empty_target() -> None:
    with pytest.raises(ValueError, match="target"):
        ExecutionRequest(
            action=ExecutionAction.TEST,
            target=" ",
            scope=ExecutionScope.TEST_SUITE,
            actor="cli",
            risk=ExecutionRisk.LOW,
            requested_capabilities=frozenset(),
        )


def test_execution_request_rejects_empty_actor() -> None:
    with pytest.raises(ValueError, match="actor"):
        ExecutionRequest(
            action=ExecutionAction.TEST,
            target="pytest",
            scope=ExecutionScope.TEST_SUITE,
            actor=" ",
            risk=ExecutionRisk.LOW,
            requested_capabilities=frozenset(),
        )


def test_execution_request_is_immutable() -> None:
    request = make_request()

    with pytest.raises(Exception):
        request.target = "ruff"  # type: ignore[misc]


def test_allow_decision_does_not_require_approval() -> None:
    decision = ExecutionDecision(
        decision=ExecutionDecisionType.ALLOW,
        reason="Read-only test execution.",
        policy="default",
        required_approval=False,
    )

    assert decision.decision is ExecutionDecisionType.ALLOW
    assert decision.required_approval is False


def test_review_decision_requires_approval() -> None:
    decision = ExecutionDecision(
        decision=ExecutionDecisionType.REVIEW,
        reason="Project modification requires review.",
        policy="default",
        required_approval=True,
    )

    assert decision.decision is ExecutionDecisionType.REVIEW
    assert decision.required_approval is True


def test_deny_decision_does_not_require_approval() -> None:
    decision = ExecutionDecision(
        decision=ExecutionDecisionType.DENY,
        reason="Destructive action denied.",
        policy="default",
        required_approval=False,
    )

    assert decision.decision is ExecutionDecisionType.DENY
    assert decision.required_approval is False


@pytest.mark.parametrize(
    "decision_type",
    [
        ExecutionDecisionType.ALLOW,
        ExecutionDecisionType.REVIEW,
        ExecutionDecisionType.DENY,
    ],
)
def test_all_execution_decisions_are_explicit(
    decision_type: ExecutionDecisionType,
) -> None:
    required_approval = decision_type is ExecutionDecisionType.REVIEW

    decision = ExecutionDecision(
        decision=decision_type,
        reason="Explicit decision.",
        policy="default",
        required_approval=required_approval,
    )

    assert decision.decision is decision_type

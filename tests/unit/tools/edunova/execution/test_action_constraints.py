from __future__ import annotations

import pytest

from tools.edunova.execution.action import ExecutionAction
from tools.edunova.execution.action_constraints import (
    ACTION_CONSTRAINTS,
    constraints_for,
)
from tools.edunova.execution.risk import ExecutionRisk
from tools.edunova.execution.scope import ExecutionScope


@pytest.mark.parametrize(
    "action",
    list(ExecutionAction),
)
def test_every_action_has_constraints(
    action: ExecutionAction,
) -> None:
    assert action in ACTION_CONSTRAINTS

    constraints = constraints_for(action)

    assert constraints.scopes
    assert constraints.max_risk in ExecutionRisk


@pytest.mark.parametrize(
    "action,scope",
    [
        (ExecutionAction.READ, ExecutionScope.FILE),
        (ExecutionAction.READ, ExecutionScope.PROJECT),
        (ExecutionAction.SCAN, ExecutionScope.PROJECT),
        (ExecutionAction.SCAN, ExecutionScope.GIT),
        (ExecutionAction.TEST, ExecutionScope.TEST_SUITE),
        (ExecutionAction.TEST, ExecutionScope.PROJECT),
        (ExecutionAction.MIGRATE, ExecutionScope.DATABASE),
        (ExecutionAction.GIT_COMMIT, ExecutionScope.GIT),
        (ExecutionAction.SHELL, ExecutionScope.SYSTEM),
    ],
)
def test_valid_action_scope_pairs(
    action: ExecutionAction,
    scope: ExecutionScope,
) -> None:
    assert scope in constraints_for(action).scopes


@pytest.mark.parametrize(
    "action,scope",
    [
        (ExecutionAction.READ, ExecutionScope.DATABASE),
        (ExecutionAction.SCAN, ExecutionScope.DATABASE),
        (ExecutionAction.TEST, ExecutionScope.DATABASE),
        (ExecutionAction.MIGRATE, ExecutionScope.FILE),
        (ExecutionAction.GIT_COMMIT, ExecutionScope.FILE),
        (ExecutionAction.GIT_PUSH, ExecutionScope.DATABASE),
    ],
)
def test_invalid_action_scope_pairs(
    action: ExecutionAction,
    scope: ExecutionScope,
) -> None:
    assert scope not in constraints_for(action).scopes


def test_read_has_low_risk_ceiling() -> None:
    assert (
        constraints_for(ExecutionAction.READ).max_risk
        is ExecutionRisk.LOW
    )


def test_modify_allows_high_risk_but_remains_review_action() -> None:
    assert (
        constraints_for(ExecutionAction.MODIFY).max_risk
        is ExecutionRisk.HIGH
    )

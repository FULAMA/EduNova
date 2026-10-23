from __future__ import annotations

from dataclasses import dataclass

from tools.edunova.execution.action import ExecutionAction
from tools.edunova.execution.capability import ExecutionCapability
from tools.edunova.execution.risk import ExecutionRisk
from tools.edunova.execution.scope import ExecutionScope


@dataclass(frozen=True)
class ActionConstraints:
    scopes: frozenset[ExecutionScope]
    max_risk: ExecutionRisk


ACTION_CONSTRAINTS: dict[ExecutionAction, ActionConstraints] = {
    ExecutionAction.READ: ActionConstraints(
        scopes=frozenset(
            {
                ExecutionScope.FILE,
                ExecutionScope.DIRECTORY,
                ExecutionScope.PROJECT,
            }
        ),
        max_risk=ExecutionRisk.LOW,
    ),
    ExecutionAction.SCAN: ActionConstraints(
        scopes=frozenset(
            {
                ExecutionScope.PROJECT,
                ExecutionScope.GIT,
            }
        ),
        max_risk=ExecutionRisk.LOW,
    ),
    ExecutionAction.ANALYZE: ActionConstraints(
        scopes=frozenset(
            {
                ExecutionScope.FILE,
                ExecutionScope.DIRECTORY,
                ExecutionScope.PROJECT,
                ExecutionScope.GIT,
            }
        ),
        max_risk=ExecutionRisk.LOW,
    ),
    ExecutionAction.PLAN: ActionConstraints(
        scopes=frozenset(
            {
                ExecutionScope.FILE,
                ExecutionScope.DIRECTORY,
                ExecutionScope.PROJECT,
            }
        ),
        max_risk=ExecutionRisk.LOW,
    ),
    ExecutionAction.TEST: ActionConstraints(
        scopes=frozenset(
            {
                ExecutionScope.TEST_SUITE,
                ExecutionScope.PROJECT,
            }
        ),
        max_risk=ExecutionRisk.MEDIUM,
    ),
    ExecutionAction.QUALITY: ActionConstraints(
        scopes=frozenset(
            {
                ExecutionScope.TEST_SUITE,
                ExecutionScope.PROJECT,
            }
        ),
        max_risk=ExecutionRisk.MEDIUM,
    ),
    ExecutionAction.SECURITY: ActionConstraints(
        scopes=frozenset(
            {
                ExecutionScope.TEST_SUITE,
                ExecutionScope.PROJECT,
                ExecutionScope.EXTERNAL,
            }
        ),
        max_risk=ExecutionRisk.HIGH,
    ),
    ExecutionAction.GENERATE: ActionConstraints(
        scopes=frozenset(
            {
                ExecutionScope.FILE,
                ExecutionScope.DIRECTORY,
                ExecutionScope.PROJECT,
            }
        ),
        max_risk=ExecutionRisk.MEDIUM,
    ),
    ExecutionAction.MODIFY: ActionConstraints(
        scopes=frozenset(
            {
                ExecutionScope.FILE,
                ExecutionScope.DIRECTORY,
                ExecutionScope.PROJECT,
            }
        ),
        max_risk=ExecutionRisk.HIGH,
    ),
    ExecutionAction.DELETE: ActionConstraints(
        scopes=frozenset(
            {
                ExecutionScope.FILE,
                ExecutionScope.DIRECTORY,
                ExecutionScope.PROJECT,
            }
        ),
        max_risk=ExecutionRisk.HIGH,
    ),
    ExecutionAction.INSTALL: ActionConstraints(
        scopes=frozenset(
            {
                ExecutionScope.PROJECT,
                ExecutionScope.EXTERNAL,
            }
        ),
        max_risk=ExecutionRisk.HIGH,
    ),
    ExecutionAction.MIGRATE: ActionConstraints(
        scopes=frozenset(
            {
                ExecutionScope.DATABASE,
                ExecutionScope.PROJECT,
            }
        ),
        max_risk=ExecutionRisk.HIGH,
    ),
    ExecutionAction.GIT_COMMIT: ActionConstraints(
        scopes=frozenset(
            {ExecutionScope.GIT}
        ),
        max_risk=ExecutionRisk.HIGH,
    ),
    ExecutionAction.GIT_PUSH: ActionConstraints(
        scopes=frozenset(
            {
                ExecutionScope.GIT,
                ExecutionScope.EXTERNAL,
            }
        ),
        max_risk=ExecutionRisk.HIGH,
    ),
    ExecutionAction.SHELL: ActionConstraints(
        scopes=frozenset(
            {
                ExecutionScope.PROJECT,
                ExecutionScope.SYSTEM,
                ExecutionScope.EXTERNAL,
            }
        ),
        max_risk=ExecutionRisk.HIGH,
    ),
}


def constraints_for(
    action: ExecutionAction,
) -> ActionConstraints:
    return ACTION_CONSTRAINTS[action]


def capability_is_allowed(
    action: ExecutionAction,
    capability: ExecutionCapability,
) -> bool:
    from tools.edunova.execution.capability_matrix import (
        allowed_capabilities,
    )

    return capability in allowed_capabilities(action)

from __future__ import annotations

import pytest

from tools.edunova.execution.action import ExecutionAction
from tools.edunova.execution.capability import ExecutionCapability
from tools.edunova.execution.capability_matrix import allowed_capabilities


@pytest.mark.parametrize(
    "action,expected",
    [
        (
            ExecutionAction.READ,
            {ExecutionCapability.FILESYSTEM_READ},
        ),
        (
            ExecutionAction.SCAN,
            {
                ExecutionCapability.FILESYSTEM_READ,
                ExecutionCapability.GIT_READ,
                    ExecutionCapability.PROCESS_EXECUTE,
            },
        ),
        (
            ExecutionAction.TEST,
            {
                ExecutionCapability.FILESYSTEM_READ,
                ExecutionCapability.PROCESS_EXECUTE,
            },
        ),
        (
            ExecutionAction.MODIFY,
            {
                ExecutionCapability.FILESYSTEM_READ,
                ExecutionCapability.FILESYSTEM_WRITE,
            },
        ),
        (
            ExecutionAction.MIGRATE,
            {
                ExecutionCapability.FILESYSTEM_READ,
                ExecutionCapability.FILESYSTEM_WRITE,
                ExecutionCapability.DATABASE_READ,
                ExecutionCapability.DATABASE_WRITE,
            },
        ),
        (
            ExecutionAction.GIT_PUSH,
            {
                ExecutionCapability.GIT_READ,
                ExecutionCapability.GIT_WRITE,
                ExecutionCapability.NETWORK_ACCESS,
            },
        ),
    ],
)
def test_action_capability_mapping(
    action: ExecutionAction,
    expected: set[ExecutionCapability],
) -> None:
    assert allowed_capabilities(action) == frozenset(expected)


def test_every_execution_action_has_a_capability_contract() -> None:
    from tools.edunova.execution.capability_matrix import ACTION_CAPABILITIES

    assert set(ACTION_CAPABILITIES) == set(ExecutionAction)


def test_test_action_cannot_request_write_capability() -> None:
    capabilities = allowed_capabilities(ExecutionAction.TEST)

    assert ExecutionCapability.FILESYSTEM_WRITE not in capabilities
    assert ExecutionCapability.DATABASE_WRITE not in capabilities
    assert ExecutionCapability.GIT_WRITE not in capabilities


def test_read_action_is_read_only() -> None:
    capabilities = allowed_capabilities(ExecutionAction.READ)

    assert capabilities == frozenset(
        {ExecutionCapability.FILESYSTEM_READ}
    )

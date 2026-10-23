from __future__ import annotations

from tools.edunova.execution.action import ExecutionAction
from tools.edunova.execution.capability import ExecutionCapability


ACTION_CAPABILITIES: dict[
    ExecutionAction,
    frozenset[ExecutionCapability],
] = {
    ExecutionAction.READ: frozenset(
        {ExecutionCapability.FILESYSTEM_READ}
    ),
    ExecutionAction.SCAN: frozenset(
        {
            ExecutionCapability.FILESYSTEM_READ,
            ExecutionCapability.GIT_READ,
            ExecutionCapability.PROCESS_EXECUTE,
        }
    ),
    ExecutionAction.ANALYZE: frozenset(
        {
            ExecutionCapability.FILESYSTEM_READ,
            ExecutionCapability.GIT_READ,
        }
    ),
    ExecutionAction.PLAN: frozenset(
        {ExecutionCapability.FILESYSTEM_READ}
    ),
    ExecutionAction.TEST: frozenset(
        {
            ExecutionCapability.FILESYSTEM_READ,
            ExecutionCapability.PROCESS_EXECUTE,
        }
    ),
    ExecutionAction.QUALITY: frozenset(
        {
            ExecutionCapability.FILESYSTEM_READ,
            ExecutionCapability.PROCESS_EXECUTE,
        }
    ),
    ExecutionAction.SECURITY: frozenset(
        {
            ExecutionCapability.FILESYSTEM_READ,
            ExecutionCapability.PROCESS_EXECUTE,
        }
    ),
    ExecutionAction.GENERATE: frozenset(
        {ExecutionCapability.FILESYSTEM_READ}
    ),
    ExecutionAction.MODIFY: frozenset(
        {
            ExecutionCapability.FILESYSTEM_READ,
            ExecutionCapability.FILESYSTEM_WRITE,
        }
    ),
    ExecutionAction.DELETE: frozenset(
        {
            ExecutionCapability.FILESYSTEM_READ,
            ExecutionCapability.FILESYSTEM_WRITE,
        }
    ),
    ExecutionAction.INSTALL: frozenset(
        {
            ExecutionCapability.PROCESS_EXECUTE,
            ExecutionCapability.NETWORK_ACCESS,
        }
    ),
    ExecutionAction.MIGRATE: frozenset(
        {
            ExecutionCapability.FILESYSTEM_READ,
            ExecutionCapability.FILESYSTEM_WRITE,
            ExecutionCapability.DATABASE_READ,
            ExecutionCapability.DATABASE_WRITE,
        }
    ),
    ExecutionAction.GIT_COMMIT: frozenset(
        {
            ExecutionCapability.GIT_READ,
            ExecutionCapability.GIT_WRITE,
        }
    ),
    ExecutionAction.GIT_PUSH: frozenset(
        {
            ExecutionCapability.GIT_READ,
            ExecutionCapability.GIT_WRITE,
            ExecutionCapability.NETWORK_ACCESS,
        }
    ),
    ExecutionAction.SHELL: frozenset(
        {ExecutionCapability.PROCESS_EXECUTE}
    ),
}


def allowed_capabilities(
    action: ExecutionAction,
) -> frozenset[ExecutionCapability]:
    return ACTION_CAPABILITIES[action]

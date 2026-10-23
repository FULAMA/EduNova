from __future__ import annotations

from tools.edunova.execution.action import ExecutionAction
from tools.edunova.execution.action_constraints import constraints_for
from tools.edunova.execution.capability_matrix import allowed_capabilities
from tools.edunova.execution.decision import (
    ExecutionDecision,
    ExecutionDecisionType,
)
from tools.edunova.execution.policy import ExecutionPolicy
from tools.edunova.execution.request import ExecutionRequest


class DefaultExecutionPolicy(ExecutionPolicy):
    _ALLOW_ACTIONS = frozenset(
        {
            ExecutionAction.READ,
            ExecutionAction.SCAN,
            ExecutionAction.ANALYZE,
            ExecutionAction.PLAN,
            ExecutionAction.TEST,
            ExecutionAction.QUALITY,
            ExecutionAction.SECURITY,
            ExecutionAction.GENERATE,
        }
    )

    _REVIEW_ACTIONS = frozenset(
        {
            ExecutionAction.MODIFY,
            ExecutionAction.DELETE,
            ExecutionAction.INSTALL,
            ExecutionAction.MIGRATE,
            ExecutionAction.GIT_COMMIT,
            ExecutionAction.GIT_PUSH,
            ExecutionAction.SHELL,
        }
    )

    def evaluate(
        self,
        request: ExecutionRequest,
    ) -> ExecutionDecision:
        constraints = constraints_for(request.action)

        if request.scope not in constraints.scopes:
            return ExecutionDecision(
                decision=ExecutionDecisionType.DENY,
                reason=(
                    f"Action {request.action.value} is not permitted "
                    f"for scope {request.scope.value}."
                ),
                policy="default",
                required_approval=False,
                evidence=request.evidence,
            )

        if request.risk > constraints.max_risk:
            return ExecutionDecision(
                decision=ExecutionDecisionType.DENY,
                reason=(
                    f"Risk {request.risk.name} exceeds the maximum "
                    f"allowed risk {constraints.max_risk.name} "
                    f"for action {request.action.value}."
                ),
                policy="default",
                required_approval=False,
                evidence=request.evidence,
            )

        permitted_capabilities = allowed_capabilities(request.action)

        unsupported_capabilities = (
            request.requested_capabilities - permitted_capabilities
        )

        if unsupported_capabilities:
            capabilities = ", ".join(
                sorted(
                    capability.value
                    for capability in unsupported_capabilities
                )
            )

            return ExecutionDecision(
                decision=ExecutionDecisionType.DENY,
                reason=(
                    f"Action {request.action.value} requests "
                    f"unsupported capabilities: {capabilities}."
                ),
                policy="default",
                required_approval=False,
                evidence=request.evidence,
            )

        if request.action in self._ALLOW_ACTIONS:
            return ExecutionDecision(
                decision=ExecutionDecisionType.ALLOW,
                reason=(
                    f"Action {request.action.value} is allowed "
                    "by the default execution policy."
                ),
                policy="default",
                required_approval=False,
                evidence=request.evidence,
            )

        if request.action in self._REVIEW_ACTIONS:
            return ExecutionDecision(
                decision=ExecutionDecisionType.REVIEW,
                reason=(
                    f"Action {request.action.value} requires "
                    "human review under the default execution policy."
                ),
                policy="default",
                required_approval=True,
                evidence=request.evidence,
            )

        return ExecutionDecision(
            decision=ExecutionDecisionType.DENY,
            reason=(
                f"Action {request.action.value} is not recognized "
                "by the default execution policy."
            ),
            policy="default",
            required_approval=False,
            evidence=request.evidence,
        )

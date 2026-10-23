from __future__ import annotations

import subprocess

import pytest

from tools.edunova.execution.decision import ExecutionDecision, ExecutionDecisionType
from tools.edunova.execution.service import AuditStatus, ExecutionResult


def allowed_decision() -> ExecutionDecision:
    return ExecutionDecision(
        ExecutionDecisionType.ALLOW,
        "allowed",
        "test",
        False,
    )


def test_executed_result_requires_a_process() -> None:
    with pytest.raises(ValueError, match="executed state"):
        ExecutionResult(
            decision=allowed_decision(),
            executed=True,
        )


def test_non_executed_result_cannot_contain_a_process() -> None:
    process = subprocess.CompletedProcess(["tool"], 0, "", "")

    with pytest.raises(ValueError, match="executed state"):
        ExecutionResult(
            decision=allowed_decision(),
            executed=False,
            process=process,
        )


def test_failed_audit_requires_a_redacted_error() -> None:
    process = subprocess.CompletedProcess(["tool"], 0, "", "")

    with pytest.raises(ValueError, match="audit error"):
        ExecutionResult(
            decision=allowed_decision(),
            executed=True,
            process=process,
            audit_status=AuditStatus.FAILED,
        )


def test_executed_result_requires_an_audit_outcome() -> None:
    process = subprocess.CompletedProcess(["tool"], 0, "", "")

    with pytest.raises(ValueError, match="audit outcome"):
        ExecutionResult(
            decision=allowed_decision(),
            executed=True,
            process=process,
        )

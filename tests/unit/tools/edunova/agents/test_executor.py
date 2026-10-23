from abc import ABC, abstractmethod

from tools.edunova.agents.provider import AgentProvider
from tools.edunova.agents.result import AgentResult
from tools.edunova.agents.role import AgentRole
from tools.edunova.agents.orchestration.executor import (
    ProviderExecutor,
)


class FakeProviderExecutor(ProviderExecutor):
    def execute_provider(
        self,
        provider: AgentProvider,
        task: str,
    ) -> AgentResult:
        return AgentResult(
            agent=provider.name,
            role=AgentRole.BUILDER,
            success=True,
            message=f"{provider.name}: {task}",
        )


def test_executor_returns_provider_result() -> None:
    executor = FakeProviderExecutor()

    result = executor.execute(
        AgentProvider("gemini"),
        "analyze EduNova",
    )

    assert result.success
    assert result.agent == "gemini"


def test_executor_passes_task_to_provider_adapter() -> None:
    executor = FakeProviderExecutor()

    result = executor.execute(
        AgentProvider("openrouter"),
        "review architecture",
    )

    assert result.message == "openrouter: review architecture"


def test_executor_rejects_empty_task_before_provider_execution() -> None:
    executor = FakeProviderExecutor()

    try:
        executor.execute(AgentProvider("gemini"), "")
    except ValueError as exc:
        assert "task" in str(exc).lower()
    else:
        raise AssertionError("Expected ValueError")


def test_executor_rejects_whitespace_task() -> None:
    executor = FakeProviderExecutor()

    try:
        executor.execute(AgentProvider("gemini"), "   ")
    except ValueError as exc:
        assert "task" in str(exc).lower()
    else:
        raise AssertionError("Expected ValueError")


def test_executor_is_read_only_at_contract_level() -> None:
    executor = FakeProviderExecutor()

    result = executor.execute(
        AgentProvider("local"),
        "inspect architecture",
    )

    assert result.success
    assert result.agent == "local"

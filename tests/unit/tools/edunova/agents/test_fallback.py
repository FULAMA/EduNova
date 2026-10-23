from tools.edunova.agents.orchestration.fallback import FallbackManager
from tools.edunova.agents.provider import AgentProvider
from tools.edunova.agents.result import AgentResult
from tools.edunova.agents.role import AgentRole


class FakeExecutor:
    def __init__(self, results: dict[str, AgentResult]) -> None:
        self._results = results
        self.calls: list[str] = []

    def execute(
        self,
        provider: AgentProvider,
        task: str,
    ) -> AgentResult:
        self.calls.append(provider.name)
        return self._results[provider.name]


def provider(name: str) -> AgentProvider:
    return AgentProvider(name)


def success(provider_name: str) -> AgentResult:
    return AgentResult(
        agent=provider_name,
        role=AgentRole.BUILDER,
        success=True,
        message=f"{provider_name} succeeded",
    )


def failure(provider_name: str) -> AgentResult:
    return AgentResult(
        agent=provider_name,
        role=AgentRole.BUILDER,
        success=False,
        message=f"{provider_name} failed",
    )


def test_fallback_returns_first_successful_result() -> None:
    executor = FakeExecutor(
        {
            "gemini": success("gemini"),
            "openrouter": success("openrouter"),
        }
    )
    manager = FallbackManager(executor)

    result = manager.execute(
        [provider("gemini"), provider("openrouter")],
        "analyze EduNova",
    )

    assert result.success
    assert result.agent == "gemini"
    assert executor.calls == ["gemini"]


def test_fallback_tries_next_provider_after_failure() -> None:
    executor = FakeExecutor(
        {
            "gemini": failure("gemini"),
            "openrouter": success("openrouter"),
        }
    )
    manager = FallbackManager(executor)

    result = manager.execute(
        [provider("gemini"), provider("openrouter")],
        "analyze EduNova",
    )

    assert result.success
    assert result.agent == "openrouter"
    assert executor.calls == ["gemini", "openrouter"]


def test_fallback_tries_all_providers_when_all_fail() -> None:
    executor = FakeExecutor(
        {
            "gemini": failure("gemini"),
            "openrouter": failure("openrouter"),
            "local": failure("local"),
        }
    )
    manager = FallbackManager(executor)

    result = manager.execute(
        [
            provider("gemini"),
            provider("openrouter"),
            provider("local"),
        ],
        "analyze EduNova",
    )

    assert not result.success
    assert result.agent == "local"
    assert executor.calls == ["gemini", "openrouter", "local"]


def test_fallback_rejects_empty_provider_list() -> None:
    executor = FakeExecutor({})
    manager = FallbackManager(executor)

    try:
        manager.execute([], "analyze EduNova")
    except ValueError as exc:
        assert "provider" in str(exc).lower()
    else:
        raise AssertionError("Expected ValueError")


def test_fallback_rejects_empty_task() -> None:
    executor = FakeExecutor({})
    manager = FallbackManager(executor)

    try:
        manager.execute([provider("gemini")], "")
    except ValueError as exc:
        assert "task" in str(exc).lower()
    else:
        raise AssertionError("Expected ValueError")

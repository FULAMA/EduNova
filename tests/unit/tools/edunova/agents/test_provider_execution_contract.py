from tools.edunova.agents.orchestration.executor import ProviderExecutor
from tools.edunova.agents.orchestration.adapter import ProviderAdapter
from tools.edunova.agents.provider import AgentProvider
from tools.edunova.agents.result import AgentResult
from tools.edunova.agents.role import AgentRole


class FakeAdapter(ProviderAdapter):
    def generate(
        self,
        provider: AgentProvider,
        task: str,
    ) -> AgentResult:
        return AgentResult(
            agent=provider.name,
            role=AgentRole.ARCHITECT,
            success=True,
            message=f"Executed: {task}",
        )


class AdapterExecutor(ProviderExecutor):
    def __init__(self, adapter: ProviderAdapter) -> None:
        self._adapter = adapter

    def execute_provider(
        self,
        provider: AgentProvider,
        task: str,
    ) -> AgentResult:
        return self._adapter.generate(provider, task)


def test_executor_delegates_to_adapter() -> None:
    provider = AgentProvider(name="fake")
    adapter = FakeAdapter()
    executor = AdapterExecutor(adapter)

    result = executor.execute(
        provider,
        "Analyse EduNova",
    )

    assert result.success is True
    assert result.agent == "fake"
    assert result.role == AgentRole.ARCHITECT
    assert result.message == "Executed: Analyse EduNova"


def test_executor_rejects_empty_task() -> None:
    provider = AgentProvider(name="fake")
    executor = AdapterExecutor(FakeAdapter())

    try:
        executor.execute(provider, "")
    except ValueError as exc:
        assert "task" in str(exc).lower()
    else:
        raise AssertionError("Expected ValueError")


def test_executor_rejects_invalid_provider_name() -> None:
    provider = AgentProvider.__new__(AgentProvider)
    object.__setattr__(provider, "name", "")

    executor = AdapterExecutor(FakeAdapter())

    try:
        executor.execute(provider, "Analyse")
    except ValueError as exc:
        assert "provider" in str(exc).lower()
    else:
        raise AssertionError("Expected ValueError")

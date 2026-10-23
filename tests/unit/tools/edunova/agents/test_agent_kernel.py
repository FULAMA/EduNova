from tools.edunova.agents.agent import Agent
from tools.edunova.agents.registry import AgentRegistry
from tools.edunova.agents.result import AgentResult
from tools.edunova.agents.role import AgentRole


class FakeAgent(Agent):
    name = "fake-inspector"
    role = AgentRole.INSPECTOR

    def run(self, task: str) -> AgentResult:
        return AgentResult(
            agent=self.name,
            role=self.role,
            success=True,
            message=f"Inspected: {task}",
        )


def test_agent_exposes_name_and_role() -> None:
    agent = FakeAgent()

    assert agent.name == "fake-inspector"
    assert agent.role == AgentRole.INSPECTOR


def test_agent_returns_result() -> None:
    agent = FakeAgent()

    result = agent.run("inspect academic records")

    assert result.success is True
    assert result.agent == "fake-inspector"
    assert result.role == AgentRole.INSPECTOR
    assert result.message == "Inspected: inspect academic records"


def test_registry_registers_and_resolves_agent() -> None:
    registry = AgentRegistry()
    agent = FakeAgent()

    registry.register(agent)

    assert registry.get("fake-inspector") is agent
    assert registry.has("fake-inspector") is True


def test_registry_rejects_duplicate_agent() -> None:
    registry = AgentRegistry()
    registry.register(FakeAgent())

    try:
        registry.register(FakeAgent())
    except ValueError as error:
        assert "already registered" in str(error)
    else:
        raise AssertionError("Expected duplicate registration to fail")


def test_registry_returns_agent_names() -> None:
    registry = AgentRegistry()
    registry.register(FakeAgent())

    assert registry.names() == ("fake-inspector",)

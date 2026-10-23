from tools.edunova.agents.agent import Agent


class AgentRegistry:
    def __init__(self) -> None:
        self._agents: dict[str, Agent] = {}

    def register(self, agent: Agent) -> None:
        if agent.name in self._agents:
            raise ValueError(
                f"Agent already registered: {agent.name}"
            )

        self._agents[agent.name] = agent

    def get(self, name: str) -> Agent:
        if name not in self._agents:
            raise KeyError(f"Unknown agent: {name}")

        return self._agents[name]

    def has(self, name: str) -> bool:
        return name in self._agents

    def names(self) -> tuple[str, ...]:
        return tuple(self._agents)

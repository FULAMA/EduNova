from collections.abc import Sequence

from tools.edunova.agents.agent import Agent
from tools.edunova.agents.orchestration.service import (
    AgentOrchestrationService,
)
from tools.edunova.core.command import Command
from tools.edunova.core.result import CommandResult, Status
from tools.edunova.security import redact_text


class AgentCommand(Command):
    name = "agent"

    def __init__(
        self,
        agent: Agent,
        task: str = "",
    ) -> None:
        self._agent = agent
        self._task = task

    def bind(self, args: Sequence[str]) -> "AgentCommand":
        if len(args) != 1 or not args[0].strip():
            raise ValueError("Agent task is required.")

        return AgentCommand(
            agent=self._agent,
            task=args[0],
        )

    def execute(self) -> CommandResult:
        if not self._task.strip():
            return CommandResult(
                command=self.name,
                status=Status.FAIL,
                message="Agent task cannot be empty.",
                exit_code=1,
            )

        try:
            result = self._agent.run(self._task)
        except Exception as error:
            return CommandResult(
                command=self.name,
                status=Status.FAIL,
                message=f"Agent execution failed ({type(error).__name__}).",
            )

        if not result.success:
            return CommandResult(
                command=self.name,
                status=Status.FAIL,
                message=redact_text(result.message),
                exit_code=1,
            )

        return CommandResult(
            command=self.name,
            status=Status.SAFE,
            message=redact_text(result.message),
            exit_code=0,
        )


class OrchestratedAgentCommand(Command):
    name = "agent-orchestrated"

    def __init__(
        self,
        service: AgentOrchestrationService,
        task: str = "",
    ) -> None:
        self._service = service
        self._task = task

    def bind(self, args: Sequence[str]) -> "OrchestratedAgentCommand":
        if len(args) != 1 or not args[0].strip():
            raise ValueError("Agent task is required.")

        return OrchestratedAgentCommand(
            service=self._service,
            task=args[0],
        )

    def execute(self) -> CommandResult:
        if not self._task.strip():
            return CommandResult(
                command=self.name,
                status=Status.FAIL,
                message="Agent task cannot be empty.",
                exit_code=1,
            )

        try:
            result = self._service.run(self._task)
        except Exception as error:
            return CommandResult(
                command=self.name,
                status=Status.FAIL,
                message=(
                    "Agent orchestration failed "
                    f"({type(error).__name__})."
                ),
            )

        if not result.success:
            return CommandResult(
                command=self.name,
                status=Status.FAIL,
                message=redact_text(result.message),
                exit_code=1,
            )

        return CommandResult(
            command=self.name,
            status=Status.SAFE,
            message=redact_text(result.message),
            exit_code=0,
        )
